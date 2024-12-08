from behave import given, when, then
import requests
import models
from environment import SessionLocal
from config import settings
from sqlalchemy import and_
import json

@given('Im logged in on the platform with my account')
def step_impl(context):
    session = SessionLocal()
    try:
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
        context.token = response.json().get('token')
    finally:
        session = SessionLocal()

@given('I have a form template with title "{template_title}"')
def step_impl(context, template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": template_title, "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=form_template_data, headers=headers)
    context.response = response

@given('I have a project with name "{project_name}" and an associated role called "{role_name}"')
def step_impl(context, project_name, role_name):
    url = settings.backend_url + "/projects/"
    role_data = {"name": role_name}
    project_data = {"name": project_name, "region": "CABA", "category": "Teatro", "roles": [role_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    response = requests.post(url, json=project_data, headers=headers)
    context.response = response

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
        context.casting_call_title = casting_call_data_table["title"]
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
