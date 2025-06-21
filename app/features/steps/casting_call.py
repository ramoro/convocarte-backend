from behave import given, when, then
import requests
import models
from environment import SessionLocal
from config import settings
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
import json
from datetime import datetime, timedelta

def create_and_log_in_account(context, session):
    # Registro del usuario de prueba
    url = settings.backend_url + "/users/"
    user_data = {field["field"]: field["value"] for field in context.table}
    user_data["password_confirmation"] = user_data["password"]

    # Verifica si el usuario ya existe, para no estar creando varios y usar uno solo para
    # varios escenarios
    existing_user = session.query(models.User).filter(models.User.email == user_data["email"]).first()
    if not existing_user:
        response = requests.post(url, json=user_data)
        response_data = response.json()
        user_id = response_data.get('id')

        user_query = session.query(models.User).filter(models.User.id == user_id)
        
        # Simulacion de cuenta verificada
        user_query.update({"is_verified": True}, synchronize_session=False)
        session.commit()

    #Si fue eliminado lo seteamos como existente nuevamente
    if existing_user and existing_user.deleted_at:
        existing_user.deleted_at = None
        session.commit()

    # Logeo con el usuario
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    url = settings.backend_url + "/login"
    response = requests.post(url, data=login_data)
    return response

@given('Im logged in on the platform with my account')
def step_given_im_logged_in(context):
    session = SessionLocal()
    try:
        response = create_and_log_in_account(context, session)
        context.token = response.json().get('token')
        context.user_id = response.json().get('id')
    finally:
        session = session.close()

