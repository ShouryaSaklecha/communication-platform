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
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear, URL_users_all

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.get(URL_users_all, 
    params={'token': first_user_flask['token']})
    assert response.status_code == VALID_STATUS


def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.get(URL_users_all, 
    params={'token': (first_user_flask['token'] + '1')})
    assert response.status_code == ACCESS_ERROR


def test_VALID_STATUS_correct_output_one_user(first_user_flask):
    response = requests.get(URL_users_all, 
    params={'token': first_user_flask['token']})
    correct_output = {'users': [{
                'u_id': first_user_flask['auth_user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }]}
    
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_many_users(first_user_flask):
    second_user_response = requests.post(URL_auth_register, json={"email": "secondemail@gmail.com", 
    "password": "password", "name_first": "Matilda", "name_last": "Smith"})
    second_user = json.loads(second_user_response.text)
    
    third_user_response = requests.post(URL_auth_register, json={"email": "thirdemail@gmail.com", 
    "password": "password", "name_first": "Amy", "name_last": "Smith"})
    third_user = json.loads(third_user_response.text)
    
    fourth_user_response = requests.post(URL_auth_register, json={"email": "fourthemail@gmail.com", 
    "password": "password", "name_first": "Greg", "name_last": "Smith"})
    fourth_user = json.loads(fourth_user_response.text)

    response = requests.get(URL_users_all, 
    params={'token': first_user_flask['token']})
    
    correct_output = {'users': [{
                'u_id': first_user_flask['auth_user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }, {
                'u_id': second_user['auth_user_id'],
                'email': 'secondemail@gmail.com',
                'name_first': 'Matilda',
                'name_last': 'Smith',
                'handle_str': 'matildasmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }, {
                'u_id': third_user['auth_user_id'],
                'email': 'thirdemail@gmail.com',
                'name_first': 'Amy',
                'name_last': 'Smith',
                'handle_str': 'amysmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }, {
                'u_id': fourth_user['auth_user_id'],
                'email': 'fourthemail@gmail.com',
                'name_first': 'Greg',
                'name_last': 'Smith',
                'handle_str': 'gregsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            }]}
    


    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS
