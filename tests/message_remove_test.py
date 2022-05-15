from pytest import fixture
import pytest 
import requests
import json
import datetime
from src import config
from src import message
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_message_senddm, URL_channel_addowner, URL_message_send, URL_message_remove

def test_VALID_STATUS_remove1(three_messages):
    response1 = requests.delete(URL_message_remove, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID']})
    assert response1.status_code == VALID_STATUS
    response2 = requests.delete(URL_message_remove, json={"token": three_messages['token'],
    "message_id": three_messages['message2_ID']})
    assert response2.status_code == INPUT_ERROR

def test_INPUT_ERROR_nomessage(three_messages):
    response = requests.delete(URL_message_remove, json={"token": three_messages['token'],
    "message_id": three_messages['message3_ID'] + 2})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_notsender_notowner(three_messages, second_member_in_channel_public_flask):
    response = requests.delete(URL_message_remove, json={"token": second_member_in_channel_public_flask['second_token'],
    "message_id": three_messages['message2_ID']})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_notindm_notowner(first_dm_multiple_users_flask):
    response = requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "Good Message"})
    assert response.status_code == VALID_STATUS
    message_sent = json.loads(response.text)
    response2 = requests.delete(URL_message_remove, json={"token": first_dm_multiple_users_flask['second_user_token'],
    "message_id": message_sent['message_id']})
    assert response2.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_invalid_token(three_messages):
    response1 = requests.delete(URL_message_remove, json={"token": three_messages['token'] + '1',
    "message_id": three_messages['message2_ID']})
    assert response1.status_code == ACCESS_ERROR

def test_VALID_STATUS_dm_messages(three_dm_messages):
    response1 = requests.delete(URL_message_remove, json={"token": three_dm_messages['first_token'],
    "message_id": three_dm_messages['message2_ID']})
    assert response1.status_code == VALID_STATUS
    