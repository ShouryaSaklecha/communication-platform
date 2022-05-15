from pytest import fixture
import pytest
import requests
import json
from src import config
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_channel_messages, URL_dm_messages
from tests.routes_test import URL_message_pin, URL_message_unpin

def test_INPUT_ERROR_invalid_message_id(three_messages):
    response = requests.post(URL_message_pin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == VALID_STATUS

    response = requests.post(URL_message_unpin, json={"token": three_messages['token'], 
    "message_id" : (three_messages['message1_ID'] + 4)})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_user_not_in_channel(three_messages, third_user_flask):
    response = requests.post(URL_message_pin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == VALID_STATUS
    
    response = requests.post(URL_message_unpin, json={"token": third_user_flask['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_user_not_in_dm(three_dm_messages, third_user_flask):
    response = requests.post(URL_message_pin, json={"token": three_dm_messages['first_token'], 
    "message_id" : three_dm_messages['message1_ID']})

    assert response.status_code == VALID_STATUS
    
    response = requests.post(URL_message_unpin, json={"token": third_user_flask['token'], 
    "message_id" : three_dm_messages['message1_ID']})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_not_already_pinned(three_messages):
    response = requests.post(URL_message_pin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == VALID_STATUS

    response_1 = requests.post(URL_message_unpin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})
    response_2 = requests.post(URL_message_unpin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})
    
    
    assert response_1.status_code == VALID_STATUS
    assert response_2.status_code == INPUT_ERROR

def test_ACCESS_ERROR_channel_user_not_owner(three_messages_two_users):
    response = requests.post(URL_message_pin, json={"token": three_messages_two_users['first_token'], 
    "message_id" : three_messages_two_users['message1_ID']})

    assert response.status_code == VALID_STATUS
    
    response = requests.post(URL_message_unpin, json={"token": three_messages_two_users['second_token'], 
    "message_id" : three_messages_two_users['message1_ID']})

    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_dm_user_not_owner(three_dm_messages, second_user_flask):
    response = requests.post(URL_message_pin, json={"token": three_dm_messages['first_token'], 
    "message_id" : three_dm_messages['message1_ID']})

    assert response.status_code == VALID_STATUS
    
    response = requests.post(URL_message_unpin, json={"token": second_user_flask['token'], 
    "message_id" : three_dm_messages['message1_ID']})

    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(three_messages):
    response = requests.post(URL_message_pin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == VALID_STATUS
    
    response = requests.post(URL_message_unpin, json={"token": (three_messages['token'] + '1'), 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_channel_message_unpin(three_messages):
    response = requests.post(URL_message_pin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response.status_code == VALID_STATUS

    response1 = requests.post(URL_message_unpin, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID']})

    assert response1.status_code == VALID_STATUS

    compare_response = requests.get(URL_channel_messages, params = {'token': three_messages['token'],
    'channel_id': three_messages['c_id'], 'start': 0})

    assert compare_response.status_code == VALID_STATUS

    channel_messages_returns = json.loads(compare_response.text)
    messages = channel_messages_returns['messages'][2]
    
    assert messages['is_pinned'] == False

def test_VALID_STATUS_dm_message_unpin(three_dm_messages):
    response = requests.post(URL_message_pin, json={"token": three_dm_messages['first_token'], 
    "message_id" : three_dm_messages['message1_ID']})

    assert response.status_code == VALID_STATUS

    response = requests.post(URL_message_unpin, json={"token": three_dm_messages['first_token'], 
    "message_id" : three_dm_messages['message1_ID']})

    assert response.status_code == VALID_STATUS

    compare_response = requests.get(URL_dm_messages, params = {'token': three_dm_messages['first_token'],
    'dm_id': three_dm_messages['dm_id'], 'start': 0})

    assert compare_response.status_code == VALID_STATUS

    dm_messages_returns = json.loads(compare_response.text)
    messages = dm_messages_returns['messages'][2]
    
    assert messages['is_pinned'] == False
