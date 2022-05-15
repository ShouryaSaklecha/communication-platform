from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1, GENERIC_PROFILE_URL
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear, URL_channel_addowner, URL_channel_invite


def test_VALID_STATUS_valid_request_private(second_member_in_channel_private_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_private_flask['token'], 
    "channel_id": second_member_in_channel_private_flask['channel_id'], "u_id": second_member_in_channel_private_flask["second_u_id"]})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_valid_request_public(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["second_u_id"]})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_output_correct_private(second_member_in_channel_private_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_private_flask['token'], 
    "channel_id": second_member_in_channel_private_flask['channel_id'], "u_id": second_member_in_channel_private_flask["second_u_id"]})
    details_response = requests.get(URL_channel_details, 
    params={'token': second_member_in_channel_private_flask['token'], 'channel_id': second_member_in_channel_private_flask['channel_id']})
    
    correct_output = {
        'name': 'new channel',
        'is_public': False,
        'owner_members': [
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


def test_VALID_STATUS_output_correct_public(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["second_u_id"]})
    details_response = requests.get(URL_channel_details, 
    params={'token': second_member_in_channel_public_flask['token'], 'channel_id': second_member_in_channel_public_flask['channel_id']})
    
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
            {
                'u_id': 1,
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }
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

def test_ACCESS_ERROR_invalid_token(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_public_flask['token'] + '1', 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["second_u_id"]})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_user_not_owner(second_member_in_channel_public_flask, third_user_flask):
    requests.post(URL_channel_invite, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": third_user_flask['auth_user_id']})
    response = requests.post(URL_channel_addowner, json={"token": third_user_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["second_u_id"]})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_channel(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'] + 1, "u_id": second_member_in_channel_public_flask["second_u_id"]})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_user(second_member_in_channel_public_flask):
    response = requests.post(URL_channel_addowner, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "u_id": second_member_in_channel_public_flask["second_u_id"] + second_member_in_channel_public_flask["first_u_id"] + 1})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_not_a_member(first_channel_private_flask, second_user_flask):
    response = requests.post(URL_channel_addowner, json={"token": first_channel_private_flask['token'], 
    "channel_id": first_channel_private_flask['channel_id'], "u_id": second_user_flask["auth_user_id"]})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_repeat_owner(first_channel_private_flask):
    response = requests.post(URL_channel_addowner, json={"token": first_channel_private_flask['token'], 
    "channel_id": first_channel_private_flask['channel_id'], "u_id": first_channel_private_flask["auth_user_id"]})
    assert response.status_code == INPUT_ERROR
