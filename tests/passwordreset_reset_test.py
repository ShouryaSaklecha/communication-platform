from pytest import fixture
import pytest
import requests
import json
from src.data_store import data_store
from tests.routes_test import URL_auth_register, URL_auth_login, URL_users_all, URL_passwordreset_request, URL_passwordreset_reset
from src.error import AccessError, InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS

def test_INPUT_ERROR_invalidcode(user_request_passwordreset):
    response = requests.post(URL_passwordreset_reset, json={'reset_code': '1212121212', 'new_password': 'validpassword'})
    assert response.status_code == INPUT_ERROR

# had to access data store to ensure the code is valid and only the password is causing the problem
def test_INPUT_ERROR_invalidpassword(user_request_passwordreset):
    store = data_store.get()
    stored_codes = store['codes']
    current_code = stored_codes[0]
    valid_code = current_code['code']
    response = requests.post(URL_passwordreset_reset, json={'reset_code': valid_code, 'new_password': 'short'})
    assert response.status_code == INPUT_ERROR

# had to access data store to ensure code is valid and request is valid.
def test_VALID_STATUS_validrequest(user_request_passwordreset):
    store = data_store.get()
    stored_codes = store['codes']
    current_code = stored_codes[0]
    valid_code = current_code['code']
    response = requests.post(URL_passwordreset_reset, json={'reset_code': valid_code, 'new_password': 'validpassword'})
    assert response.status_code == VALID_STATUS
    response = requests.post(URL_auth_login, json={"email": "newemail@gmail.com",
    "password": "validpassword"})
    assert response.status_code == VALID_STATUS
