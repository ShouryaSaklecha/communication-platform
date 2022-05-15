from pytest import fixture
import pytest
import requests
import json
from src import config
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_dm_create, URL_dm_leave, URL_dm_list, URL_dm_remove

def test_INPUT_ERROR_invalid_dm_id(first_dm_flask):
    response = requests.delete(URL_dm_remove, json={"token": first_dm_flask['first_token'], 
    "dm_id": (first_dm_flask['dm_id'] + 1)})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_user_not_creator(first_dm_flask):
    response = requests.delete(URL_dm_remove, json={"token": first_dm_flask['second_token'], 
    "dm_id": first_dm_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_user_not_in_dm(first_dm_flask):
    response_leave = requests.post(URL_dm_leave, json={"token": first_dm_flask['second_token'], 
    "dm_id": first_dm_flask['dm_id']})
    assert response_leave.status_code == VALID_STATUS
    response = requests.delete(URL_dm_remove, json={"token": first_dm_flask['second_token'], 
    "dm_id": first_dm_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(first_dm_flask):
    response = requests.delete(URL_dm_remove, json={"token": (first_dm_flask['second_token'] + '1'), 
    "dm_id": first_dm_flask['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_creator_dm_remove(first_dm_flask):
    requests.post(URL_dm_create, json={"token": first_dm_flask['first_token'], 
    "u_ids": first_dm_flask["second_user_id"]})
    response = requests.delete(URL_dm_remove, json={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id']})
    response_list = requests.get(URL_dm_list, 
    params={'token': first_dm_flask['first_token']})

    details = {
        'dms': []
    }

    assert json.loads(response_list.text) == details
    assert response.status_code == VALID_STATUS