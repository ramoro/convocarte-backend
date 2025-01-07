from behave import given, when, then
import requests
from environment import SessionLocal
from config import settings
import models
from sqlalchemy.orm import joinedload
from sqlalchemy import and_


@when('I create a project with name "{project_name}"')
def step_impl(context, project_name):
    url = settings.backend_url + "/projects/"
    role_data = {"name": "Neo"}
    project_creation_data = {"name": project_name, "description": "Matrix project", 
                             "region": "Ciudad Autónoma de Buenos Aires", "category": "Cine-largometraje",
                             "roles": [role_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=project_creation_data, headers=headers)
    context.response = response


@then('a project with the name "{project_name}" should be created successfully')
def step_impl(context, project_name):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(and_(
                models.Project.name == project_name,
                models.Project.owner_id == context.user_id
            )).first()
        assert project is not None, f"Project with name {project_name} was not created"
    finally:
        session.close()

@given('I have a project with name "{project_name}"')
def step_impl(context, project_name):
    url = settings.backend_url + "/projects/"
    role_data = {"name": "Neo"}
    project_creation_data = {"name": project_name, "description": "Matrix project", 
                             "region": "Ciudad Autónoma de Buenos Aires", "category": "Cine-largometraje",
                             "roles": [role_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=project_creation_data, headers=headers)
    context.response = response

@then('the project should not be created for the user')
def step_impl(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that they already have a project with that name')
def step_impl(context):
    assert "The user already has a project with the name" in context.response.text, "Expected error message not found"

@when('I create a project named "{project_name}" with two roles named "{role_name}"')
def step_impl(context, project_name, role_name):
    url = settings.backend_url + "/projects/"
    role_data = {"name": role_name}
    project_creation_data = {"name": project_name, "description": "Matrix project", 
                             "region": "Ciudad Autónoma de Buenos Aires", "category": "Cine-largometraje",
                             "roles": [role_data, role_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=project_creation_data, headers=headers)
    context.response = response

@then('the user should be notified that the project shouldnt have more than one role with the same name')
def step_impl(context):
    assert "project mustnt have two roles with the same name" in context.response.text, "Expected error message not found"

@when('I create a project named "{project_name}" with no roles')
def step_impl(context, project_name):
    url = settings.backend_url + "/projects/"

    project_creation_data = {"name": project_name, "description": "Matrix project", 
                             "region": "Ciudad Autónoma de Buenos Aires", "category": "Cine-largometraje",
                             "roles": []}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=project_creation_data, headers=headers)
    context.response = response

@then('the user should be notified that the project should have at least one role')
def step_impl(context):
    assert "project must have at least one role" in context.response.text, "Expected error message not found"


