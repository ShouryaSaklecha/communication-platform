from pytest import fixture
import pytest 
import requests
import json
from src import config
from src.other import THUMBS_UP_REACT
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_message_send, URL_message_senddm, URL_notifications_get, URL_message_react, URL_dm_create

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.get(URL_notifications_get, 
    params={'token': (first_user_flask['token'] + '1')})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_valid_request(first_user_flask):
    response = requests.get(URL_notifications_get, params = {'token': first_user_flask['token']})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_empty(first_user_flask):
    response = requests.get(URL_notifications_get, params = {'token': first_user_flask['token']})
    notifications = json.loads(response.text)
    correct_output = {'notifications': []}
    assert notifications == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_adding_to_channel(second_member_in_channel_public_flask):
    response = requests.get(URL_notifications_get, params = {'token': second_member_in_channel_public_flask['second_token']})
    correct_output = {
        'notifications': [{
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "johnsmith added you to new channel"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_adding_to_dm(first_dm_flask):
    response = requests.get(URL_notifications_get, params = {'token': first_dm_flask['second_token']})
    correct_output = {
        'notifications': [{
            'channel_id': -1,
            'dm_id': first_dm_flask['dm_id'],
            'notification_message': "johnsmith added you to jakesmith, johnsmith"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_tagging_channel(second_member_in_channel_public_flask):
    requests.post(URL_message_send, json={"token": second_member_in_channel_public_flask['second_token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "message" : "Hi @johnsmith"})
    response = requests.get(URL_notifications_get, params = {'token': second_member_in_channel_public_flask['token']})
    correct_output = {
        'notifications': [{
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: Hi @johnsmith"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_tagging_dm(first_dm_flask):
    requests.post(URL_message_senddm, json={"token": first_dm_flask['second_token'], 
    "dm_id": first_dm_flask['dm_id'], "message" : "Hi @johnsmith"})
    response = requests.get(URL_notifications_get, params = {'token': first_dm_flask['first_token']})
    correct_output = {
        'notifications': [{
            'channel_id': -1,
            'dm_id': first_dm_flask['dm_id'],
            'notification_message': "jakesmith tagged you in jakesmith, johnsmith: Hi @johnsmith"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_tagging_long_message(second_member_in_channel_public_flask):
    requests.post(URL_message_send, json={"token": second_member_in_channel_public_flask['second_token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "message" : "Hi @johnsmith, how are you going? This message is longer than average"})
    response = requests.get(URL_notifications_get, params = {'token': second_member_in_channel_public_flask['token']})
    correct_output = {
        'notifications': [{
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: Hi @johnsmith, how a"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_reacting_channel(second_member_in_channel_public_flask):
    message_response = requests.post(URL_message_send, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "message" : "Good message"})
    message = json.loads(message_response.text)
    requests.post(URL_message_react, json={"token": second_member_in_channel_public_flask['second_token'], 
    "message_id" : message['message_id'], "react_id": THUMBS_UP_REACT})
    response = requests.get(URL_notifications_get, params = {'token': second_member_in_channel_public_flask['token']})
    correct_output = {
        'notifications': [{
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith reacted to your message in new channel"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_reacting_dm(first_dm_flask):
    message_response = requests.post(URL_message_senddm, json={"token": first_dm_flask['first_token'], 
    "dm_id": first_dm_flask['dm_id'], "message" : "Good message"})
    message = json.loads(message_response.text)
    requests.post(URL_message_react, json={"token": first_dm_flask['second_token'], 
    "message_id" : message['message_id'], "react_id": THUMBS_UP_REACT})
    response = requests.get(URL_notifications_get, params = {'token': first_dm_flask['first_token']})
    correct_output = {
        'notifications': [{
            'channel_id': -1,
            'dm_id': first_dm_flask['dm_id'],
            'notification_message': "jakesmith reacted to your message in jakesmith, johnsmith"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_multiple_notification_types(second_member_in_channel_public_flask):
    message_response = requests.post(URL_message_send, json={"token": second_member_in_channel_public_flask['token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "message" : "Good message"})
    message = json.loads(message_response.text)
    requests.post(URL_message_react, json={"token": second_member_in_channel_public_flask['second_token'], 
    "message_id" : message['message_id'], "react_id": THUMBS_UP_REACT})
    requests.post(URL_message_send, json={"token": second_member_in_channel_public_flask['second_token'], 
    "channel_id": second_member_in_channel_public_flask['channel_id'], "message" : "Hi @johnsmith"})
    dm_response = requests.post(URL_dm_create, json={"token": second_member_in_channel_public_flask['second_token'], 
    "u_ids": [second_member_in_channel_public_flask["first_u_id"]]})
    dm = json.loads(dm_response.text)
    response = requests.get(URL_notifications_get, params = {'token': second_member_in_channel_public_flask['token']})
    correct_output = {
        'notifications': [{
            'channel_id': -1,
            'dm_id': dm['dm_id'],
            'notification_message': "jakesmith added you to jakesmith, johnsmith"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: Hi @johnsmith"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith reacted to your message in new channel"
    }]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_over_20_notifications(second_member_in_channel_public_flask):
    for count in range(31):
        requests.post(URL_message_send, json={"token": second_member_in_channel_public_flask['second_token'], 
        "channel_id": second_member_in_channel_public_flask['channel_id'], "message" : "@johnsmith " + str(count)})
    response = requests.get(URL_notifications_get, params = {'token': second_member_in_channel_public_flask['token']})
    correct_output = {
        'notifications': [{
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 30"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 29"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 28"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 27"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 26"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 25"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 24"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 23"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 22"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 21"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 20"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 19"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 18"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 17"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 16"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 15"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 14"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 13"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 12"
    }, {
            'channel_id': second_member_in_channel_public_flask['channel_id'],
            'dm_id': -1,
            'notification_message': "jakesmith tagged you in new channel: @johnsmith 11"
    }, ]}
    assert json.loads(response.text) == correct_output
    assert response.status_code == VALID_STATUS