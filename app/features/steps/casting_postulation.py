from behave import given, when, then
import requests
from config import settings
import models
from environment import SessionLocal
from sqlalchemy import and_
import json
from datetime import datetime, timedelta
from repository.open_role import OpenRoleRepository
from casting_call import create_and_log_in_account

@given('there is a project with name "{project_name}" with an associated role called "{role_name}"')
def step_given_existent_project_with_role(context, project_name, role_name):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": "Matrix 4 Form Template", "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    response = requests.post(url, json=form_template_data, headers=headers)
    context.form_template_id = response.json()["id"]

    url = settings.backend_url + "/projects/"
    role_data = {"name": role_name}
    project_data = {"name": project_name, "region": "CABA", "category": "Teatro", "roles": [role_data]}

    response = requests.post(url, json=project_data, headers=headers)
    context.project_id = response.json()["id"]

@given('there is a casting call published for that project opening the role "{role_name}" with {spots_limit} spots')
def step_given_casting_published_with_limited_spots(context, role_name, spots_limit):
    url = settings.backend_url + "/casting-calls/"

    session = SessionLocal()
    try:
        role = session.query(models.Role).filter(and_(
                models.Role.project_id == context.project_id,
                models.Role.name == role_name
        )).first()
        context.role_id = role.id
        
        casting_call_data_table = {field["field"]: field["value"] for field in context.table}
        casting_call_data = {
        "title": casting_call_data_table["title"],
        "project_id": context.project_id,
        "remuneration_type":  casting_call_data_table["remuneration_type"],
        "casting_roles": json.dumps(  # Enviar los roles como un array de objetos JSON
                {
                    "role_id": role.id,
                    "form_template_id": context.form_template_id,
                    "has_limited_spots":  False if spots_limit == "unlimited" else True,
                    "spots_amount": None if spots_limit == "unlimited" else spots_limit
                }
            )
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.post(url, data=casting_call_data, headers=headers)
        context.casting_call_id = response.json()["casting_call_id"]

        url = settings.backend_url + "/casting-calls/publish/{casting_id}"

        casting_call = session.query(models.CastingCall).filter(models.CastingCall.id == context.casting_call_id).first()
        publication_data = {
            "title": casting_call.title,
            "state": casting_call.state,
            "expiration_date": (datetime.now().date() + timedelta(days=10)).strftime('%Y-%m-%d')
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }

        response = requests.patch(url.format(casting_id=context.casting_call_id), json=publication_data, headers=headers)
        context.response = response
    finally:
        session.close()

@given('the casting is finished')
def step_given_casting_ended(context):
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

@given('the casting is paused')
def step_given_casting_paused(context):
    url = settings.backend_url + "/casting-calls/pause/{casting_id}"
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

@given('the open role "{role_name}" has all its {spots_amount} spots full')
def step_given_open_role_has_spots_full(context, role_name, spots_amount):
    session = SessionLocal() 
    open_role = session.query(models.OpenRole).filter(and_(
    models.OpenRole.casting_call_id == context.casting_call_id,
    models.OpenRole.role_id == context.role_id
    )).first()
    open_role_respository = OpenRoleRepository(session)
    open_role_respository.update_occupied_spots(open_role.id, spots_amount)

def make_postulation(context):
    url = settings.backend_url + "/casting-postulations/"

    session = SessionLocal()
    try:

        open_role = session.query(models.OpenRole).filter(and_(
        models.OpenRole.casting_call_id == context.casting_call_id,
        models.OpenRole.role_id == context.role_id
        )).first()
        context.open_role_id = open_role.id
        postulation_data = {
            "form_id": open_role.form_id,
            "postulation_data": json.dumps({"Instagram": "https://www.instagram.com/username"})
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }

        response = requests.post(url, data=postulation_data, headers=headers)
        context.response = response
        context.postulation_id = context.response.json().get("id", -1)    
    finally:
        session.close()  

@given('I postulate for the open role "{role_name}" within the published casting')
def step_given_postulation_for_open_role(context, role_name):
    make_postulation(context)

@when('I postulate for the open role "{role_name}" within the published casting')
def step_when_postulate_for_open_role(context, role_name):
    make_postulation(context)


@then('a postulation for that casting call and that open role should be succesfully created in the system')
def step_then_postulation_created(context):
    session = SessionLocal()
    try:
        postulation = context.database.query(models.CastingPostulation).filter(and_(
                 models.CastingPostulation.casting_call_id == context.casting_call_id,
                 models.Project.owner_id == context.user_id
             )).first()
        assert postulation is not None, "Postulation for casting call was not created"
        assert context.response.status_code == 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"
    finally:
        session.close()

@then('the postulation should not be created for the user')
def step_then_postulation_not_created(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that the casting has already finished')
def step_then_user_notified_casting_finished(context):
    assert "casting call for this role has already finished" in context.response.text, "Expected error message not found"

@then('the user should be notified that the casting is paused')
def step_then_user_notified_casting_paused(context):
    assert "casting call for this role is paused" in context.response.text, "Expected error message not found"

@then('the user should be notified that the open role for this casting call is full')
def step_then_user_notified_open_role_is_full(context):
    assert "open role for this casting call is full" in context.response.text, "Expected error message not found"

@then('the user should be notified that they has already postulated for that role')
def step_then_user_notified_they_has_already_postulated_for_role(context):
    assert "user has already postulated for this role" in context.response.text, "Expected error message not found"

@when('I try to search for my postulations')
def step_when_search_my_postulations(context):
    url = settings.backend_url + "/casting-postulations/"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    response = requests.get(url, headers=headers)
    context.response = response.json()

@then('the system will show me the submitted postulation')
def step_then_system_show_postulation(context):
    found = any(postulation['id'] == context.postulation_id for postulation in context.response)
    assert found, (
        f"Postulation with ID {context.postulation_id} not found in results. "
        f"Available postulations: {[c['id'] for c in context.response]}\n"
        f"Full response: {context.response}"
    )

@then('the system will not show me the submitted postulation')
def step_then_system_doesnt_show_postulation(context):
    assert len(context.response) == 0, "A postulation was found when it shouldn't have been"

@when('I try to delete the postulation')
def step_when_delete_postulation(context):
    url = settings.backend_url + "/casting-postulations/{postulation_id}"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    context.response = requests.delete(url.format(postulation_id=context.postulation_id), headers=headers)
    # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}

@then('the postulation will be deleted from the system')
def step_then_postulation_deleted(context):
    session = SessionLocal()
    try:
        casting_postulation = session.query(models.CastingPostulation) \
        .filter(models.CastingPostulation.id == context.postulation_id).first()

        assert casting_postulation.deleted_at is not None, "Casting postulation was not deleted."
    finally:
        session.close()

@when('I try to delete a non-existent postulation')
def step_when_delete_non_existent_postulation(context):
    url = settings.backend_url + "/casting-postulations/{postulation_id}"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    context.response = requests.delete(url.format(postulation_id=-1), headers=headers)
    # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}

@then('I should be notified that the postulation doesnt exists so it cant be deleted')
def step_then_notified_postulation_doesnt_exist_cant_be_deleted(context):
    assert "not found" in context.response.text, "Expected error message not found."


@given('an artist applied for the role with his account')
def step_given_other_user_apply_for_role(context):
    session = SessionLocal()
    try:
        #Se crea otro usuario de prueba que se postulara
        response = create_and_log_in_account(context, session)
        token = response.json().get('token')
        context.artist_user_id = response.json().get('id')
        form = session.query(models.Form).filter(models.Form.role_id == context.role_id).first()
        data = {row['field']: row['value'] for row in context.table}

        url = settings.backend_url + "/casting-postulations/"
        casting_postulation_data = {
        "form_id": form.id,
        "postulation_data": json.dumps(  # Enviar la data de la postulacion como un array de objetos JSON
                {"Nombre y Apellido": data["fullname"]}
            )
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(url, data=casting_postulation_data, headers=headers)
        context.responsejson = response.json()
        context.postulation_id = context.responsejson["id"]


    finally:
        session.close()

@when('I try to view the postulation list for roles within the casting')
def step_when_get_postulation_list_my_casting(context):
    url = settings.backend_url + "/casting-calls/with-postulations/{casting_call_id}"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    context.response = requests.get(url.format(casting_call_id=context.casting_call_id), headers=headers)
    context.responsejson = context.response.json()

@then('the system will show me the artists postulation')
def step_then_show_artist_postulation(context):
    postulation_ids = []

    # Recorrer open_roles y luego las postulaciones
    for role in context.responsejson.get('open_roles', []):
        for postulation in role.get('casting_postulations', []):
            postulation_ids.append(postulation['id'])

    assert context.postulation_id in postulation_ids, (
        f"Postulation ID {context.postulation_id} not found in response, insted found {context.responsejson}"
    )

@then('the system wont show any postulation')
def step_then_not_show_postulation(context):
    assert context.responsejson.get('open_roles', []) == [], 'User could get information from other casting'

@then('I will be notify that "{error_message}"')
def step_then_notifiy_error_message(context, error_message):
    assert error_message in context.response.text, f"Expected error message not found {context.response.text}"

@when('I try to reject the postulation')
def step_when_reject_postulation(context):
    url = settings.backend_url + "/casting-postulations/reject"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    context.response = requests.patch(url, json={"ids": [context.postulation_id]}, headers=headers)
    # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}

@then('the postulation is rejected')
def step_then_postulation_rejected(context):
    session = SessionLocal()
    try:
        casting_postulation = session.query(models.CastingPostulation) \
        .filter(models.CastingPostulation.id == context.postulation_id).first()

        assert casting_postulation.state == "Rechazada", "Casting postulation was not rejected."
    finally:
        session.close()

@then('the postulation will be deleted from the casting')
def step_then_postulation_deleted_from_casting(context):
    postulation_ids = []

    # Recorrer open_roles y luego las postulaciones
    for role in context.responsejson.get('open_roles', []):
        for postulation in role.get('casting_postulations', []):
            postulation_ids.append(postulation['id'])

    assert context.postulation_id not in postulation_ids, (
        f"Postulation ID {context.postulation_id} found in response"
    )

@then('the postulation is not rejected')
def step_then_postulation_not_rejected(context):
    session = SessionLocal()
    try:
        casting_postulation = session.query(models.CastingPostulation) \
        .filter(models.CastingPostulation.id == context.postulation_id).first()

        assert casting_postulation.state != "Rechazada", "Casting postulation was rejected when it shouldnt be."
    finally:
        session.close()

@when('I try to choose the postulation')
def step_when_choose_postulation(context):
    url = settings.backend_url + "/casting-postulations/choose/{postulation_id}"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    context.response = requests.patch(url.format(postulation_id=context.postulation_id), headers=headers)
    # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}

@then('the postulation is chosen')
def then_postulation_chosen(context):
    session = SessionLocal()
    try:
        casting_postulation = session.query(models.CastingPostulation) \
        .filter(models.CastingPostulation.id == context.postulation_id).first()

        assert casting_postulation.state == "Elegida", "Casting postulation was not chosen."
    finally:
        session.close()


@then('the postulation is not chosen')
def then_postulation_not_chosen(context):
    session = SessionLocal()
    try:
        casting_postulation = session.query(models.CastingPostulation) \
        .filter(models.CastingPostulation.id == context.postulation_id).first()

        assert casting_postulation.state != "Elegida", "Casting postulation was incorrectly chosen."
    finally:
        session.close()

@given('I reject the postulation')
def step_given_reject_postulation(context):
    url = settings.backend_url + "/casting-postulations/reject"
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    context.response = requests.patch(url, json={"ids": [context.postulation_id]}, headers=headers)
    # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}