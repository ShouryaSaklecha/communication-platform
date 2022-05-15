from tests.conftest import first_dm_multiple_users_flask
from urllib import request, response
from pytest import fixture
import pytest
import json
import requests
from src.error import ACCESS_ERROR, AccessError, VALID_STATUS
from tests.routes_test import URL_dm_list, URL_dm_create

def test_ACCESS_ERROR_invalid_token(first_user_flask, first_dm_multiple_users_flask):
    response = requests.get(URL_dm_list,
    params={'token': first_user_flask['token'] + '1'})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_one_dm(first_dm_multiple_users_flask):
    response = requests.get(URL_dm_list,
    params={'token': first_dm_multiple_users_flask['token']})
    details = {
        'dms': [
            {
        		'dm_id': first_dm_multiple_users_flask['dm_id'],
        		'name': 'jakesmith, johnsmith, tomzombom',
        	}
        ]
    }
    assert json.loads(response.text) == details
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_many_dm(first_user_flask, second_user_flask, third_user_flask):
    first_dm_response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"], third_user_flask["auth_user_id"]]})
    first_dm = json.loads(first_dm_response.text)
    second_dm_response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": []})
    second_dm = json.loads(second_dm_response.text)
    third_dm_response = requests.post(URL_dm_create, json={"token": second_user_flask['token'], 
    "u_ids": [first_user_flask["auth_user_id"], third_user_flask["auth_user_id"]]})
    third_dm = json.loads(third_dm_response.text)
    
    correct_output = {
        'dms': [
        	{
        		'dm_id': first_dm['dm_id'],
        		'name': 'jakesmith, johnsmith, tomzombom',
        	},
            {
                'dm_id': second_dm['dm_id'],
        		'name': 'johnsmith',
            },
            {
                'dm_id': third_dm['dm_id'],
        		'name': 'jakesmith, johnsmith, tomzombom',
            }
        ]
    }
    response = requests.get(URL_dm_list,
    params={'token': first_user_flask['token']})
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_no_dm(first_user_flask):
    response = requests.get(URL_dm_list,
    params={'token': first_user_flask['token']})
    correct_output = {'dms': []}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS