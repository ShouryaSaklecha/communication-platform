from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1, OWNER_PERMISSION, MEMBER_PERMISSION, GENERIC_PROFILE_URL
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear
#from tests.fixtures_test import clear, first_user, first_channel_public, first_channel_private, clear_flask, first_user_flask, first_channel_public_flask, first_channel_private_flask

def test_INPUT_ERROR_channel_not_valid(first_user_flask):
    response = requests.get(URL_channel_details, 
    params={'token': first_user_flask['token'], 'channel_id': -1})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_non_member_token_public(first_channel_public_flask):
    not_member_response = requests.post(URL_auth_register, json={"email": "notmember@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    not_member = json.loads(not_member_response.text)
    response = requests.get(URL_channel_details, 
    params={'token': not_member['token'], 'channel_id': first_channel_public_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_non_member_token_private(first_channel_private_flask):
    not_member_response = requests.post(URL_auth_register, json={"email": "notmember@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    not_member = json.loads(not_member_response.text)
    response = requests.get(URL_channel_details,
    params={'token': not_member['token'], 'channel_id': first_channel_private_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token_public(first_channel_public_flask):
    response = requests.get(URL_channel_details, 
    params={'token': (first_channel_public_flask['token'] + '1'), 'channel_id': first_channel_public_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token_private(first_channel_private_flask):
    response = requests.get(URL_channel_details, 
    params={'token': (first_channel_private_flask['token'] + '1'), 'channel_id': first_channel_private_flask['channel_id']})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_output_correct(first_channel_public_flask):
    response = requests.get(URL_channel_details, 
    params={'token': first_channel_public_flask['token'], 'channel_id': first_channel_public_flask['channel_id']})
    
    details = {
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
            }
        ],
    }
    
    assert json.loads(response.text) == details
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_valid_details_request_public(first_channel_public_flask):
    response = requests.get(URL_channel_details, 
    params={'token': first_channel_public_flask['token'], 'channel_id': first_channel_public_flask['channel_id']})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_valid_details_request_private(first_channel_private_flask):
    response = requests.get(URL_channel_details, 
    params={'token': first_channel_private_flask['token'], 'channel_id': first_channel_private_flask['channel_id']})
    assert response.status_code == VALID_STATUS