@when('I create a casting call for the project "{project_name}" associating the role "{role_name}" to the form template "{template_title}"')
def step_when_create_casting_call(context, project_name, role_name, template_title):
    url = settings.backend_url + "/casting-calls/"

    session = SessionLocal()
    try:
        form_template = session.query(models.FormTemplate).filter(models.FormTemplate.form_template_title == template_title).first()
        project = session.query(models.Project).filter(models.Project.name == project_name).first()
        role = session.query(models.Role).filter(and_(
                models.Role.project_id == project.id,
                models.Role.name == role_name
        )).first()
        
        casting_call_data_table = {field["field"]: field["value"] for field in context.table}
        casting_call_data = {
        "title": casting_call_data_table["title"],
        "project_id": project.id,
        "remuneration_type":  casting_call_data_table["remuneration_type"],
        "casting_roles": json.dumps(  # Enviar los roles como un array de objetos JSON
                {
                    "role_id": role.id,
                    "form_template_id": form_template.id,
                    "has_limited_spots": False 
                }
            )
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.post(url, data=casting_call_data, headers=headers)
        context.response = response
        context.responsejson = response.json()
        context.casting_call_id = context.responsejson["casting_call_id"]
        context.role_id = role.id
    finally:
        session.close()

@then('a casting call with the title "{casting_call_title}" should be created successfully as draft')
def step_then_casting_call_created(context, casting_call_title):
    session = SessionLocal()
    try:
        casting_call = context.database.query(models.CastingCall).filter(models.CastingCall.title == casting_call_title).first()
        assert casting_call is not None, f"Casting call with title {casting_call_title} was not created"
        assert casting_call.state == "Borrador", "Casting call was not created as draft"
    finally:
        session.close()

@then('a form should be created successfully for the casting role with the same title and same fields that the form template "{form_title}"')
def step_then_form_created_for_casting_role(context, form_title):
    session = SessionLocal()
    try:
        form = context.database.query(models.Form).filter(and_(
                models.Form.form_title == form_title,
                models.Form.casting_call_id == context.casting_call_id
        )).options(joinedload(models.Form.form_fields)).first()
        assert form is not None, f"Form with title {form_title} was not created"
        assert len(form.form_fields) > 0, f"Form with title {form_title} has no form fields created"
    finally:
        session.close()

@when('I create a casting call for the project "{project_name}" without associating any roles to it')
def step_when_create_casting_without_roles(context, project_name):
    url = settings.backend_url + "/casting-calls/"

    session = SessionLocal()
    try:
        project = session.query(models.Project).filter(models.Project.name == project_name).first()

        casting_call_data_table = {field["field"]: field["value"] for field in context.table}
        casting_call_data = {
            "title": casting_call_data_table["title"],
            "project_id": project.id,
            "remuneration_type": casting_call_data_table["remuneration_type"]
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.post(url, data=casting_call_data, headers=headers)
        context.response = response
    finally:
        session.close()

@when('I create a casting call associating the role "{role_name}" without assigning a form template to it')
def step_when_create_casting_with_role_and_no_form_template(context, role_name):
    url = settings.backend_url + "/casting-calls/"

    session = SessionLocal()
    try:
        role = session.query(models.Role).filter(models.Role.name == role_name).first()
        project = session.query(models.Project).filter(models.Project.id == role.project_id).first()

        casting_call_data_table = {field["field"]: field["value"] for field in context.table}
        casting_call_data = {
            "title": casting_call_data_table["title"],
            "project_id": project.id,
            "remuneration_type": casting_call_data_table["remuneration_type"],
            "casting_roles": json.dumps(  # Rol sin form template asignado
                {
                    "role_id": role.id,
                    "has_limited_spots": False
                }
            )
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.post(url, data=casting_call_data, headers=headers)
        context.response = response
    finally:
        session.close()

@then('no casting call should be created in the system')
def step_then_no_casting_created(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that the casting call must have at least one role associated')
def step_then_user_notified_casting_must_have_at_least_one_role(context):
    assert ("Field required" in context.response.text and "casting_roles" in context.response.text), "Expected error message not found"

@then('the user should be notified that each role must have a form template assigned')
def step_then_user_notified_roles_must_have_form_template_assigned(context):
    assert "Form template is required for each role." in context.response.text, "Expected error message not found"

@when('I publish the casting call "{casting_call_title}" with an expiration date greater than the current date')
def step_when_publish_casting(context, casting_call_title):
    url = settings.backend_url + "/casting-calls/publish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        publication_data = {
            "title": casting_call.title,
            "state": casting_call.state,
            "expiration_date": (datetime.now().date() + timedelta(days=10)).strftime('%Y-%m-%d')
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }

        response = requests.patch(url.format(casting_id=casting_call.id), json=publication_data, headers=headers)
        context.response = response
    finally:
        session.close()

@then('the casting call should be successfully published')
def step_then_casting_published(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state == "Publicado", f"Casting call is not published. Current state: {casting_call.state}"
    finally:
        session.close()

@given('I create a casting call for the project "{project_name}" associating the role "{role_name}" to the form template "{template_title}"')
def step_given_casting_call_created(context, project_name, role_name, template_title):
    url = settings.backend_url + "/casting-calls/"

    session = SessionLocal()
    try:
        form_template = session.query(models.FormTemplate).filter(models.FormTemplate.form_template_title == template_title).first()
        project = session.query(models.Project).filter(models.Project.name == project_name).first()
        role = session.query(models.Role).filter(and_(
                models.Role.project_id == project.id,
                models.Role.name == role_name
        )).first()
        
        casting_call_data_table = {field["field"]: field["value"] for field in context.table}
        casting_call_data = {
        "title": casting_call_data_table["title"],
        "project_id": project.id,
        "remuneration_type":  casting_call_data_table["remuneration_type"],
        "casting_roles": json.dumps(  # Enviar los roles como un array de objetos JSON
                {
                    "role_id": role.id,
                    "form_template_id": form_template.id,
                    "has_limited_spots": False 
                }
            )
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.post(url, data=casting_call_data, headers=headers)
        context.response = response
        context.responsejson = response.json()
        context.casting_call_id = context.responsejson["casting_call_id"]
        context.role_id = role.id
    finally:
        session.close()

@given('I publish the casting call with an expiration date greater than the current date')
def step_given_publish_casting_expiration_date_grater_current_date(context):
    url = settings.backend_url + "/casting-calls/publish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        publication_data = {
            "title": casting_call.title,
            "state": casting_call.state,
            "expiration_date": (datetime.now().date() + timedelta(days=10)).strftime('%Y-%m-%d')
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }

        response = requests.patch(url.format(casting_id=casting_call.id), json=publication_data, headers=headers)
        context.response = response
    finally:
        session.close()

@given('I pause the casting call publication')
def step_given_casting_publication_paused(context):
    url = settings.backend_url + "/casting-calls/pause/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        pause_data = {
            "title": casting_call.title,
            "state": casting_call.state
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        requests.patch(url.format(casting_id=casting_call.id), json=pause_data, headers=headers)
    finally:
        session.close()

@when('I publish the casting call "{casting_call_title}" with an expiration date less than the current date')
def step_when_publish_casting_expiration_date_less_than_current_date(context, casting_call_title):
    url = settings.backend_url + "/casting-calls/publish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        publication_data = {
            "title": casting_call.title,
            "state": casting_call.state,
            "expiration_date": (datetime.now().date() - timedelta(days=10)).strftime('%Y-%m-%d')
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }

        response = requests.patch(url.format(casting_id=casting_call.id), json=publication_data, headers=headers)
        context.response = response
    finally:
        session.close()

@then('the casting call should not be published')
def step_then_casting_not_published(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state != "Publicado", "Casting call was incorrectly published."
    finally:
        session.close()

@then('the user should be notified that the expiration date must be greater than the current date')
def step_user_notified_expiration_date_must_be_greater_than_current_date(context):
    assert "Expiration date must be after the current date" in context.response.text, "Expected error message not found."

@given('I finish the casting call')
def step_given_casting_call_ended(context):
    url = settings.backend_url + "/casting-calls/finish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        publication_data = {
            "title": casting_call.title,
            "state": casting_call.state
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }

        response = requests.patch(url.format(casting_id=casting_call.id), json=publication_data, headers=headers)
        context.response = response
    finally:
        session.close()

@then('the user should be notified that the casting cannot be published because it has already ended')
def step_then_user_notified_casting_cannot_published_its_ended(context):
    assert "The casting cannot be published because it has already ended" in context.response.text, "Expected error message not found."

@when('I pause the casting call')
def step_pause_casting(context):
    url = settings.backend_url + "/casting-calls/pause/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        pause_data = {
            "title": casting_call.title,
            "state": casting_call.state
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.patch(url.format(casting_id=casting_call.id), json=pause_data, headers=headers)
        context.response = response
    finally:
        session.close()

@then('the casting call should be successfully paused')
def step_then_casting_paused(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state == "Pausado", f"Casting call is not paused. Current state: {casting_call.state}"
    finally:
        session.close()

@then('the casting call should not be paused')
def step_then_casting_not_paused(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state != "Pausado", "Casting call was incorrectly paused."
    finally:
        session.close()

@then("the user should be notified that the casting cannot be paused because it hasn't been published yet")
def step_then_user_notified_casting_cannot_be_paused_it_hasnt_been_published(context):
    assert "casting cannot be paused because it hasn't been published yet" in context.response.text, "Expected error message not found."

@then("the user should be notified that the casting cannot be paused because it has already ended")
def step_then_user_notified_casting_cannot_be_paused_its_ended(context):
    assert "casting cannot be paused because it has already ended" in context.response.text, "Expected error message not found."

@when('I finish the casting call')
def step_when_casing_ended(context):
    url = settings.backend_url + "/casting-calls/finish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        pause_data = {
            "title": casting_call.title,
            "state": casting_call.state
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.patch(url.format(casting_id=casting_call.id), json=pause_data, headers=headers)
        context.response = response
    finally:
        session.close()

@then('the casting call should be successfully finished')
def step_then_casting_ended(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state == "Finalizado", f"Casting call is not paused. Current state: {casting_call.state}"
    finally:
        session.close()

@then('the casting call should not be finished')
def step_casting_not_ended(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state != "Finalizado", f"Casting call was incorrectly finished."
    finally:
        session.close()

@then("the user should be notified that the casting cannot be finished because it hasn't been published yet")
def step_then_user_notified_casting_cannot_be_ended_it_hasnt_been_published(context):
    assert "casting cannot be finished because it hasn't been published yet" in context.response.text, "Expected error message not found."

@given('a user that has a published {casting_category} casting with title "{other_casting_title}" and open role "{role_name}"')
def step_given_user_has_casting_published(context, other_casting_title, role_name, casting_category):
    session = SessionLocal()
    try:
        #Creamos otro usuario de prueba y lo logeamos para crear lo necesario para publicar un casting
        response = create_and_log_in_account(context, session)
        token = response.json().get('token')
        context.casting_director_id = response.json().get('id')

        #Le creamos un form template
        url = settings.backend_url + "/form-templates/"
        form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
        form_template_data = {"form_template_title": "Template", "form_template_fields": [form_template_field_data]}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        form_template_response = requests.post(url, json=form_template_data, headers=headers)
        form_template_id = form_template_response.json().get('id')
        #Le creamos un proyecto y un casting asociado a ese proyecto con el titulo other_casting_title
        url = settings.backend_url + "/projects/"
        role_data = {"name": role_name}
        project_data = {"name": "Matrix y algo mas", "region": "CABA", "category": casting_category, "roles": [role_data]}
        headers = {
            "Authorization": f"Bearer {token}"
        }
        project_response = requests.post(url, json=project_data, headers=headers)
        project_id = project_response.json().get('id')

        url = settings.backend_url + "/casting-calls/"
        role = session.query(models.Role).filter(and_(
                models.Role.project_id == project_id,
                models.Role.name == role_name
        )).first()
        casting_call_data = {
        "title": other_casting_title,
        "project_id": project_id,
        "remuneration_type":  "Remunerado",
        "casting_roles": json.dumps(  # Enviar los roles como un array de objetos JSON
                {
                    "role_id": role.id,
                    "form_template_id": form_template_id,
                    "has_limited_spots": False 
                }
            )
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }
        casting_response = requests.post(url, data=casting_call_data, headers=headers)
        casting_id = casting_response.json().get('casting_call_id')
        casting_title = casting_response.json().get('casting_call_title')

        #Publicamos el casting
        url = settings.backend_url + f"/casting-calls/publish/{casting_id}"
        publication_data = {
            "title": casting_title,
            "state": "Borrador",
            "expiration_date": (datetime.now().date() + timedelta(days=10)).strftime('%Y-%m-%d')
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.patch(url, json=publication_data, headers=headers)
        context.casting_call_id = casting_id
        context.role_id = role.id

    finally:
        session.close()

@then('the user should be notified that there is already a published casting with the title "{casting_title}"')
def step_then_user_notified_casting_arleady_published_with_that_name(context, casting_title):
    assert f"there is already a published casting with the title {casting_title}" in context.response.text, "Expected error message not found."

@when('I edit the casting call "{current_casting_title}" with the title "{new_casting_title}" and its role "{role_name}" with minimum age requirement "{min_age_required}"')
def step_when_update_casting(context, current_casting_title, new_casting_title, role_name, min_age_required):
    url = settings.backend_url + "/casting-calls/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        project = session.query(models.Project).filter(models.Project.id == casting_call.project_id).first()
        role = session.query(models.Role).filter(and_(
                models.Role.project_id == project.id,
                models.Role.name == role_name
        )).first()
        open_role = next((open_role for open_role in casting_call.open_roles if open_role.role_id == role.id), None)
        casting_call_data = {
        "casting_state": casting_call.state,
        "title": new_casting_title,
        "project_id": project.id,
        "remuneration_type":  casting_call.remuneration_type,
        "casting_roles": json.dumps(  # Enviar los roles como un array de objetos JSON
                {
                    "id": open_role.id,
                    "role_id": role.id,
                    "has_limited_spots": False,
                    "min_age_required":  min_age_required
                }
            )
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.patch(url.format(casting_id=casting_call.id), data=casting_call_data, headers=headers)
        context.response = response
        context.updated_role_id = role.id
    finally:
        session.close()

@then('the casting call should be successfully updated with the title "{new_casting_title}" and its role "{role_name}" should have a minimum age requirement of "{min_age_required}"')
def step_then_casting_updated(context, new_casting_title, role_name, min_age_required):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        #filtrar el rol con el id igual al updated_role_id del contexto
        updated_open_role = casting_call.open_roles[0]
        
        assert casting_call.title == new_casting_title, "Casting call was not updated."
        assert updated_open_role.min_age_required == int(min_age_required), "Casting call role was not updated."
    finally:
        session.close()

@then('the casting call should not be successfully updated with the title "{new_casting_title_failed}" and its role "{role_name}" with minimum age requirement "{min_age_required}"')
def step_then_casting_not_updated(context, new_casting_title_failed, role_name, min_age_required):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        
        updated_open_role = casting_call.open_roles[0]        
        assert casting_call.title != new_casting_title_failed, "Casting call was incorrectly updated."
        assert updated_open_role.min_age_required != int(min_age_required), "Casting call role was incorrectly updated."
    finally:
        session.close()

@then('the user should be notified that the casting must be paused to be updated')
def step_then_user_notified_casting_must_be_paused_to_be_updated(context):
    assert "casting must be paused to be updated" in context.response.text, "Expected error message not found."

@then('the user should be notified that the casting has finished and cant be edited')
def step_then_user_notified_casting_has_finished(context):
    assert "casting has finished and cant be edited" in context.response.text, "Expected error message not found."

@when('I try to delete the casting call')
def step_when_delete_casting(context):
    url = settings.backend_url + "/casting-calls/{casting_id}"
    session = SessionLocal()
    try:
        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.delete(url.format(casting_id=context.casting_call_id), headers=headers)
        context.response = response
    finally:
        session.close()

@then('the casting call is deleted from the system')
def step_then_casting_call_deleted(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
       # open_roles = context.database.query(models.OpenRole).filter(models.OpenRole.casting_call_id == context.casting_call_id).all()

        assert casting_call.deleted_at is not None, "Casting call was not deleted."

    finally:
        session.close()

@then('the casting call forms should desappear from the system')
def step_then_casting_deleted(context):
    session = SessionLocal()
    try:
        forms = context.database.query(models.Form).filter(models.Form.casting_call_id == context.casting_call_id).all()
        for form in forms:
            assert form.deleted_at is not None, f"Form {form.id} was not properly deleted (deleted_at is None)"
    finally:
        session.close()

@then('the casting call should not be eliminated from the system')
def step_then_casting_not_deleted(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        open_roles = context.database.query(models.OpenRole).filter(models.OpenRole.casting_call_id == context.casting_call_id).all()
        
        assert casting_call.deleted_at is None, "Casting call was deleted."
        assert len(open_roles) > 0, "Casting call open roles were deleted"

    finally:
        session.close()
@then('the user should be notified that the casting call cant be deleted cause its published')
def step_then_user_notified_casting_cant_be_deleted_its_published(context):
    assert "casting call cant be deleted cause its published" in context.response.text, "Expected error message not found."

@then('the user should be notified that the casting call cant be deleted cause its paused')
def step_then_user_notified_casting_cant_be_deleted_its_paused(context):
    assert "casting call cant be deleted cause its paused" in context.response.text, "Expected error message not found."

@when('I try to search for {casting_category} castings')
def step_when_search_for_casting(context, casting_category):
    url = settings.backend_url + "/casting-calls/published"
    search_data = {"date_order": "Ascendente", "categories": [casting_category]}
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    response = requests.post(url, json=search_data ,headers=headers)
    context.response = response.json()

@then('the system displays the casting as a result')
def step_then_system_displays_casting(context):
    found = any(casting['id'] == context.casting_call_id for casting in context.response)
    assert found, (
        f"Casting with ID {context.casting_call_id} not found in results. "
        f"Available castings: {[c['id'] for c in context.response]}\n"
        f"Full response: {context.response}"
    )

@then('the system does not show any castings as results')
def step_then_system_does_not_show_results(context):
    assert len(context.response) == 0, "A casting was found when it shouldn't have been"
