from pytest import fixture
import pytest
import requests
import json
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1, channel_details_v1
from tests.routes_test import URL_auth_register, URL_channel_details, URL_channels_create
from tests.routes_test import  URL_clear, URL_channel_join
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1, OWNER_PERMISSION, MEMBER_PERMISSION, GENERIC_PROFILE_URL
from src import config

def test_INPUT_ERROR_invalid_channel_id(first_channel_public_flask, second_user_flask):
    response = requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": (first_channel_public_flask['channel_id'] + 1)})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_user_in_channel(first_channel_public_flask):
    response = requests.post(URL_channel_join, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_private_channel(first_channel_private_flask, second_user_flask):
    response = requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_private_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACSESS_ERROR_invalid_token(first_channel_public_flask, second_user_flask):
    response = requests.post(URL_channel_join, json={"token": (second_user_flask['token'] 
    + first_channel_public_flask['token'] + '1'), 
    "channel_id": first_channel_public_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_user_join(first_channel_public_flask, second_user_flask):
    response_channel_join = requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    response_channel_details = requests.get(URL_channel_details, 
    params={'token': second_user_flask['token'],
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
            {
                'u_id': second_user_flask['auth_user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }
        ],
    }

    assert json.loads(response_channel_details.text) == details
    assert response_channel_join.status_code == VALID_STATUS
