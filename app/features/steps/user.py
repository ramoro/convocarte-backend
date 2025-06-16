from behave import given, when, then
import models
import requests
from environment import SessionLocal
from config import settings
from casting_call import create_and_log_in_account

@when('I try to delete my account')
def step_when_account_delete(context):
    url = settings.backend_url + "/users/{user_id}"
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }

    context.response = requests.delete(
        url.format(user_id=context.user_id),
        headers=headers
    )
     # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}

@then('the account is deleted from the system')
def step_then_account_deleted_from_system(context):
    session = SessionLocal()
    try:
        user = context.database.query(models.User).filter(models.User.id == context.user_id).first()
        assert user.deleted_at != None, "User was not deleted."
    finally:
        session.close()

@given('I create a project called "{project_name}" with a role called "{role_name}"')
def step_given_project_created(context, project_name, role_name):
    url = settings.backend_url + "/projects/"
    role_data = {"name": role_name}
    project_data = {"name": project_name, "region": "CABA", "category": "Teatro", "roles": [role_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    response = requests.post(url, json=project_data, headers=headers)
    context.responsejson = response.json()
    context.project_id = context.responsejson["id"]

@then('the project is deleted from the system along with the role')
def step_then_project_deleted(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.deleted_at is not None, "Project was not deleted"
        for role in project.roles:
            assert role.deleted_at is not None, f"Role {role.name} was not deleted"
    finally:
        session.close()

@given('I create a form template with title "{template_title}" and some form fields')
def step_impl(context, template_title):
    url = settings.backend_url + "/form-templates/"
    # Procesar la tabla de campos del formulario
    form_template_field_data = []
    for row in context.table:
        field_data = {field["field"]: field["value"] for field in context.table}
    form_template_field_data.append(field_data)
    
    form_template_data = {
        "form_template_title": template_title,
        "form_template_fields": form_template_field_data
    }

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=form_template_data, headers=headers)
    context.response = response
    context.responsejson = response.json()
    context.form_template_id = context.responsejson["id"]

@then('the form template is deleted from the system')
def step_then_form_template_deleted(context):
    session = SessionLocal()
    try:
        form_template = context.database.query(models.FormTemplate) \
            .filter(models.FormTemplate.id == context.form_template_id).first()
        assert form_template == None, "Form Template was not deleted"
    finally:
        session.close()

@when('I try to delete an non-existent account')
def step_when_non_existent_account_delete(context):
    url = settings.backend_url + "/users/{user_id}"
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }

    context.response = requests.delete(
        url.format(user_id=context.user_id + 50),
        headers=headers
    )
     # Solo parsea a json si tiene contenido, para tomar errores
    try:
        context.response_json = context.response.json() if context.response.content else {}
    except ValueError:
        context.response_json = {}

@then('the account is not deleted from the system')
def step_then_account_not_deleted(context):
    assert len(context.response_json) > 0, "Account was incorrectly deleted"

@then('i am notified that the account couldnt be deleted because it doesnt exists')
def step_then_user_notified_account_doesnt_exist(context):
    assert "Account couldnt be deleted cause it doesnt exists" in context.response.text, "Expected error message not found"

@then('the postulation is deleted from the system')
def step_then_postulation_deleted(context):
    session = SessionLocal()
    try:
        postulation = context.database.query(models.CastingPostulation) \
            .filter(models.CastingPostulation.id == context.postulation_id).first()
        assert postulation.deleted_at != None, "Postulation was not deleted"
    finally:
        session.close()

@when('I try to update my weight with {weight_value} and my height with {height_value} in my profile')
def step_when_update_my_weight_and_height(context, weight_value, height_value):
    url = settings.backend_url + "/users/{user_id}"
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }

    context.response = requests.patch(
        url.format(user_id=context.user_id),
        json={"weight": weight_value, "height": height_value},
        headers=headers
    )

    context.response_json = context.response.json() if context.response.content else {}

@then('my weight is updated with {weight_value} and my height with {height_value} in the system')
def step_then_my_weight_and_height_updated(context, weight_value, height_value):
    session = SessionLocal()
    try:
        user = context.database.query(models.User) \
            .filter(models.User.id == context.user_id).first()
        assert user.weight == float(weight_value), "Weight was not updated"
        assert user.height == float(height_value), "Height was not updated"

    finally:
        session.close()

@given('there is another user with a different account')
def step_given_existent_user(context):
    session = SessionLocal()
    try:
        response = create_and_log_in_account(context, session)
        context.other_user_id = response.json().get('id')
    finally:
        session = session.close()

@when('I try to update that users weight and height with {weight_value} and {height_value} respectively')
def step_when_update_other_user_weight_height(context, weight_value, height_value):
    url = settings.backend_url + "/users/{user_id}"
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }

    context.response = requests.patch(
        url.format(user_id=context.other_user_id),
        json={"weight": weight_value, "height": height_value},
        headers=headers
    )

    context.response_json = context.response.json() if context.response.content else {}

@then('the weight and height of the other user it not updated with {weight_value} and {height_value} respectively')
def step_then_weight_and_height_other_user_not_updated(context, weight_value, height_value):
    session = SessionLocal()
    try:
        user = context.database.query(models.User) \
            .filter(models.User.id == context.other_user_id).first()
        assert user.weight != float(weight_value), "Weight was incorrectly updated"
        assert user.height != float(height_value), "Height was incorrectly updated"

    finally:
        session.close()

@then('I am notified that I cannot update the information of a user I am not logged in as')
def step_then_user_notified_cannot_update_other_user(context):
    assert "Cannot update other user information" in context.response.text, "Expected error message not found"
