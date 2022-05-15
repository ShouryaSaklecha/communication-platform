from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_join_v1
from src.error import InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1
from tests.routes_test import URL_admin_permission_change, URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear

def test_VALID_STATUS_valid_request(first_user_flask, second_user_flask):
    response = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"], "permission_id": 1})
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(first_user_flask, second_user_flask):
    response = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'] + '1',
    "u_id": second_user_flask["auth_user_id"], "permission_id": 1})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_not_global_owner(first_user_flask, second_user_flask):
    third_user = requests.post(URL_auth_register, json={"email": "newereremail@gmail.com", 
    "password": "password", "name_first": "Jake", "name_last": "Smith"})
    third_user_response = json.loads(third_user.text)
    response = requests.post(URL_admin_permission_change, json={"token": second_user_flask['token'],
    "u_id": third_user_response["auth_user_id"], "permission_id": 1})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_user(first_user_flask, second_user_flask):
    response = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"] + 1, "permission_id": 1})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_global_owner(first_user_flask):
    response = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": first_user_flask["auth_user_id"], "permission_id": 2})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_permission(first_user_flask, second_user_flask):
    response = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"], "permission_id": 3})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_same_permissions(first_user_flask, second_user_flask):
    response = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"], "permission_id": 2})
    assert response.status_code == INPUT_ERROR

def test_VALID_STATUS_changes_permission(first_user_flask, second_user_flask):
    response1 = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"], "permission_id": 1})
    assert response1.status_code == VALID_STATUS
    response2 = requests.post(URL_admin_permission_change, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"], "permission_id": 1})
    assert response2.status_code == INPUT_ERROR