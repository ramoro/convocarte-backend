from behave import given, when, then
import models
import requests
from environment import SessionLocal
from config import settings

@given('there is no account registered with the email "{email}"')
def step_given_no_account_with_email(context, email):
    session = SessionLocal()
    try:
        session.query(models.User).filter(models.User.email == email).delete()
        session.commit()
    finally:
        session.close()

@when('I register an account with valid data')
def step_when_register_account(context):
    url = settings.backend_url + "/users/"
    data = {field["field"]: field["value"] for field in context.table}
    response = requests.post(url, json=data)
    context.response = response
    assert response.status_code == 5001, f"Response: {response}"
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}, response: {response.text}"

@then('an account with the email "{email}" is created in the system')
def step_then_account_created(context, email):
    session = SessionLocal()
    try:
        user = context.database.query(models.User).filter(models.User.email == email).first()
        assert user is not None, f"User with email {email} was not created. User: {user}"
    finally:
        session.close()

@given('there is an account registered with the email "{email}"')
def step_given_account_with_email(context, email):
    session = SessionLocal()
    try:
        session.query(models.User).filter(models.User.email == email).delete()
        session.commit()
        user = models.User(fullname="Existing User", email=email, password="Password123*")
        session.add(user)
        session.commit()
    finally:
        session.close()

@when('I try to register an account with the same email and a valid data')
def step_when_register_account_with_same_email(context):
    url = settings.backend_url + "/users/"
    data = {field["field"]: field["value"] for field in context.table}
    response = requests.post(url, json=data)
    context.response = response

@then('the account is not created in the system')
def step_then_account_not_created(context):
    assert context.response.status_code != 201, f"Unexpected status code: {context.response.status_code}, response: {context.response.text}"

@then('the user is notified that an account with that email already exists')
def step_then_user_notified_email_exists(context):
    assert "The email is already used." in context.response.text, "Expected error message not found"

@when('I register an account with that email and no full name')
def step_when_register_account_with_no_fullname(context):
    url = settings.backend_url + "/users/"
    data = {field["field"]: field["value"] for field in context.table}
    response = requests.post(url, json=data)
    context.response = response

@then('the user is notified that the field is required')
def step_then_user_notified_fullname_required(context):
    response_json = context.response.json()
    error_message = response_json['detail'][0]['msg']
    assert "Field required" == error_message, "Expected error message not found"

@when('I register an account with no email')
def step_when_register_account_with_no_email(context):
    url = settings.backend_url + "/users/"
    data = {field["field"]: field["value"] for field in context.table}
    response = requests.post(url, json=data)
    context.response = response

@when('I register an account with no password')
def step_when_register_account_with_no_password(context):
    url = settings.backend_url + "/users/"
    data = {field["field"]: field["value"] for field in context.table}
    response = requests.post(url, json=data)
    context.response = response

@when('I register with a password that does not match the confirmation password')
def step_when_register_account_with_password_mismatch(context):
    url = settings.backend_url + "/users/"
    data = {field["field"]: field["value"] for field in context.table}
    response = requests.post(url, json=data)
    context.response = response

@then('the user is notified that the passwords must match')
def step_then_user_notified_password_mismatch(context):
    assert "passwords must match" in context.response.text, "Expected error message not found"