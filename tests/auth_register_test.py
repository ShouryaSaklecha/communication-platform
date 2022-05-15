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
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear

def test_VALID_STATUS_valid_request(clear_flask):
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    assert  response.status_code == VALID_STATUS

def test_INPUT_ERROR_invalid_email(clear_flask):
    response = requests.post(URL_auth_register, json={"email": "bademail", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    assert  response.status_code == INPUT_ERROR

def test_INPUT_ERROR_duplicate_email(clear_flask):
    requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    assert  response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_password(clear_flask):
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "small", "name_first": "John", "name_last": "Smith"})
    assert  response.status_code == INPUT_ERROR

def test_INPUT_ERROR_firstname_size(clear_flask):
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "", "name_last": "Smith"})
    assert  response.status_code == INPUT_ERROR
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong",
    "name_last": "Smith"})
    assert  response.status_code == INPUT_ERROR

def test_INPUT_ERROR_lastname_size(clear_flask):
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": ""})
    assert  response.status_code == INPUT_ERROR
    response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John",
    "name_last": "thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong"})
    assert  response.status_code == INPUT_ERROR

def test_VALID_STATUS_returns_correct(clear_flask):
    calling_auth = requests.post(URL_auth_register, json={"email": "neweremail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    calling_login = requests.post(URL_auth_login, json={"email": "neweremail@gmail.com", 
    "password": "password"})
    response_auth = json.loads(calling_auth.text)
    response_login = json.loads(calling_login.text)
    assert  response_auth['auth_user_id'] == response_login['auth_user_id']
