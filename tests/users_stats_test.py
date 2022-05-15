from pytest import fixture
import pytest 
import requests
import datetime
import json
from src.error import ACCESS_ERROR, VALID_STATUS
from tests.routes_test import URL_users_stats, URL_channels_create, URL_dm_create, URL_message_send, URL_channel_join

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.get(URL_users_stats, 
    params={'token': (first_user_flask['token'] + '1')})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.get(URL_users_stats, params = {'token': first_user_flask['token']})
    assert response.status_code == VALID_STATUS

def test_empty_VALID_STATUS(first_user_flask):
    response = requests.get(URL_users_stats, params = {'token': first_user_flask['token']})
    workspace_stats = json.loads(response.text)
    test_time = int(datetime.datetime.now().timestamp())
    correct_output = {'channels_exist': [{'num_channels_exist': 0, 'time_stamp': test_time}],
                      'dms_exist': [{'num_dms_exist': 0,'time_stamp' : test_time}],
                      'messages_exist': [{'num_messages_exist': 0,'time_stamp': test_time}],
                      'utilization_rate': 0}   
    assert workspace_stats == correct_output            
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_multiple_channels(first_user_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'newer channel', "is_public": True})
    response = requests.get(URL_users_stats, params = {'token': first_user_flask['token']})
    workspace_stats = json.loads(response.text)
    test_time = int(datetime.datetime.now().timestamp())
    correct_output = {'channels_exist': [{'num_channels_exist': 2, 'time_stamp': test_time}],
                      'dms_exist': [{'num_dms_exist': 0,'time_stamp' : test_time}],
                      'messages_exist': [{'num_messages_exist': 0,'time_stamp': test_time}],
                      'utilization_rate': 1.0}   
    assert workspace_stats == correct_output            
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_dm_exist(first_user_flask, second_user_flask, third_user_flask):
    requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"], third_user_flask["auth_user_id"]]})
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'newer channel', "is_public": True})
    response = requests.get(URL_users_stats, params = {'token': first_user_flask['token']})
    workspace_stats = json.loads(response.text)
    test_time = int(datetime.datetime.now().timestamp())
    correct_output = {'channels_exist': [{'num_channels_exist': 2, 'time_stamp': test_time}],
                      'dms_exist': [{'num_dms_exist': 1,'time_stamp' : test_time}],
                      'messages_exist': [{'num_messages_exist': 0,'time_stamp': test_time}],
                      'utilization_rate': 1.0}   
    assert workspace_stats == correct_output            
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_message_exists(first_user_flask, second_user_flask, third_user_flask,first_channel_public_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"]]})
    requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    response = requests.get(URL_users_stats, params = {'token': first_user_flask['token']})
    workspace_stats = json.loads(response.text)
    test_time = int(datetime.datetime.now().timestamp())
    correct_output = {'channels_exist': [{'num_channels_exist': 2, 'time_stamp': test_time}],
                      'dms_exist': [{'num_dms_exist': 1,'time_stamp' : test_time}],
                      'messages_exist': [{'num_messages_exist': 1,'time_stamp': test_time}],
                      'utilization_rate': 0.6666666666666666}   
    assert workspace_stats == correct_output            
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_inactive_user(first_user_flask, second_user_flask, third_user_flask,first_channel_public_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_dm_create, json={"token": first_user_flask['token'], 
    "u_ids": [second_user_flask["auth_user_id"]]})
    requests.post(URL_channel_join, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id']})
    requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Good Message"})
    response = requests.get(URL_users_stats, params = {'token': third_user_flask['token']})
    workspace_stats = json.loads(response.text)
    test_time = int(datetime.datetime.now().timestamp())
    correct_output = {'channels_exist': [{'num_channels_exist': 2, 'time_stamp': test_time}],
                      'dms_exist': [{'num_dms_exist': 1,'time_stamp' : test_time}],
                      'messages_exist': [{'num_messages_exist': 1,'time_stamp': test_time}],
                      'utilization_rate': 0.6666666666666666}   
    assert workspace_stats == correct_output            
    assert response.status_code == VALID_STATUS