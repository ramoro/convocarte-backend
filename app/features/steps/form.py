from behave import given, when, then
import requests
from environment import SessionLocal
from config import settings
import models
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

@given('I create a form template with title "{template_title}" and one form field')
def step_given_create_form_template(context, template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": template_title, "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=form_template_data, headers=headers)
    context.responsejson = response.json()

@when('I edit the form "{form_title}" generated for the open role "{role_name}" setting three form fields') 
def step_when_update_form_for_open_role(context, form_title, role_name):
    url = settings.backend_url + "/forms"
    session = SessionLocal()
    try:
        open_role = session.query(models.OpenRole).filter(and_(
                models.OpenRole.casting_call_id == context.casting_call_id,
                models.OpenRole.role_id == context.role_id
        )).first()
        form = session.query(models.Form).filter(models.Form.id == open_role.form_id).first()
        form_fields_data = [{"title": "Instagram", "type": "text", "order": 0, "is_required": True},
                                {"title": "Facebook", "type": "text", "order": 1, "is_required": False},
                                {"title": "Nacionalidad", "type": "text", "order": 2, "is_required": False}]

        form_updated_data = {"id": form.id,
                            "form_title": form_title, 
                            "form_fields": form_fields_data}

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
    
        response = requests.put(url, json=form_updated_data, headers=headers)
        context.response = response
        context.form_id = form.id
    finally:
        session.close()

@then('form "{form_title}" associated to the role "{role_name}" within the casting call "{casting_call_title}" should have "{form_fields_amount}" form fields')
def step_then_form_updated(context, form_title, role_name, casting_call_title, form_fields_amount):
    session = SessionLocal()
    try:
        form = (
            session.query(models.Form)
            .filter(models.Form.id == context.form_id)
            .options(joinedload(models.Form.form_fields))  # Carga los campos asociados
            .first()
        )
        assert len(form.form_fields) == 3, f"Form {form_title} was not updated"
    finally:
        session.close()
@then('the form "{form_title}" associated to the role "{role_name}" within the casting call "{casting_call_title}" should not have "{form_fields_amount}" more fields')
def step_then_form_not_updated(context, form_title, role_name, casting_call_title, form_fields_amount):
    session = SessionLocal()
    try:
        form = (
            session.query(models.Form)
            .filter(models.Form.id == context.form_id)
            .options(joinedload(models.Form.form_fields))  # Carga los campos asociados
            .first()
        )
        assert len(form.form_fields) < 3, f"Form {form_title} was updated incorrectly"
    finally:
        session.close()

@then('the user should be notified that the form cant be updated cause it belongs to a published casting call')
def step_then_user_notified_form_cant_be_updated_belongs_published_casting(context):
    assert "cant be updated cause its casting call is published" in context.response.text, "Expected error message not found"

@then('the user should be notified that the form cant be updated cause it belongs to a finished casting call')
def step_then_user_notified_form_cant_be_updated_belongs_ended_casting(context):
    assert "cant be updated cause its casting call has finished" in context.response.text, "Expected error message not found"
