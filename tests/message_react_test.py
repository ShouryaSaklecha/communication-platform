from pytest import fixture
import pytest
import requests
import json
from src import config
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import THUMBS_UP_REACT
from tests.routes_test import URL_channel_messages, URL_dm_messages, URL_message_react

def test_INPUT_ERROR_invalid_message_id(three_messages):
    response = requests.post(URL_message_react, json={"token": three_messages['token'], 
    "message_id" : (three_messages['message1_ID'] + 4), "react_id": THUMBS_UP_REACT})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_user_not_in_channel(three_messages, third_user_flask):
    response = requests.post(URL_message_react, json={"token": third_user_flask['token'], 
    "message_id" : three_messages['message1_ID'], "react_id": THUMBS_UP_REACT})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_user_not_in_dm(three_dm_messages, third_user_flask):
    response = requests.post(URL_message_react, json={"token": third_user_flask['token'], 
    "message_id" : three_dm_messages['message1_ID'], "react_id": THUMBS_UP_REACT})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_react_id(three_messages):
    response = requests.post(URL_message_react, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID'], "react_id": 0})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_already_reacted(three_messages):
    response = requests.post(URL_message_react, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID'], "react_id": THUMBS_UP_REACT})
    response_1 = requests.post(URL_message_react, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID'], "react_id": THUMBS_UP_REACT})

    assert response.status_code == VALID_STATUS
    assert response_1.status_code == INPUT_ERROR

def test_ACCESS_ERROR_invalid_token(three_messages):
    response = requests.post(URL_message_react, json={"token": (three_messages['token'] + '1'), 
    "message_id" : three_messages['message1_ID'], "react_id": THUMBS_UP_REACT})

    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_channel_message_react(three_messages):
    response = requests.post(URL_message_react, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID'], "react_id": THUMBS_UP_REACT})

    assert response.status_code == VALID_STATUS

    compare_response = requests.get(URL_channel_messages, params = {'token': three_messages['token'],
    'channel_id': three_messages['c_id'], 'start': 0})

    assert compare_response.status_code == VALID_STATUS

    channel_messages_returns = json.loads(compare_response.text)
    messages = channel_messages_returns['messages'][2]
    
    assert messages['reacts'][0]['is_this_user_reacted'] == True

def test_VALID_STATUS_dm_message_react(three_dm_messages):
    response = requests.post(URL_message_react, json={"token": three_dm_messages['first_token'], 
    "message_id" : three_dm_messages['message1_ID'], "react_id": THUMBS_UP_REACT})

    assert response.status_code == VALID_STATUS

    compare_response = requests.get(URL_dm_messages, params = {'token': three_dm_messages['first_token'],
    'dm_id': three_dm_messages['dm_id'], 'start': 0})

    assert compare_response.status_code == VALID_STATUS

    dm_messages_returns = json.loads(compare_response.text)
    messages = dm_messages_returns['messages'][2]
    
    assert messages['reacts'][0]['is_this_user_reacted'] == True
