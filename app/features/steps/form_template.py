from behave import given, when, then
import requests
from environment import SessionLocal
from config import settings
import models
from sqlalchemy.orm import joinedload
from sqlalchemy import and_


@when('I create a form template with title "{template_title}" and some form fields')
def step_impl(context, template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": template_title, "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=form_template_data, headers=headers)
    context.response = response

@then('a form template with the title "{form_template_title}" should be created successfully for the user')
def step_impl(context, form_template_title):
    session = SessionLocal()
    try:
        form_template = session.query(models.FormTemplate).filter(and_(
                models.FormTemplate.form_template_title == form_template_title,
                models.FormTemplate.owner_id == context.user_id
            )).first()
        assert form_template is not None, f"Form template with title {form_template_title} was not created"
    finally:
        session.close()

@given('I have a form template with title "{template_title}" and some form fields')
def step_impl(context, template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": template_title, "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=form_template_data, headers=headers)
    context.response = response

@then('the form template should not be created for the user')
def step_impl(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that they already have a form with that title')
def step_impl(context):
    assert "The user already has a form template with the title" in context.response.text, "Expected error message not found"

@given('I have a form template with title "{template_title}" with one form field')
def step_impl(context, template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = {"title": "Instagram", "type": "text", "order": 0, "is_required": True}
    form_template_data = {"form_template_title": template_title, "form_template_fields": [form_template_field_data]}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=form_template_data, headers=headers)
    context.responsejson = response.json()

@when('I edit the form template adding a form field')
def step_impl(context):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = [{"title": "Instagram", "type": "text", "order": 0, "is_required": True},
                                {"title": "Facebook", "type": "text", "order": 1, "is_required": False}]

    form_template_updated_data = {"id": context.responsejson["id"],"original_form_template_title": context.responsejson["form_template_title"] ,
                                  "form_template_title": context.responsejson["form_template_title"], 
                                  "form_template_fields": form_template_field_data}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    requests.put(url, json=form_template_updated_data, headers=headers)

@then('the form template "{form_template_title}" should be updated with two form fields')
def step_impl(context, form_template_title):
    session = SessionLocal()
    try:
        form_template = (
            session.query(models.FormTemplate)
            .filter(and_(
                models.FormTemplate.id == context.responsejson["id"],
                models.FormTemplate.owner_id == context.user_id
            ))
            .options(joinedload(models.FormTemplate.form_template_fields))  # Carga los campos asociados
            .first()
        )
        assert len(form_template.form_template_fields) == 2 , f"Form template with title {form_template_title} was not updated"
    finally:
        session.close()

@when('I edit the form template "{original_form_template_title}" with the existing title "{new_form_template_title}"')
def step_impl(context, original_form_template_title, new_form_template_title):
    url = settings.backend_url + "/form-templates/"
    form_template_field_data = [{"title": "Instagram", "type": "text", "order": 0, "is_required": True},
                                {"title": "Facebook", "type": "text", "order": 1, "is_required": False}]

    form_template_updated_data = {"id": context.responsejson["id"],"original_form_template_title": original_form_template_title ,
                                  "form_template_title": new_form_template_title, 
                                  "form_template_fields": form_template_field_data}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.put(url, json=form_template_updated_data, headers=headers)
    context.response = response

@then('the form template "{original_form_template_title}" should not be updated')
def step_impl(context, original_form_template_title):
    session = SessionLocal()
    try:
        form_template = (
            session.query(models.FormTemplate)
            .filter(and_(
                models.FormTemplate.form_template_title == original_form_template_title,
                models.FormTemplate.owner_id == context.user_id
            ))
            .options(joinedload(models.FormTemplate.form_template_fields))  # Carga los campos asociados
            .first()
        )
        assert context.response.status_code == 409
        assert form_template != None,  f"Form template with title {original_form_template_title} was incorrectly updated"
        assert len(form_template.form_template_fields) == 1 , f"Form template with title {original_form_template_title} was incorrectly updated"
    finally:
        session.close()
