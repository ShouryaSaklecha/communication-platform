from urllib import response
from pytest import fixture
import pytest
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1
import requests
import json
from src import config
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear

def test_INPUT_ERROR_no_users(clear_flask):
    response = requests.post(URL_auth_login, json={"email": "whyamiloggingin@gmail.com",
    "password": "nopassword"})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_wrong_email(clear_flask):
    requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    response = requests.post(URL_auth_login, json={"email": "falseemail@gmail.com",
    "password": "nopassword"})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_password_incorrect(clear_flask):
    requests.post(URL_auth_register, json={"email": "neweremail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    response = requests.post(URL_auth_login, json={"email": "neweremail@gmail.com",
    "password": "wrongpassword"})
    assert response.status_code == INPUT_ERROR

def test_VALID_STATUS_valid_request(clear_flask):
    requests.post(URL_auth_register, json={"email": "neweremail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    response = requests.post(URL_auth_login, json={"email": "neweremail@gmail.com",
    "password": "password"})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_returns_correct(clear_flask):
    auth_response = requests.post(URL_auth_register, json={"email": "neweremail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    login_response = requests.post(URL_auth_login, json={"email": "neweremail@gmail.com",
    "password": "password"})
    auth_data = json.loads(auth_response.text)
    login_data = json.loads(login_response.text)
    assert login_data['auth_user_id'] == auth_data['auth_user_id']
