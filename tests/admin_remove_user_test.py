from src.admin import check_user_valid
from pytest import fixture
import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_join_v1
from src.admin import admin_remove_user_v1
from src.error import InputError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import clear_v1
from tests.routes_test import URL_admin_removeuser, URL_channel_messages, URL_auth_register, URL_channel_join, URL_channel_details, URL_message_send, URL_clear

def test_ACCESS_ERROR_invalid_token(first_user_flask, second_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_user_flask['token'] + '1',
    "u_id": second_user_flask["auth_user_id"]})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_global_owner(first_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_user_flask['token'],
    "u_id": first_user_flask["auth_user_id"]})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_user(first_user_flask, second_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_user_flask['token'],
    "u_id": second_user_flask['auth_user_id'] + 1})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_not_global_owner(first_user_flask, second_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": second_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"]})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_user_flask, second_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"]})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_email_reusable(first_user_flask, second_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_user_flask['token'],
    "u_id": second_user_flask["auth_user_id"]})
    assert response.status_code == VALID_STATUS
    third_user = requests.post(URL_auth_register, json={"email": "neweremail@gmail.com", 
    "password": "password", "name_first": "Jason", "name_last": "Smith"})
    assert third_user.status_code == VALID_STATUS

def test_VALID_STATUS_handle_reusable(first_channel_public_flask, second_user_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_channel_public_flask['token'],
    "u_id": second_user_flask["auth_user_id"]})
    assert response.status_code == VALID_STATUS
    # register third user with same first and last name as removed user.
    third_user = requests.post(URL_auth_register, json={"email": "newest@gmail.com", 
    "password": "password", "name_first": "Jake", "name_last": "Smith"})
    third_user_details = json.loads(third_user.text)
    #add newly registered 3rd user to public channel.
    requests.post(URL_channel_join, json={"token": third_user_details['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    #get channel details of channel user joined to test handle.
    response_channel_details = requests.get(URL_channel_details, 
    params={'token': first_channel_public_flask['token'],
    'channel_id': first_channel_public_flask['channel_id']})
    response_channel_details_returns = json.loads(response_channel_details.text)
    #get handle of user and check value
    members = response_channel_details_returns['all_members']
    specific_member = members[1]
    check_handle = specific_member['handle_str']
    assert check_handle == 'jakesmith'

def test_VALID_STATUS_channel_messages(first_channel_public_flask, second_user_flask):
    # add second user to public channel
    requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    # get second user to send a message
    response = requests.post(URL_message_send, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Bye"})
    # remove user
    response = requests.delete(URL_admin_removeuser, json={"token": first_channel_public_flask['token'],
    "u_id": second_user_flask["auth_user_id"]})
    # get messages for that channel after user is removed
    compare_response = requests.get(URL_channel_messages, params = {'token': first_channel_public_flask['token'],
     'channel_id': first_channel_public_flask['channel_id'], 'start' : 0})
    message = json.loads(response.text)
    #compare message to expected replacement.
    correct_message = "Removed user"
    channel_messages_returns = json.loads(compare_response.text)
    message = channel_messages_returns['messages'][0]
    specific_message = message['message']
    assert specific_message == correct_message

def test_helper_function(clear):
    first_user = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    second_user = auth_register_v1('neweremail@gmail.com', 'password', 'Jake', 'Smith')
    admin_remove_user_v1(first_user['token'], second_user['auth_user_id'])
    assert check_user_valid(second_user["auth_user_id"]) == False
    assert check_user_valid(first_user["auth_user_id"]) == True

def test_VALID_STATUS_valid_dm_request(first_user_flask, second_dm_flask):
    response = requests.delete(URL_admin_removeuser, json={"token": first_user_flask['token'],
    "u_id": second_dm_flask["second_user_id"]})
    assert response.status_code == VALID_STATUS