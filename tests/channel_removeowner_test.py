from audioop import add
from urllib import response
from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_join_v1, channel_addowner_v1
from src.error import InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1, GENERIC_PROFILE_URL
from tests.routes_test import URL_auth_register, URL_channel_details, URL_channel_removeowner, URL_channel_invite, URL_channels_create, URL_clear, URL_channel_addowner

def test_VALID_STATUS_valid_request(add_second_owner):
    response = requests.post(URL_channel_removeowner, json={"token": add_second_owner['token'],
    "channel_id": add_second_owner["channel_id"], "u_id": add_second_owner["second_member_id"]})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_removes_owner(add_second_owner):
    response1 = requests.post(URL_channel_removeowner, json={"token": add_second_owner['token'],
    "channel_id": add_second_owner["channel_id"], "u_id": add_second_owner["second_member_id"]})
    assert response1.status_code == VALID_STATUS
    response2 = requests.post(URL_channel_addowner, json={"token": add_second_owner['token'], 
    "channel_id": add_second_owner["channel_id"], "u_id": add_second_owner["second_member_id"]})
    assert response2.status_code == VALID_STATUS

def test_VALID_STATUS_output_correct(add_second_owner):
    response = requests.post(URL_channel_removeowner, json={"token": add_second_owner['token'], 
    "channel_id": add_second_owner['channel_id'], "u_id": add_second_owner["second_member_id"]})
    details_response = requests.get(URL_channel_details, 
    params={'token': add_second_owner['token'], 'channel_id': add_second_owner['channel_id']})
    
    correct_output = {
        'name': 'new channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': 0,
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
        ],
        'all_members': [
            {
                'u_id': 0,
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
            {
                'u_id': 1,
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }
        ],
    }

    assert json.loads(details_response.text) == correct_output
    
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(add_second_owner):
    response1 = requests.post(URL_channel_removeowner, json={"token": add_second_owner['token'] + '1',
    "channel_id": add_second_owner["channel_id"], "u_id": add_second_owner["second_member_id"]})
    assert response1.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_noowner_permissions(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_removeowner, json={"token": second_member_in_channel_public_flask['second_token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["first_u_id"]})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_channelid(add_second_owner):
    response = requests.post(URL_channel_removeowner, json={"token": add_second_owner['token'],
    "channel_id": add_second_owner["channel_id"] + 1, "u_id": add_second_owner["second_member_id"]})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_userid(add_second_owner):
    response = requests.post(URL_channel_removeowner, json={"token": add_second_owner['token'],
    "channel_id": add_second_owner["channel_id"], "u_id": add_second_owner["second_member_id"] + 1})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_notowner(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_removeowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["second_u_id"]})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_onlyowner(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_removeowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["first_u_id"]})
    assert response.status_code == INPUT_ERROR
