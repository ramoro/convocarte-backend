from behave import given, when, then
import requests
from config import settings
import models
from environment import SessionLocal
import models
from casting_call import create_and_log_in_account


@when('I try to send a message to the artist that says "{message_content}"')
def step_when_send_message_to_artist(context, message_content):
    url = settings.backend_url + "/messages/"

    message_data = {"content": message_content, 
                    "receiver_id": context.artist_user_id, 
                    "postulation_id": context.postulation_id}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    
    context.response = requests.post(url, data=message_data, headers=headers)
    context.responsejson = context.response.json()
    if 'id' in context.responsejson:
        context.casting_director_message_id = context.responsejson['id']
    else:
        context.casting_director_message_id = -1

@then('a message with the content "{content_message}" is created')
def step_then_message_created(context, content_message):
    session = SessionLocal()
    try:
        message = context.database.query(models.Message).filter(models.Message.content == content_message).first()
        assert message is not None, f"Message with content {content_message} was not created"
    finally:
        session.close()

@then('the artist postulation receives the message')
def step_then_artist_receives_message(context):
    session = SessionLocal()
    try:
        message = context.database.query(models.Message).filter(models.Message.id == context.casting_director_message_id).first()
        assert message.receiver_id == context.artist_user_id, f"Message was not received by the artist with id {context.artist_user_id}"
    finally:
        session.close()

@given('an artist that did not postulate for the role')
def step_given_an_artist_not_postulated(context):
    session = SessionLocal()
    try:
        response = create_and_log_in_account(context, session)
        context.artist_user_id = response.json().get('id')
        context.postulation_id = -1
    finally:
        session.close()

@then('a message with the content "{content_message}" is not created')
def step_then_message_not_created(context, content_message):
    session = SessionLocal()
    try:
        message = context.database.query(models.Message).filter(models.Message.content == content_message).first()
        assert message is None, f"Message with content {content_message} was created"
    finally:
        session.close()

@given('the casting director owner of the casting sends me a message')
def step_given_casting_director_sends_message(context):
    url = settings.backend_url + "/messages/"

    message_data = {"content": "Message content", 
                    "receiver_id": context.user_id, 
                    "postulation_id": context.postulation_id}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    
    context.response = requests.post(url, data=message_data, headers=headers)
    context.responsejson = context.response.json()
    if 'id' in context.responsejson:
        context.casting_director_message_id = context.responsejson['id']
    else:
        context.casting_director_message_id = -1

@when('I try to response to the message telling "{message_content}"')
def step_when_respond_message(context, message_content):
    url = settings.backend_url + "/messages/"

    message_data = {"content": message_content, 
                    "receiver_id": context.casting_director_id, 
                    "postulation_id": context.postulation_id,
                    "previous_message_id": context.casting_director_message_id}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    context.response = requests.post(url, data=message_data, headers=headers)
    context.responsejson = context.response.json()
    if 'id' in context.responsejson:
        context.response_message_id = context.responsejson['id']
    else:
        context.response_message_id = -1

@then('the casting director receives the message')
def step_then_casting_director_receives_message(context):
    session = SessionLocal()
    try:
        message = context.database.query(models.Message).filter(models.Message.id == context.response_message_id).first()
        assert message.receiver_id == context.casting_director_id, f"Message was not received by the casting director with id {context.casting_director_id}"
    finally:
        session.close()

@when('I try to response to a non-existent message with "{message_content}"')
def step_when_response_non_existent_message(context, message_content):
    url = settings.backend_url + "/messages/"

    message_data = {"content": message_content, 
                    "receiver_id": context.casting_director_id, 
                    "postulation_id": context.postulation_id,
                    "previous_message_id": -1}
    
    headers = {
        "Authorization": f"Bearer {context.token}"
    }
    
    context.response = requests.post(url, data=message_data, headers=headers)
    context.responsejson = context.response.json()
    if 'id' in context.responsejson:
        context.response_message_id = context.responsejson['id']
    else:
        context.response_message_id = -1