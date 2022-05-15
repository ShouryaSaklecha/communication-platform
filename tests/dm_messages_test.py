from pytest import fixture
import pytest 
import requests
import json
import datetime
from src import config
from src.channel import channel_messages_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_auth_register, URL_message_send, URL_dm_messages, URL_message_senddm

def test_INPUT_ERROR_invalid_dm_id(first_user_flask):
    response = requests.get(URL_dm_messages, params={"token": first_user_flask['token'], 
    'dm_id': -1, 'start': 0})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_start(first_dm_multiple_users_flask):
    response = requests.get(URL_dm_messages, params = {'token': first_dm_multiple_users_flask['token'],
    'dm_id': first_dm_multiple_users_flask['dm_id'], 'start' : 5})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_non_member_token(first_dm_multiple_users_flask):
    not_member_response = requests.post(URL_auth_register, json={"email": "notmember@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    not_member = json.loads(not_member_response.text)
    response = requests.get(URL_dm_messages, 
    params={'token': not_member['token'], 'dm_id': first_dm_multiple_users_flask['dm_id'], 'start' : 0})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(first_dm_multiple_users_flask):
    response = requests.get(URL_dm_messages, 
    params={'token': (first_dm_multiple_users_flask['token'] + '1'),
    'dm_id': first_dm_multiple_users_flask['dm_id'], 'start' : 0})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_messages_validity(first_dm_multiple_users_flask):
    response = requests.get(URL_dm_messages, params = {'token': first_dm_multiple_users_flask['token'],
    'dm_id': first_dm_multiple_users_flask['dm_id'], 'start' : 0})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_not_first(first_user_flask, first_dm_multiple_users_flask):
    first_message_response =requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "First Message"})
    time_now = datetime.datetime.now()
    second_message_response =requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "Second Message"})
    time_now_1 = datetime.datetime.now()
    requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "Third Message"})
    requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "Fourth Message"})
    first_message = json.loads(first_message_response.text)
    second_message = json.loads(second_message_response.text)
    
    response = requests.get(URL_dm_messages, params = {'token': first_dm_multiple_users_flask['token'],
     'dm_id': first_dm_multiple_users_flask['dm_id'], 'start' : 2})
    correct_message = {
        'messages' : [{
            'message_id' : second_message['message_id'],
            'u_id': first_user_flask["auth_user_id"],
            'message' : "Second Message",
            'time_sent': int(time_now_1.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        },{
            'message_id' : first_message['message_id'],
            'u_id': first_user_flask["auth_user_id"],
            'message' : "First Message",
            'time_sent': int(time_now.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }],
        'start' : 2,
        'end' : -1,
    }
    assert json.loads(response.text) == correct_message
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_channel_message_included(first_user_flask, first_dm_multiple_users_flask, first_channel_public_flask):
    dm_message_response =requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "DM Message"})
    time_now = datetime.datetime.now()
    requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Channel Message"})
    dm_message = json.loads(dm_message_response.text)
    
    response = requests.get(URL_dm_messages, params = {'token': first_dm_multiple_users_flask['token'],
     'dm_id': first_dm_multiple_users_flask['dm_id'], 'start' : 0})
    correct_message = {
        'messages' : [{
            'message_id' : dm_message['message_id'],
            'u_id': first_user_flask["auth_user_id"],
            'message' : "DM Message",
            'time_sent': int(time_now.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }],
        'start' : 0,
        'end' : -1,
    }
    assert json.loads(response.text) == correct_message
    assert response.status_code == VALID_STATUS