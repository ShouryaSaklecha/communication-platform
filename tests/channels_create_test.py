from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1
from tests.routes_test import URL_auth_register, URL_auth_login, URL_channel_details, URL_channels_create, URL_clear

def test_INPUT_ERROR_channel_name_long(first_user_flask):
    response = requests.post(URL_channels_create, json={"token": first_user_flask['token'], 
    "name": 'thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong', "is_public": True})
    assert response.status_code == INPUT_ERROR
    response = requests.post(URL_channels_create, json={"token": first_user_flask['token'], 
    "name": 'thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong', "is_public": False})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_channel_name_size_short(first_user_flask):
    response = requests.post(URL_channels_create, json={"token": first_user_flask['token'], 
    "name": '', "is_public": True})
    assert response.status_code == INPUT_ERROR
    response = requests.post(URL_channels_create, json={"token": first_user_flask['token'], 
    "name": '', "is_public": False})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_channel_invalid_token(first_user_flask):
    response = requests.post(URL_channels_create, json={"token": (first_user_flask['token'] + "1"), 
    "name": 'channel_name', "is_public": True})
    assert response.status_code == ACCESS_ERROR
    response = requests.post(URL_channels_create, json={"token": (first_user_flask['token'] + "1"), 
     "name": 'channel_name', "is_public": False})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.post(URL_channels_create, json={"token": first_user_flask['token'], 
    "name": 'channel_name_public', "is_public": True})
    assert response.status_code == VALID_STATUS
    response = requests.post(URL_channels_create, json={"token": first_user_flask['token'], 
    "name": 'channel_name_private', "is_public": False})
    assert response.status_code == VALID_STATUS   


'''OLD TESTS
@fixture
def clear():
    clear_v1()

@fixture
def first_user(clear):
    return auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    def test_channel_name_long(first_user):
    with pytest.raises(InputError):
        channels_create_v1(first_user['auth_user_id'], 'thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong', True)
    with pytest.raises(InputError):
        channels_create_v1(first_user['auth_user_id'], 'thisnameiswayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyytoolong', False)

def test_channel_name_short(first_user):
    with pytest.raises(InputError):
        channels_create_v1(first_user['auth_user_id'], '', True)
    with pytest.raises(InputError):
        channels_create_v1(first_user['auth_user_id'], '', False)

def test_creator_in_channel(first_user):
    user_id = first_user['auth_user_id']
    new_channel = channels_create_v1(user_id, 'new channel', True)
    new_channel_id = new_channel['channel_id']
    new_channel_details = channel_details_v1(user_id, new_channel_id)
    new_channel_owner_list = new_channel_details['owner_members']
    new_channel_owner = new_channel_owner_list[0]

    assert user_id == new_channel_owner['u_id']

def test_channel_without_user(clear):
    with pytest.raises(AccessError):
        channels_create_v1(-1, 'new channel', True)
    with pytest.raises(AccessError):
        channels_create_v1(-1, 'new channel', False)
        
'''   