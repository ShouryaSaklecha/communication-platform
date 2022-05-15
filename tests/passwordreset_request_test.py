from pytest import fixture
import pytest
import requests
import json
from tests.routes_test import URL_auth_register, URL_auth_login, URL_users_all, URL_passwordreset_request, URL_clear
from src.error import AccessError, InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS

def test_VALID_STATUS_resetrequest(first_user_flask):
    response = requests.post(URL_passwordreset_request, json={'email': 'newemail@gmail.com'})
    assert response.status_code == VALID_STATUS
    response = requests.post(URL_passwordreset_request, json={'email': 'fakeemail@gmail.com'})
    assert response.status_code == VALID_STATUS

def test_logged_out_user(first_user_flask):
    response = requests.post(URL_passwordreset_request, json={'email': 'newemail@gmail.com'})
    assert response.status_code == VALID_STATUS
    response = requests.get(URL_users_all, 
    params={'token': (first_user_flask['token'])})
    assert response.status_code == ACCESS_ERROR