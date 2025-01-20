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

@given('I have a project named "{project_name}"')
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
    context.responsejson = response.json()
    context.project_id = context.responsejson["id"]

@then('the project should not be created for the user')
def step_impl(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that they already have a project with that name')
def step_impl(context):
    print(context.response.text)
    assert "The user already has a project named" in context.response.text, "Expected error message not found"

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

@when('I try to delete the project')
def step_impl(context):
    url = settings.backend_url + "/projects/{project_id}"

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.delete(url.format(project_id=context.project_id), headers=headers)
    context.response = response

@then('the project should successfully desappear from the system')
def step_impl(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.deleted_at is not None, f"Project was not deleted"
    finally:
        session.close()
        
@then('the castings associated should desappear from the system')
def step_impl(context):
    session = SessionLocal()
    try:
        castings = context.database.query(models.CastingCall).filter(models.CastingCall.project_id == context.project_id).all()
        assert castings[0].deleted_at is not None, f"Casting calls were not deleted"
    finally:
        session.close()

@then('the project should not be eliminated from the system')
def step_impl(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.deleted_at is None, f"Project was deleted"
    finally:
        session.close()

@then('the user should be notified that the project is being used and must end the castings that are using it in order to delete the project')
def step_impl(context):
    assert "cant be deleted cause its being used by a casting call" in context.response.text, "Expected error message not found"

@when('I try to edit project name, project description and role name')
def step_impl(context):
    url = settings.backend_url + "/projects/{project_id}"
    updating_data = {field["field"]: field["value"] for field in context.table}

    role_data = {"name": updating_data["new_role_name"]}
    project_updated_data = {"name": updating_data["new_name"], "description": updating_data["new_description"], 
                             "region": updating_data["region"], "category": updating_data["category"], "is_used": False,
                             "roles": [role_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.put(url.format(project_id=context.project_id), json=project_updated_data, headers=headers)
    context.response = response
    context.new_project_name = updating_data["new_name"]
    context.new_project_description = updating_data["new_description"]
    context.new_role_name = updating_data["new_role_name"]

@then('the project information should be successfully updated on the system')    
def step_impl(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        updated = (project.name == context.new_project_name and project.description == context.new_project_description \
                    and project.roles and project.roles[0].name == context.new_role_name)
        assert updated, f"Project name was not correctly updated"
    finally:
        session.close()

@then('the project information should not be successfully updated on the system')
def step_impl(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        updated = (project.name != context.new_project_name and project.description != context.new_project_description \
                    and project.roles and project.roles[0].name != context.new_role_name)
        assert updated, f"Project name was incorrectly updated"
        assert context.response.status_code != 204, "Incorrect status code"
    finally:
        session.close()

@then('the user should be notified that the project is being used and must end the castings that are using it in order to update the project')
def step_impl(context):
    assert "cant be updated cause its being used by a casting call" in context.response.text, "Expected error message not found"

@when('I try to edit project named "{project_name}" with name "{new_name}"')
def step_impl(context, project_name, new_name):
    url = settings.backend_url + "/projects/{project_id}"
    updating_data = {field["field"]: field["value"] for field in context.table}

    role_data = {"name": updating_data["new_role_name"]}
    project_updated_data = {"name": new_name, "description": updating_data["new_description"], 
                             "region": updating_data["region"], "category": updating_data["category"], "is_used": False,
                             "roles": [role_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.put(url.format(project_id=context.project_id), json=project_updated_data, headers=headers)
    context.response = response
    context.new_project_name = new_name
    context.new_project_description = updating_data["new_description"]
    context.new_role_name = updating_data["new_role_name"]

@given('I create a project named "{project_name}" with two roles named "{role_one_name}" and "{role_two_name}"')
def step_impl(context, project_name, role_one_name, role_two_name ):
    url = settings.backend_url + "/projects/"
    role_one_data = {"name": role_one_name}
    role_two_data = {"name": role_two_name}

    project_creation_data = {"name": project_name, "description": "Matrix project", 
                             "region": "Ciudad Autónoma de Buenos Aires", "category": "Cine-largometraje",
                             "roles": [role_one_data, role_two_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.post(url, json=project_creation_data, headers=headers)
    context.response = response
    context.responsejson = response.json()
    context.project_id = context.responsejson["id"]

@when('I try to edit project setting two roles named "{role_name}"')
def step_impl(context, role_name):
    url = settings.backend_url + "/projects/{project_id}"
    updating_data = {field["field"]: field["value"] for field in context.table}

    role_data = {"name": role_name}
    project_updated_data = {"name": updating_data["new_name"], "description": updating_data["new_description"], 
                             "region": updating_data["region"], "category": updating_data["category"], "is_used": False,
                             "roles": [role_data, role_data]}

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.put(url.format(project_id=context.project_id), json=project_updated_data, headers=headers)
    context.response = response

@then('the project roles should not be successfully updated on the system')
def step_impl(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.roles[0].name != project.roles[1].name, f"Project name was incorrectly updated"
        assert context.response.status_code != 204, "Incorrect status code"
    finally:
        session.close()