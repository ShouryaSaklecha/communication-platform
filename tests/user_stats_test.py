from pytest import fixture
import pytest 
import requests
import datetime
import json
from src.error import ACCESS_ERROR, VALID_STATUS
from tests.routes_test import URL_channel_listall, URL_dm_list, URL_channel_messages, URL_dm_messages, URL_user_stats
from tests.routes_test import URL_channels_create, URL_dm_create, URL_channel_join, URL_message_send

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.get(URL_user_stats, 
    params={'token': (first_user_flask['token'] + '1')})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.get(URL_user_stats, params = {'token': first_user_flask['token']})
    assert response.status_code == VALID_STATUS

def test_empty_VALID_STATUS(first_user_flask):
    response = requests.get(URL_user_stats, params = {'token': first_user_flask['token']})
    user_stats = json.loads(response.text)
    test_time_stamp = int(datetime.datetime.now().timestamp())
    correct_output = {
        'channels_joined': [{'num_channels_joined' : 0, 'time_stamp' : test_time_stamp}],
        'dms_joined': [{'num_dms_joined' : 0, 'time_stamp' : test_time_stamp}],
        'messages_sent': [{'num_messages_sent' : 0, 'time_stamp' : test_time_stamp}],
        'involvement_rate': 0,
        }                  
    assert user_stats == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_channel(first_user_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'newer channel', "is_public": True})
    response = requests.get(URL_user_stats, params = {'token': first_user_flask['token']})
    user_stats = json.loads(response.text)
    test_time_stamp = int(datetime.datetime.now().timestamp())
    correct_output = {
        'channels_joined': [{'num_channels_joined' : 2, 'time_stamp' : test_time_stamp}],
        'dms_joined': [{'num_dms_joined' : 0, 'time_stamp' : test_time_stamp}],
        'messages_sent': [{'num_messages_sent' : 0, 'time_stamp' : test_time_stamp}],
        'involvement_rate': 1,
        }   
    assert user_stats == correct_output
    assert response.status_code == VALID_STATUS   

def test_VALID_STATUS_dms(first_user_flask, second_user_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})       
    requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"]]})   
    response = requests.get(URL_user_stats, params = {'token': second_user_flask['token']})
    user_stats = json.loads(response.text)
    test_time_stamp = int(datetime.datetime.now().timestamp())
    correct_output = {
        'channels_joined': [{'num_channels_joined' : 0, 'time_stamp' : test_time_stamp}],
        'dms_joined': [{'num_dms_joined' : 1, 'time_stamp' : test_time_stamp}],
        'messages_sent': [{'num_messages_sent' : 0, 'time_stamp' : test_time_stamp}],
        'involvement_rate': 0.5,
        }
    assert user_stats == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_messages(first_user_flask, second_user_flask,first_channel_public_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"]]})
    requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    response = requests.get(URL_user_stats, params = {'token': first_user_flask['token']})
    user_stats = json.loads(response.text)
    test_time_stamp = int(datetime.datetime.now().timestamp())
    correct_output = {
        'channels_joined': [{'num_channels_joined' : 2, 'time_stamp' : test_time_stamp}],
        'dms_joined': [{'num_dms_joined' : 1, 'time_stamp' : test_time_stamp}],
        'messages_sent': [{'num_messages_sent' : 1, 'time_stamp' : test_time_stamp}],
        'involvement_rate': 1,
        }
    assert user_stats == correct_output
    assert response.status_code == VALID_STATUS

