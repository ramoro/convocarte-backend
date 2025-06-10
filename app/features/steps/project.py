from behave import given, when, then
import requests
from environment import SessionLocal
from config import settings
import models
from sqlalchemy import and_


@when('I create a project with name "{project_name}"')
def step_when_create_project(context, project_name):
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
def step_then_project_created(context, project_name):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(and_(
                models.Project.name == project_name,
                models.Project.owner_id == context.user_id
            )).first()
        assert project is not None, f"Project with name {project_name} was not created"
    finally:
        session.close()

@given('I create a project named "{project_name}"')
def step_given_project_created(context, project_name):
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
def step_then_project_not_created(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user should be notified that they already have a project with that name')
def step_then_user_notified_project_already_exists(context):
    assert "The user already has a project named" in context.response.text, "Expected error message not found"

@when('I create a project called "{project_name}" with two roles named "{role_name}"')
def step_when_create_project_with_two_roles_same_name(context, project_name, role_name):
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
def step_then_user_notified_cant_have_two_roles_same_name_in_project(context):
    assert "project mustnt have two roles with the same name" in context.response.text, "Expected error message not found"

@when('I create a project named "{project_name}" with no roles')
def step_when_create_project_no_roles(context, project_name):
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
def step_then_user_notified_project_must_have_at_least_one_role(context):
    assert "project must have at least one role" in context.response.text, "Expected error message not found"

@when('I try to delete the project')
def step_when_delete_project(context):
    url = settings.backend_url + "/projects/{project_id}"

    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    response = requests.delete(url.format(project_id=context.project_id), headers=headers)
    context.response = response

@then('the project should successfully desappear from the system')
def step_then_project_deleted(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.deleted_at is not None, "Project was not deleted"
    finally:
        session.close()
        
@then('the castings associated should desappear from the system')
def step_then_castings_associated_deleted(context):
    session = SessionLocal()
    try:
        castings = context.database.query(models.CastingCall).filter(models.CastingCall.project_id == context.project_id).all()
        assert castings[0].deleted_at is not None, "Casting calls were not deleted"
    finally:
        session.close()

@then('the project should not be eliminated from the system')
def step_then_project_not_deleted(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.deleted_at is None, "Project was deleted"
    finally:
        session.close()

@then('the user should be notified that the project is being used and must end the castings that are using it in order to delete the project')
def step_then_notified_must_delete_castings_to_delete_project(context):
    assert "cant be deleted cause its being used by a casting call" in context.response.text, "Expected error message not found"

@when('I try to edit project name, project description and role name')
def step_when_edit_project(context):
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
def step_then_project_updated(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        updated = (project.name == context.new_project_name and project.description == context.new_project_description \
                    and project.roles and project.roles[0].name == context.new_role_name)
        assert updated, "Project name was not correctly updated"
    finally:
        session.close()

@then('the project information should not be successfully updated on the system')
def step_then_project_not_updated(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        updated = (project.name != context.new_project_name and project.description != context.new_project_description \
                    and project.roles and project.roles[0].name != context.new_role_name)
        assert updated, "Project name was incorrectly updated"
        assert context.response.status_code != 204, "Incorrect status code"
    finally:
        session.close()

@then('the user should be notified that the project is being used and must end the castings that are using it in order to update the project')
def step_then_user_notified_casting_must_be_ended_to_edit_project(context):
    assert "cant be updated cause its being used by a casting call" in context.response.text, "Expected error message not found"

@when('I try to edit project named "{project_name}" with name "{new_name}"')
def step_when_edit_project_with_existing_name(context, project_name, new_name):
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

@given('I create a project called "{project_name}" with two roles named "{role_one_name}" and "{role_two_name}"')
def step_given_project_created_with_two_roles(context, project_name, role_one_name, role_two_name ):
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
def step_when_edit_roles_with_same_name(context, role_name):
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
def step_project_roles_not_updated(context):
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        assert project.roles[0].name != project.roles[1].name, "Project name was incorrectly updated"
        assert context.response.status_code != 204, "Incorrect status code"
    finally:
        session.close()

@when('I attempt to delete the role called "{role_name}"')
def step_when_delete_role(context, role_name):
    url = settings.backend_url + "/projects/{project_id}"
    session = SessionLocal()
    try:
        project = context.database.query(models.Project).filter(models.Project.id == context.project_id).first()
        updated_roles = [role for role in project.roles if role.name != role_name]
        project_updated_data = {"name": project.name, "description": project.description, 
                                "region": project.region, "category": project.category, "is_used": False,
                                "roles": [{"name": r.name, "description": r.description} for r in updated_roles]}

        headers = {
            "Authorization": f"Bearer {context.token}"
        }
        
        response = requests.put(url.format(project_id=context.project_id), json=project_updated_data, headers=headers)
        context.response = response
        context.role_removed_name = role_name
        context.new_project_roles = updated_roles
    finally:
        session.close()

@then('the role is removed from the project')
def step_then_role_removed_from_project(context):
    session = SessionLocal()

    try:
        project = session.query(models.Project).filter(
            models.Project.id == context.project_id
        ).first()
        
        remaining_role_names = [role.name for role in project.roles]
        assert context.role_removed_name not in remaining_role_names, \
            f"Role '{context.role_removed_name}' was found in project roles after deletion"     
    finally:
        session.close()

@then('the role is not deleted')
def step_then_role_not_deleted(context):
    session = SessionLocal()

    try:
        project = session.query(models.Project).filter(
            models.Project.id == context.project_id
        ).first()
        
        remaining_role_names = [role.name for role in project.roles]
        assert context.role_removed_name in remaining_role_names, \
            f"Role '{context.role_removed_name}' wasnt found in project after incorrect deletion"     
    finally:
        session.close()

@then('Im notified that the project cannot remain without roles')
def step_then_notified_project_must_have_at_least_one_role(context):
    assert "project must have at least one role" in context.response.text, "Expected error message not found"
