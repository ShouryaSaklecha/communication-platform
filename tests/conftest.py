from pytest import fixture
import pytest
import requests
import json
import datetime
from src import config
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from tests.routes_test import *

@fixture
def clear():
    clear_v1()

@fixture
def first_user(clear):
    return auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')

@fixture
def first_channel_public(clear):
    first_user = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    first_channel = channels_create_v1(first_user['auth_user_id'], 'new channel', True)
    return {'auth_id': first_user['auth_user_id'], 'channel_id': first_channel['channel_id']}

@fixture
def first_channel_private(clear):
    first_user = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    first_channel = channels_create_v1(first_user['auth_user_id'], 'new channel', False)
    return {'auth_id': first_user['auth_user_id'], 'channel_id': first_channel['channel_id']}

@fixture
def clear_flask():
    requests.delete(URL_clear)

@fixture
def first_user_flask(clear_flask):
    first_user_response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    return json.loads(first_user_response.text)

@fixture
def second_user_flask():
    second_user = requests.post(URL_auth_register, json={"email": "neweremail@gmail.com", 
    "password": "password", "name_first": "Jake", "name_last": "Smith"})
    return json.loads(second_user.text)

@fixture
def third_user_flask():
    third_user_response = requests.post(URL_auth_register, json={"email": "thirdemail@gmail.com", 
    "password": "example", "name_first": "Tom", "name_last": "Zombom"})
    return json.loads(third_user_response.text)

@fixture
def first_channel_public_flask(first_user_flask):
    first_channel_response = requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'], "name": 'new channel', "is_public": True})
    first_channel = json.loads(first_channel_response.text)
    return {
        "token": first_user_flask['token'], 
        "channel_id": first_channel['channel_id'],
        "user_id": first_user_flask['auth_user_id'],
    }

@fixture
def second_channel_public_flask(second_user_flask):
    second_channel_response = requests.post(URL_channels_create, 
    json={"token": second_user_flask['token'], "name": 'newer channel', "is_public": True})
    second_channel = json.loads(second_channel_response.text)
    return {
        "token": second_user_flask['token'], 
        "channel_id": second_channel['channel_id'],
        "user_id": second_user_flask['auth_user_id'],
    }
    
@fixture
def first_channel_private_flask(first_user_flask):
    first_channel_response = requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'], "name": 'new channel', "is_public": False})
    first_channel = json.loads(first_channel_response.text)
    return {
        "token": first_user_flask['token'], 
        "channel_id": first_channel['channel_id'],
        "auth_user_id": first_user_flask['auth_user_id'],
    }

@fixture
def second_channel_private_flask(second_user_flask):
    second_channel_response = requests.post(URL_channels_create, 
    json={"token": second_user_flask['token'], "name": 'newer channel', "is_public": False})
    second_channel = json.loads(second_channel_response.text)
    return {
        "token": second_user_flask['token'], 
        "channel_id": second_channel['channel_id'],
        "user_id": second_user_flask['auth_user_id'],
    }

@fixture
def second_member_in_channel_private_flask(first_channel_private_flask, second_user_flask):
    requests.post(URL_channel_invite, json={"token": first_channel_private_flask['token'], 
    "channel_id": first_channel_private_flask['channel_id'], "u_id": second_user_flask['auth_user_id']})
    return {
        "channel_id": first_channel_private_flask['channel_id'], 
        "token": first_channel_private_flask['token'], 
        "second_u_id": second_user_flask['auth_user_id']
    }

@fixture
def second_member_in_channel_public_flask(first_channel_public_flask, second_user_flask):
    requests.post(URL_channel_invite, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "u_id": second_user_flask['auth_user_id']})
    return {
        "channel_id": first_channel_public_flask['channel_id'],
        "token": first_channel_public_flask['token'],
        "first_u_id": first_channel_public_flask['user_id'],
        "second_u_id": second_user_flask['auth_user_id'],
        "second_token": second_user_flask['token']
    }

@fixture
def add_second_owner(second_member_in_channel_public_flask):
    requests.post(URL_channel_addowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask['second_u_id']})
    return {
        "second_member_id": second_member_in_channel_public_flask['second_u_id'], 
        "token": second_member_in_channel_public_flask['token'],
        "channel_id": second_member_in_channel_public_flask['channel_id'],
        "second_token": second_member_in_channel_public_flask['second_token']
    }

