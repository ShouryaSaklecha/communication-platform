from pytest import fixture
import pytest 
import requests
import json
import datetime
import time
from src import config
from src import message
from src.channel import channel_messages_v1
from src.message import message_send_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_channels_create, URL_standup_start, URL_standup_send, URL_channel_messages

def test_ACCESS_ERROR_invalid_token(first_standup):
    response = requests.post(URL_standup_send, json={"token": first_standup['token'] + '1', 
    "channel_id": first_standup['channel_id'], "message" : "Good message"})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_channel_id(first_standup):
    response = requests.post(URL_standup_send, json={"token": first_standup['token'], 
    "channel_id": first_standup['channel_id'] + 1, "message" : "Good message"})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_too_long(first_standup):
    long_message = """Lorem ipsum dolor sit amet, consectetuer adipiscing 
        elit. Aenean commodo 
        ligula eget dolor. Aenean massa. Cum sociis natoque 
        penatibus et magnis dis parturient montes, nascetur 
        ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu,
        pretium quis, sem. Nulla consequat massa quis enim. Donec pede 
        justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim
        justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam 
        dictum felis eu pede mollis pretium. Integer tincidunt. Cras 
        dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend
        tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend
        ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, 
        tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. 
        Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi.
        Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem 
        quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"""
    response = requests.post(URL_standup_send, json={"token": first_standup['token'] + '1', 
    "channel_id": first_standup['channel_id'], "message" : long_message})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_no_active_standup(first_channel_public_flask):
    response = requests.post(URL_standup_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good message"})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_not_a_member(first_standup, third_user_flask):
    response = requests.post(URL_standup_send, json={"token": third_user_flask['token'], 
    "channel_id": first_standup['channel_id'], "message" : "Good message"})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_standup):
    response = requests.post(URL_standup_send, json={"token": first_standup['token'], 
    "channel_id": first_standup['channel_id'], "message" : "Good message"})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output(first_standup):
    requests.post(URL_standup_send, json={"token": first_standup['token'], 
    "channel_id": first_standup['channel_id'], "message" : "This is John's message"})
    requests.post(URL_standup_send, json={"token": first_standup['second_token'], 
    "channel_id": first_standup['channel_id'], "message" : "This is Jake's message"})
    time.sleep(6)
    response = requests.get(URL_channel_messages, params = {'token': first_standup['token'],
     'channel_id': first_standup['channel_id'], 'start' : 0})
    output = json.loads(response.text)
    # Make list to allow for +- 1 second offset in final result
    time_finishes = [first_standup['time_finish'] - 1, first_standup['time_finish'], first_standup['time_finish'] + 1]
    output_correct = False
    for finish in time_finishes:
        if output == {'messages' : [{
                    'message_id' : 0,
                    'u_id': first_standup["first_u_id"],
                    'message' : '''johnsmith: This is John's message\njakesmith: This is Jake's message''',
                    'time_sent': finish,
                    'reacts': [{"react_id": 1,
                                "u_ids": [], 
                                "is_this_user_reacted": False}],
                    'is_pinned': False
                }],
                'start' : 0,
                'end' : -1,
            }:
            output_correct = True
            break
    assert output_correct
    assert response.status_code == VALID_STATUS