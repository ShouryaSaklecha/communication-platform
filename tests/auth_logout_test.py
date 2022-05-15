from pytest import fixture
import pytest
import requests
import json
from tests.routes_test import URL_auth_register, URL_auth_login, URL_auth_logout, URL_clear
from src.error import AccessError, InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.post(URL_auth_logout, json={'token': first_user_flask['token']})
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.post(URL_auth_logout, json={'token': first_user_flask['token'] + '1'})
    assert response.status_code == ACCESS_ERROR

def test_invalidates_1session_token(first_user_flask):
    response1 = requests.post(URL_auth_logout, json={'token': first_user_flask['token']})
    assert response1.status_code == VALID_STATUS
    response2 = requests.post(URL_auth_logout, json={'token': first_user_flask['token']})
    assert response2.status_code == ACCESS_ERROR

def test_invalidates_2session_token(first_user_flask):
    response1 = requests.post(URL_auth_logout, json={'token': first_user_flask['token']})
    assert response1.status_code == VALID_STATUS
    login_response = requests.post(URL_auth_login, json={"email": "newemail@gmail.com",
     "password": "password"})
    login_data = json.loads(login_response.text)
    response2 = requests.post(URL_auth_logout, json={'token': login_data['token']})
    assert response2.status_code == VALID_STATUS