from pytest import fixture
import pytest
import requests
import json
from src import config
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import GENERIC_PROFILE_URL
from tests.routes_test import URL_dm_leave, URL_dm_details

def test_INPUT_ERROR_invalid_dm_id(first_dm_flask):
    response = requests.post(URL_dm_leave, json={"token": first_dm_flask['first_token'], 
    "dm_id": (first_dm_flask['dm_id'] + 1)})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_user_not_in_dm(first_dm_flask, third_user_flask):
    response = requests.post(URL_dm_leave, json={"token": third_user_flask['token'], 
    "dm_id": first_dm_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(first_dm_flask):
    response = requests.post(URL_dm_leave, json={"token": (first_dm_flask['second_token']
     + first_dm_flask['first_token'] + '1'), 
    "dm_id": first_dm_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_member_leave(first_dm_flask):
    response = requests.post(URL_dm_leave, json={"token": first_dm_flask['second_token'], 
    "dm_id": first_dm_flask['dm_id']})
    response_dm_details = requests.get(URL_dm_details, params={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id']})

    details = {
        "name": 'jakesmith, johnsmith',
        "members": [
            {
                'u_id': first_dm_flask['first_user_id'],
                'email': 'newemail@gmail.com',
                'name_first': 'John',
                'name_last': 'Smith',
                'handle_str': 'johnsmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
        ],
    }

    assert json.loads(response_dm_details.text) == details
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_creator_leave(first_dm_flask):
    response = requests.post(URL_dm_leave, json={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id']})
    response_dm_details = requests.get(URL_dm_details, params={"token": first_dm_flask['second_token'], 
    "dm_id": first_dm_flask['dm_id']})

    details = {
        "name": 'jakesmith, johnsmith',
        "members": [
            {
                'u_id': first_dm_flask['second_user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
        ],
    }

    assert json.loads(response_dm_details.text) == details
    assert response.status_code == VALID_STATUS
