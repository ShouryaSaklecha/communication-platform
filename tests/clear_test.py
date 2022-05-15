from pytest import fixture
import pytest
import requests
import json
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear

def test_VALID_STATUS_removed_user_by_checking_duplicate():
    requests.delete(URL_clear)
    requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    requests.delete(URL_clear)
    duplicate_user_response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    assert duplicate_user_response.status_code == VALID_STATUS


def test_VALID_STATUS_removed_channel_by_checking_c_id():
    requests.delete(URL_clear)
    first_user_response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    first_user = json.loads(first_user_response.text)
    first_channel_response = requests.post(URL_channels_create, 
    json={"token": first_user['token'], "name": 'new channel', "is_public": False})
    first_channel = json.loads(first_channel_response.text)
    requests.delete(URL_clear)
    duplicate_user_response = requests.post(URL_auth_register, json={"email": "newemail@gmail.com", 
    "password": "password", "name_first": "John", "name_last": "Smith"})
    duplicate_user = json.loads(duplicate_user_response.text)
    duplicate_channel_response = requests.post(URL_channels_create, 
    json={"token": duplicate_user['token'], "name": 'new channel', "is_public": False})
    duplicate_channel = json.loads(duplicate_channel_response.text)
    assert first_channel['channel_id'] == duplicate_channel['channel_id']


'''OLD TESTS
def test_removed_user():
    clear_v1()
    auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    login_returns1 = auth_login_v1('newemail@gmail.com', 'password')
    auth_user_id_1 = login_returns1['auth_user_id']
    clear_v1()
    auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    login_returns2 = auth_login_v1('newemail@gmail.com', 'password')
    auth_user_id_2 = login_returns2['auth_user_id']

    assert auth_user_id_2 == auth_user_id_1

def test_removed_channel():
    clear_v1()
    register_returns1 = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    auth_user_id1 = register_returns1['auth_user_id']
    new_channel1 = channels_create_v1(auth_user_id1, 'new channel', 1)
    new_channel_id1 = new_channel1['channel_id']
    clear_v1()
    register_returns2 = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    auth_user_id2 = register_returns2['auth_user_id']
    new_channel2 = channels_create_v1(auth_user_id2, 'new channel', 1)
    new_channel_id2 = new_channel2['channel_id']
    assert new_channel_id1 == new_channel_id2
    '''