from pytest import fixture
import pytest
import requests
import json
from tests.routes_test import URL_auth_register, URL_channel_details, URL_channels_create
from tests.routes_test import  URL_clear, URL_channel_invite, URL_channel_leave
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1, OWNER_PERMISSION, MEMBER_PERMISSION, GENERIC_PROFILE_URL
from src import config
    
def test_INPUT_ERROR_invalid_channel_id(first_channel_public_flask):
    response = requests.post(URL_channel_leave, json={"token": first_channel_public_flask['token'], 
    "channel_id": (first_channel_public_flask['channel_id'] + 1)})
    assert response.status_code == INPUT_ERROR

def test_ACSESS_ERROR_user_not_in_channel(first_channel_public_flask, second_user_flask):
    response = requests.post(URL_channel_leave, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACSESS_ERROR_invalid_user_token(first_channel_public_flask):
    response = requests.post(URL_channel_leave, json={"token": (first_channel_public_flask['token'] + '1'), 
    "channel_id": first_channel_public_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_second_user_leave(first_channel_public_flask, second_user_flask):
    requests.post(URL_channel_invite, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "u_id": second_user_flask['auth_user_id']})
    response_channel_leave = requests.post(URL_channel_leave, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    response_channel_details = requests.get(URL_channel_details,
    params={'token': first_channel_public_flask['token'],
    'channel_id': first_channel_public_flask['channel_id']})
    
    details = {
        'name': 'new channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': first_channel_public_flask['user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }
        ],
        'all_members': [
            {
                'u_id': first_channel_public_flask['user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
        ],
    }

    assert json.loads(response_channel_details.text) == details
    assert response_channel_leave.status_code == VALID_STATUS

def test_VALID_STATUS_owner_leave(first_channel_public_flask, second_user_flask):
    requests.post(URL_channel_invite, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "u_id": second_user_flask['auth_user_id']})
    response_channel_leave = requests.post(URL_channel_leave, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    response_channel_details = requests.get(URL_channel_details,
    params={'token': second_user_flask['token'],
    'channel_id': first_channel_public_flask['channel_id']})
    
    details = {
        'name': 'new channel',
        'is_public': True,
        'owner_members': [],
        'all_members': [
            {
                'u_id': second_user_flask['auth_user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
        ],
    }

    assert json.loads(response_channel_details.text) == details
    assert response_channel_leave.status_code == VALID_STATUS
