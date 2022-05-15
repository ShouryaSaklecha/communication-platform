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
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear, URL_users_all, URL_user_profile

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.get(URL_user_profile, 
    params={'token': first_user_flask['token'], 'u_id': first_user_flask['auth_user_id']})
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.get(URL_user_profile, 
    params={'token': (first_user_flask['token'] + '1'), 'u_id': first_user_flask['auth_user_id']})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_u_id(first_user_flask):
    response = requests.get(URL_user_profile, 
    params={'token': (first_user_flask['token']), 'u_id': (first_user_flask['auth_user_id'] + 1)})
    assert response.status_code == INPUT_ERROR

def test_VALID_STATUS_correct_output(first_user_flask):
    response = requests.get(URL_user_profile, 
    params={'token': first_user_flask['token'], 'u_id': first_user_flask['auth_user_id']})
    correct_output = {'user': {'u_id': first_user_flask['auth_user_id'],
                               'email': 'newemail@gmail.com',
                               'name_first': 'John',
                               'name_last': 'Smith',
                               'handle_str': 'johnsmith',
                               'profile_img_url': GENERIC_PROFILE_URL,
                                }
                    }
    
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_other_user(first_user_flask, second_user_flask):
    response = requests.get(URL_user_profile, 
    params={'token': first_user_flask['token'], 'u_id': second_user_flask['auth_user_id']})
    
    correct_output = {'user': {'u_id': second_user_flask['auth_user_id'],
                               'email': "neweremail@gmail.com",
                               'name_first': "Jake", 
                               'name_last': "Smith",
                               'handle_str': 'jakesmith',
                               'profile_img_url': GENERIC_PROFILE_URL,
                               }
                    }
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS
