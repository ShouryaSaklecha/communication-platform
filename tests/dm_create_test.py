from pytest import fixture
import pytest
import requests
import json
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_dm_create

def test_VALID_STATUS_valid_request(first_user_flask, second_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"]]})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_only_owner(first_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": []})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_more_users(first_user_flask, second_user_flask, third_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"], third_user_flask["auth_user_id"]]})
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(first_user_flask, second_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'] + '1', 
    "u_ids": [second_user_flask["auth_user_id"]]})
    assert response.status_code == ACCESS_ERROR
    
def test_INPUT_ERROR_duplicate_u_id(first_user_flask, second_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"], second_user_flask["auth_user_id"]]})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_u_id_invalid(first_user_flask, second_user_flask):
    response = requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [(second_user_flask["auth_user_id"] + 1)]})
    assert response.status_code == INPUT_ERROR
