from behave import when, then
import requests
import models
from environment import SessionLocal
from config import settings

@when('I pause the casting call')
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

@then('the casting call should be successfully paused')
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
        assert casting_call.state == "Pausado", f"Casting call is not paused. Current state: {casting_call.state}"
    finally:
        session.close()

@then('the casting call should not be paused')
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
        assert casting_call.state != "Pausado", f"Casting call was incorrectly paused."
    finally:
        session.close()

@then("the user should be notified that the casting cannot be paused because it hasn't been published yet")
def step_impl(context):
    assert "casting cannot be paused because it hasn't been published yet" in context.response.text, "Expected error message not found."

@then("the user should be notified that the casting cannot be paused because it has already ended")
def step_impl(context):
    assert "casting cannot be paused because it has already ended" in context.response.text, "Expected error message not found."

