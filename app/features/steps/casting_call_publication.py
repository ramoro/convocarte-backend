from behave import given, when, then
import requests
import models
from environment import SessionLocal
from config import settings
from sqlalchemy import and_
import json
from datetime import datetime, timedelta 

@when('I publish the casting call "{casting_call_title}" with an expiration date greater than the current date')
def step_impl(context, casting_call_title):
    url = settings.backend_url + "/casting-calls/publish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == casting_call_title).first()
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
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
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
        context.casting_call_title = casting_call_data_table["title"]
    finally:
        session.close()

@given('I publish the casting call with an expiration date greater than the current date')
def step_impl(context):
    url = settings.backend_url + "/casting-calls/publish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
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
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
        pause_data = {
            "title": context.casting_call_title,
            "state": casting_call.state
        }

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        response = requests.patch(url.format(casting_id=casting_call.id), json=pause_data, headers=headers)
        context.response = response
    finally:
        session.close()

@when('I publish the casting call "{casting_call_title}" with an expiration date less than the current date')
def step_impl(context, casting_call_title):
    url = settings.backend_url + "/casting-calls/publish/{casting_id}"
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == casting_call_title).first()
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
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
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
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
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
