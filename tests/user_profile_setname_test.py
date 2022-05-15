from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1, OWNER_PERMISSION, GENERIC_PROFILE_URL
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear, URL_users_all, URL_user_profile_setemail, URL_user_profile_setname, URL_user_profile_sethandle

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'], 
    "name_first": 'Frank', "name_last": 'Newname'})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_output_correct(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'], 
    "name_first": 'Frank', "name_last": 'Newname'})
    users_all_response = requests.get(URL_users_all, 
    params={'token': first_user_flask['token']})
    correct_output = {'users': [{
                'u_id': first_user_flask['auth_user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'Frank',
                'name_last': 'Newname',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }]}
    
    assert json.loads(users_all_response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'] + '1', 
    "name_first": 'Frank', "name_last": 'Newname'})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_first_name_too_long(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'], 
    "name_first": 'thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong', "name_last": 'Newname'})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_first_name_too_short(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'], 
    "name_first": '', "name_last": 'Newname'})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_last_name_too_long(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'], 
    "name_first": 'Frank', "name_last": 'thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong'})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_last_name_too_short(first_user_flask):
    response = requests.put(URL_user_profile_setname, json={"token": first_user_flask['token'], 
    "name_first": 'Frank', "name_last": ''})
    assert response.status_code == INPUT_ERROR