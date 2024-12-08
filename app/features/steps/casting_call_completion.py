from behave import when, then
import requests
import models
from environment import SessionLocal
from config import settings

@when('I finish the casting call')
def step_impl(context):
    url = settings.backend_url + "/casting-calls/finish/{casting_id}"
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

@then('the casting call should be successfully finished')
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
        assert casting_call.state == "Finalizado", f"Casting call is not paused. Current state: {casting_call.state}"
    finally:
        session.close()

@then('the casting call should not be finished')
def step_impl(context):
    session = SessionLocal()
    try:
        casting_call = session.query(models.CastingCall).filter(models.CastingCall.title == context.casting_call_title).first()
        assert casting_call.state != "Finalizado", f"Casting call was incorrectly finished."
    finally:
        session.close()

@then("the user should be notified that the casting cannot be finished because it hasn't been published yet")
def step_impl(context):
    assert "casting cannot be finished because it hasn't been published yet" in context.response.text, "Expected error message not found."
