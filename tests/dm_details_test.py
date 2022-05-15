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
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear, URL_dm_details

def test_INPUT_ERROR_dm_not_valid(first_user_flask):
    response = requests.get(URL_dm_details, 
    params={'token': first_user_flask['token'], 'dm_id': -1})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_non_member_token(first_dm_one_user_flask, second_user_flask):
    response = requests.get(URL_dm_details, 
    params={'token': second_user_flask['token'], 'dm_id': first_dm_one_user_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(first_dm_one_user_flask):
    response = requests.get(URL_dm_details, 
    params={'token': (first_dm_one_user_flask['token'] + '1'), 'dm_id': first_dm_one_user_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_output_correct_one_user(first_dm_one_user_flask):
    response = requests.get(URL_dm_details, 
    params={'token': first_dm_one_user_flask['token'], 'dm_id': first_dm_one_user_flask['dm_id']})
    
    correct_output = {
        'name': 'johnsmith',
        'members': [
            {
                'u_id': first_dm_one_user_flask['first_user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }
        ]
    }
    
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_output_correct_multiple_users(first_dm_multiple_users_flask):
    response = requests.get(URL_dm_details, 
    params={'token': first_dm_multiple_users_flask['token'], 'dm_id': first_dm_multiple_users_flask['dm_id']})
    
    correct_output = {
        'name': 'jakesmith, johnsmith, tomzombom',
        'members': [
            {
                'u_id': first_dm_multiple_users_flask['first_user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }, {
                'u_id': first_dm_multiple_users_flask['second_user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }, {
                'u_id': first_dm_multiple_users_flask['third_user_id'],
                'email': 'thirdemail@gmail.com',
                'name_first': 'Tom',
                'name_last': 'Zombom',
                'handle_str': 'tomzombom',
                'profile_img_url': GENERIC_PROFILE_URL,
            }
        ]
    }
    
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS