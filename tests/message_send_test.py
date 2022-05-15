from pytest import fixture
import pytest 
import requests
import json
import datetime
from src import config
from src import message
from src.channel import channel_messages_v1
from src.message import message_send_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channel_messages, URL_channels_create, URL_clear, URL_message_send

def test_INPUT_ERROR_invalid_channel_id(first_channel_public_flask):
    response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": (first_channel_public_flask['channel_id'] + 1), "message": "loremipsum"})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_short(first_channel_public_flask):
    response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : ""})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_long(first_channel_public_flask):
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
    response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": (first_channel_public_flask['channel_id'] + 1), 
    "message" : new_message})
    assert response.status_code == INPUT_ERROR

def test_ACSESS_ERROR_invalid_token(first_channel_public_flask):
    response = requests.post(URL_message_send, json={"token": (first_channel_public_flask['token'] + '1'), 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum"})
    assert response.status_code == ACCESS_ERROR

def test_ACSESS_ERROR_token_user_not_in_channel(first_channel_public_flask, second_user_flask):
    response = requests.post(URL_message_send, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "loremipsum"})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_message_send(first_channel_public_flask):
    response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_same_channel(first_channel_public_flask):
    response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    time_now = datetime.datetime.now()
    compare_response = requests.get(URL_channel_messages, params = {'token': first_channel_public_flask['token'],
    'channel_id': first_channel_public_flask['channel_id'], 'start' : 0})
    message = json.loads(response.text)
    correct_message = {
        'messages' : [{
            'message_id' : message['message_id'],
            'u_id': 0,
            'message' : "Good Message",
            'time_sent': int(time_now.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }],
        'start' : 0,
        'end' : -1,
    }
    assert json.loads(compare_response.text) == correct_message
    assert response.status_code == VALID_STATUS


def test_VALID_STATUS_different_channels(first_channel_public_flask):
    second_channel_response = requests.post(URL_channels_create, 
    json={"token": first_channel_public_flask['token'], "name": 'second channel', "is_public": True})
    second_channel = json.loads(second_channel_response.text)

    response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    time_now = datetime.datetime.now()

    other_channel_message_response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": second_channel['channel_id'], "message" : "Other message"})
    

    compare_response = requests.get(URL_channel_messages, params = {'token': first_channel_public_flask['token'],
     'channel_id': first_channel_public_flask['channel_id'], 'start' : 0})
    message = json.loads(response.text)
    correct_message = {
        'messages' : [{
            'message_id' : message['message_id'],
            'u_id': 0,
            'message' : "Good Message",
            'time_sent': int(time_now.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }],
        'start' : 0,
        'end' : -1,
    }
    assert json.loads(compare_response.text) == correct_message
    assert response.status_code == VALID_STATUS
    assert other_channel_message_response.status_code == VALID_STATUS