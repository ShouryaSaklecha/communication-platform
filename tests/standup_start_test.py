from pytest import fixture
import pytest 
import requests
import json
import datetime
from src import config
from src import message
from src.channel import channel_messages_v1
from src.message import message_send_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_channels_create, URL_standup_start

def test_ACCESS_ERROR_invalid_token(first_channel_public_flask):
    response = requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'] + '1', 
    "channel_id": first_channel_public_flask['channel_id'], "length" : 100})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_channel_id(first_channel_public_flask):
    response = requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'], 
    "channel_id": (first_channel_public_flask['channel_id'] + 1), "length": 100})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_length_negative(first_channel_public_flask):
    response = requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "length" : -4})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_standup_already_active(first_channel_public_flask):
    requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "length" : 10000})
    response = requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "length" : 1000})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_not_a_member(first_channel_public_flask, second_user_flask):
    response = requests.post(URL_standup_start, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "length" : 100})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_channel_public_flask):
    response = requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "length": 100})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output(first_channel_public_flask):
    response = requests.post(URL_standup_start, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "length": 2})
    correct_time_finish = int((datetime.datetime.now()).timestamp()) + 2
    output = json.loads(response.text)
    # Make list to allow for +- 1 second offset in final result
    time_finishes = [correct_time_finish - 1, correct_time_finish, correct_time_finish + 1]
    output_correct = False
    for time in time_finishes:
        if output == {"time_finish": time}:
            output_correct = True
            break
    assert output_correct
    assert response.status_code == VALID_STATUS