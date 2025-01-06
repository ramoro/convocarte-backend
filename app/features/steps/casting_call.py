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

    # Logeo con el usuario
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    url = settings.backend_url + "/login"
    response = requests.post(url, data=login_data)
    return response

@given('Im logged in on the platform with my account')
def step_impl(context):
    session = SessionLocal()
    try:
        response = create_and_log_in_account(context, session)
        context.token = response.json().get('token')
        context.user_id = response.json().get('id')
    finally:
        session = session.close()

@given('I have a form template with title "{template_title}"')
def step_impl(context, template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": template_title, "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    requests.post(url, json=form_template_data, headers=headers)

@given('I have a project with name "{project_name}" and an associated role called "{role_name}"')
def step_impl(context, project_name, role_name):
    url = settings.backend_url + "/projects/"
    role_data = {"name": role_name}
    project_data = {"name": project_name, "region": "CABA", "category": "Teatro", "roles": [role_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    requests.post(url, json=project_data, headers=headers)

@when('I create a casting call for the project "{project_name}" associating the role "{role_name}" to the form template "{template_title}"')
def step_impl(context, project_name, role_name, template_title):
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
def step_impl(context, casting_call_title):
    session = SessionLocal()
    try:
        casting_call = context.database.query(models.CastingCall).filter(models.CastingCall.title == casting_call_title).first()
        assert casting_call is not None, f"Casting call with title {casting_call_title} was not created"
        assert casting_call.state == "Borrador", f"Casting call was not created as draft"
    finally:
        session.close()

@then('a form should be created successfully for the casting role with the same title and same fields that the form template "{form_title}"')
def step_impl(context, form_title):
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
def step_impl(context, project_name):
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
def step_impl(context, role_name):
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
def step_impl(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that the casting call must have at least one role associated')
def step_impl(context):
    assert ("Field required" in context.response.text and "casting_roles" in context.response.text), "Expected error message not found"

@then('the user should be notified that each role must have a form template assigned')
def step_impl(context):
    assert "Form template is required for each role." in context.response.text, "Expected error message not found"

@when('I publish the casting call "{casting_call_title}" with an expiration date greater than the current date')
def step_impl(context, casting_call_title):
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
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state == "Publicado", f"Casting call is not published. Current state: {casting_call.state}"
    finally:
        session.close()

@given('I create a casting call for the project "{project_name}" associating the role "{role_name}" to the form template "{template_title}"')
def step_impl(context, project_name, role_name, template_title):
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
def step_impl(context):
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
def step_impl(context):
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
def step_impl(context, casting_call_title):
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
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state != "Publicado", f"Casting call was incorrectly published."
    finally:
        session.close()

@then('the user should be notified that the expiration date must be greater than the current date')
def step_impl(context):
    assert "Expiration date must be after the current date" in context.response.text, "Expected error message not found."

@given('I finish the casting call')
def step_impl(context):
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
def step_impl(context):
    assert "The casting cannot be published because it has already ended" in context.response.text, "Expected error message not found."

@when('I pause the casting call')
def step_impl(context):
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
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state == "Pausado", f"Casting call is not paused. Current state: {casting_call.state}"
    finally:
        session.close()

@then('the casting call should not be paused')
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state != "Pausado", f"Casting call was incorrectly paused."
    finally:
        session.close()

@then("the user should be notified that the casting cannot be paused because it hasn't been published yet")
def step_impl(context):
    assert "casting cannot be paused because it hasn't been published yet" in context.response.text, "Expected error message not found."

@then("the user should be notified that the casting cannot be paused because it has already ended")
def step_impl(context):
    assert "casting cannot be paused because it has already ended" in context.response.text, "Expected error message not found."

@when('I finish the casting call')
def step_impl(context):
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
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state == "Finalizado", f"Casting call is not paused. Current state: {casting_call.state}"
    finally:
        session.close()

@then('the casting call should not be finished')
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        assert casting_call.state != "Finalizado", f"Casting call was incorrectly finished."
    finally:
        session.close()

@then("the user should be notified that the casting cannot be finished because it hasn't been published yet")
def step_impl(context):
    assert "casting cannot be finished because it hasn't been published yet" in context.response.text, "Expected error message not found."

@given('a user that has a published casting with title "{other_casting_title}"')
def step_impl(context, other_casting_title):
    session = SessionLocal()
    try:
        #Creamos otro usuario de prueba y lo logeamos para crear lo necesario para publicar un casting
        response = create_and_log_in_account(context, session)
        token = response.json().get('token')

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
        role_name = "Rol protagonico"
        url = settings.backend_url + "/projects/"
        role_data = {"name": role_name}
        project_data = {"name": "Matrix y algo mas", "region": "CABA", "category": "Cine-largometraje", "roles": [role_data]}
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

    finally:
        session.close()

@then('the user should be notified that there is already a published casting with the title "{casting_title}"')
def step_impl(context, casting_title):
    assert f"there is already a published casting with the title {casting_title}" in context.response.text, "Expected error message not found."

@when('I edit the casting call "{current_casting_title}" with the title "{new_casting_title}" and its role "{role_name}" with minimum age requirement "{min_age_required}"')
def step_impl(context, current_casting_title, new_casting_title, role_name, min_age_required):
    url = settings.backend_url + "/casting-calls/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        project = session.query(models.Project).filter(models.Project.id == casting_call.project_id).first()
        role = session.query(models.Role).filter(and_(
                models.Role.project_id == project.id,
                models.Role.name == role_name
        )).first()
        exposed_role = next((exposed_role for exposed_role in casting_call.exposed_roles if exposed_role.role_id == role.id), None)
        casting_call_data = {
        "casting_state": casting_call.state,
        "title": new_casting_title,
        "project_id": project.id,
        "remuneration_type":  casting_call.remuneration_type,
        "casting_roles": json.dumps(  # Enviar los roles como un array de objetos JSON
                {
                    "id": exposed_role.id,
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
def step_impl(context, new_casting_title, role_name, min_age_required):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        #filtrar el rol con el id igual al updated_role_id del contexto
        print(context.updated_role_id)
        updated_exposed_role = casting_call.exposed_roles[0]
        
        assert casting_call.title == new_casting_title, f"Casting call was not updated."
        assert updated_exposed_role.min_age_required == int(min_age_required), f"Casting call role was not updated."
    finally:
        session.close()

@then('the casting call should not be successfully updated with the title "{new_casting_title_failed}" and its role "{role_name}" with minimum age requirement "{min_age_required}"')
def step_impl(context, new_casting_title_failed, role_name, min_age_required):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        
        updated_exposed_role = casting_call.exposed_roles[0]        
        assert casting_call.title != new_casting_title_failed, f"Casting call was incorrectly updated."
        assert updated_exposed_role.min_age_required != int(min_age_required), f"Casting call role was incorrectly updated."
    finally:
        session.close()

@then('the user should be notified that the casting must be paused to be updated')
def step_impl(context):
    print(context.response.text)
    assert f"casting must be paused to be updated" in context.response.text, "Expected error message not found."

@then('the user should be notified that the casting has finished and cant be edited')
def step_impl(context):
    assert f"casting has finished and cant be edited" in context.response.text, "Expected error message not found."