@fixture
def first_dm_flask(first_user_flask, second_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"]]})
    dm_id_dict = json.loads(response.text)
    return {
        "dm_id": dm_id_dict['dm_id'],
        "dm_name": "jakesmith, johnsmith",
        "first_token": first_user_flask['token'],
        "first_user_id": first_user_flask['auth_user_id'],
        "second_token": second_user_flask['token'],
        "second_user_id": second_user_flask['auth_user_id'],
    }

@fixture
def second_dm_flask(second_user_flask, third_user_flask):
    response = requests.post(URL_dm_create, json={"token": second_user_flask['token'], 
    "u_ids": [third_user_flask["auth_user_id"]]})
    dm_id_dict = json.loads(response.text)
    return {
        "dm_id": dm_id_dict['dm_id'],
        "dm_name": "johnsmith, tomzombom",
        "first_token": second_user_flask['token'],
        "first_user_id": second_user_flask['auth_user_id'],
        "second_token": third_user_flask['token'],
        "second_user_id": third_user_flask['auth_user_id'],
    }

@fixture
def first_dm_multiple_users_flask(first_user_flask, second_user_flask, third_user_flask):
    dm_response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask['auth_user_id'], third_user_flask['auth_user_id']]})
    first_dm = json.loads(dm_response.text)
    return {
        "token": first_user_flask['token'], 
        "dm_id": first_dm['dm_id'],
        "first_user_id": first_user_flask['auth_user_id'], 
        "second_user_id": second_user_flask['auth_user_id'],
        "second_user_token": second_user_flask['token'],
        "third_user_id": third_user_flask['auth_user_id'],
    }

@fixture
def first_dm_one_user_flask(first_user_flask):
    dm_response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": []})
    first_dm = json.loads(dm_response.text)
    return {
        "token": first_user_flask['token'], 
        "dm_id": first_dm['dm_id'],
        "first_user_id": first_user_flask['auth_user_id'],
    }

@fixture
def three_messages(first_channel_public_flask):
    message1 = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    message2 = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Better Message"})
    message3 = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Extraordinary Message"})
    time_now = int((datetime.datetime.now()).timestamp())
    return1 = json.loads(message1.text)
    return2 = json.loads(message2.text)
    return3 = json.loads(message3.text)
    return {
        "message1_ID": return1['message_id'],
        "message2_ID": return2['message_id'],
        "message3_ID": return3['message_id'],
        "token": first_channel_public_flask['token'],
        "user_id": first_channel_public_flask['user_id'],
        "c_id": first_channel_public_flask['channel_id'],
        "time_now": time_now,
    }

@fixture
def three_messages_two_users(first_channel_public_flask, second_user_flask):
    requests.post(URL_channel_invite, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "u_id": second_user_flask['auth_user_id']})
    message1 = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    message2 = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Better Message"})
    message3 = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Extraordinary Message"})
    time_now = int((datetime.datetime.now()).timestamp())
    return1 = json.loads(message1.text)
    return2 = json.loads(message2.text)
    return3 = json.loads(message3.text)
    return {
        "message1_ID": return1['message_id'],
        "message2_ID": return2['message_id'],
        "message3_ID": return3['message_id'],
        "first_token": first_channel_public_flask['token'],
        "second_token": second_user_flask['token'],
        "first_user_id": first_channel_public_flask['user_id'],
        "second_user_id": second_user_flask['auth_user_id'],
        "c_id": first_channel_public_flask['channel_id'],
        "time_now": time_now,
    }

@fixture
def three_dm_messages(first_dm_flask):
    message1 = requests.post(URL_message_senddm, json={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id'], "message" : "Good Message"})
    message2 = requests.post(URL_message_senddm, json={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id'], "message" : "Better Message"})
    message3 = requests.post(URL_message_senddm, json={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id'], "message" : "Extraordinary Message"})
    time_now = int((datetime.datetime.now()).timestamp())
    return1 = json.loads(message1.text)
    return2 = json.loads(message2.text)
    return3 = json.loads(message3.text)
    return {
        "message1_ID": return1['message_id'],
        "message2_ID": return2['message_id'],
        "message3_ID": return3['message_id'],
        "first_token": first_dm_flask['first_token'],
        "first_user_id": first_dm_flask['first_user_id'],
        "second_token": first_dm_flask['second_token'],
        "second_user_id": first_dm_flask['second_user_id'],
        "dm_id": first_dm_flask['dm_id'],
        "time_now": time_now,
    }

@fixture
def user_request_passwordreset(first_user_flask):
    requests.post(URL_passwordreset_request, json={'email': 'newemail@gmail.com'})

@fixture
def first_standup(second_member_in_channel_public_flask):
    response = requests.post(URL_standup_start, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "length" : 5})
    time_now = int((datetime.datetime.now()).timestamp())
    standup= json.loads(response.text)
    return {"channel_id": second_member_in_channel_public_flask['channel_id'],
        "token": second_member_in_channel_public_flask['token'],
        "first_u_id": second_member_in_channel_public_flask['first_u_id'],
        "second_u_id": second_member_in_channel_public_flask['second_u_id'],
        "second_token": second_member_in_channel_public_flask['second_token'],
        "time_now": time_now,
        "time_finish": standup["time_finish"]}
