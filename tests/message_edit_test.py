from pytest import fixture
import pytest 
import requests
import json
from src import config
from src import message
from src.channel import channel_messages_v1
from src.message import message_send_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_message_edit, URL_message_send, URL_channel_addowner, URL_channel_messages, URL_message_remove, URL_message_senddm, URL_message_edit

def test_VALID_STATUS_edit(three_messages):
    response = requests.put(URL_message_edit, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID'], "message": "loremipsum"})
    assert response.status_code == VALID_STATUS

def test_INPUT_ERROR_nomessage(three_messages):
    response = requests.put(URL_message_edit, json={"token": three_messages['token'],
    "message_id": three_messages['message3_ID'] + 2, "message": "loremipsum"})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_notsender_notowner(three_messages, second_member_in_channel_public_flask):
    response = requests.put(URL_message_edit, json={"token": second_member_in_channel_public_flask['second_token'],
    "message_id": three_messages['message2_ID'], "message": "loremipsum"})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_notindm_notowner(first_dm_multiple_users_flask):
    response = requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "Good Message"})
    assert response.status_code == VALID_STATUS
    message_sent = json.loads(response.text)
    response2 = requests.put(URL_message_edit, json={"token": first_dm_multiple_users_flask['second_user_token'],
    "message_id": message_sent['message_id'], "message": "loremipsum"})
    assert response2.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(three_messages):
    response1 = requests.put(URL_message_edit, json={"token": three_messages['token'] + '1',
    "message_id": three_messages['message2_ID'], "message": "loremipsum"})
    assert response1.status_code == ACCESS_ERROR

def test_INPUT_ERROR_long(three_messages):
    new_message = """Lorem ipsum dolor sit amet, consectetuer adipiscing 
        elit. Aenean commodo 
        ligula eget dolor. Aenean massa. Cum sociis natoque 
        penatibus et magnis dis parturient montes, nascetur 
        ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
        pretium quis, sem. Nulla consequat massa quis enim. Donec pede 
        justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim
        justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam 
        dictum felis eu pede mollis pretium. Integer tincidunt. Cras 
        dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend
        tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend
        ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, 
        tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. 
        Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi.
        Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem 
        quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"""
    response1 = requests.put(URL_message_edit, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID'], "message": new_message})
    assert response1.status_code == INPUT_ERROR

def test_INPUT_ERROR_short(three_messages):
    response1 = requests.put(URL_message_edit, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID'], "message": ""})
    assert response1.status_code == VALID_STATUS
    response2 = requests.delete(URL_message_remove, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID']})
    assert response2.status_code == INPUT_ERROR

def test_VALID_STATUS_channel_messages(three_messages):
    response = requests.put(URL_message_edit, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID'], "message": "loremipsum"})
    assert response.status_code == VALID_STATUS
    # get messages for that channel after user is removed
    compare_response = requests.get(URL_channel_messages, params = {'token': three_messages['token'],
     'channel_id': three_messages['c_id'], 'start' : 0})
    assert compare_response.status_code == VALID_STATUS
    message = json.loads(response.text)
    #compare message to expected replacement.
    correct_message = "loremipsum"
    channel_messages_returns = json.loads(compare_response.text)
    messages = channel_messages_returns['messages'][1]
    message = messages['message']
    assert message == correct_message

def test_VALID_STATUS_dm_messages(three_dm_messages):
    response1 = requests.put(URL_message_edit, json={"token": three_dm_messages['first_token'],
    "message_id": three_dm_messages['message2_ID'], "message": "hello"})
    assert response1.status_code == VALID_STATUS
