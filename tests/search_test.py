from pytest import fixture
import pytest 
import requests
import json
import datetime
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_auth_register, URL_message_send, URL_search, URL_message_senddm, URL_message_react
from src.other import THUMBS_UP_REACT

def test_ACCESS_ERROR_invalid_token(first_dm_multiple_users_flask):
    response = requests.get(URL_search, 
    params={'token': (first_dm_multiple_users_flask['token'] + '1'), 'query_str': "Query String"})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_query_str_too_short(first_dm_multiple_users_flask):
    response = requests.get(URL_search, 
    params={'token': (first_dm_multiple_users_flask['token']), 'query_str': ""})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_query_str_too_long(first_dm_multiple_users_flask):
    response = requests.get(URL_search, 
    params={'token': (first_dm_multiple_users_flask['token']), 
            'query_str': """Lorem ipsum dolor sit amet, consectetuer adipiscing 
                            elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque 
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
                            quam semper libero, sit amet adipiscing sem neque sed ipsum. Na"""})
    assert response.status_code == INPUT_ERROR

def test_VALID_STATUS_no_messages(first_dm_multiple_users_flask):
    response = requests.get(URL_search, params = {'token': first_dm_multiple_users_flask['token'], 'query_str': "Query String"})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_one_of_three_channel(three_messages):
    response = requests.get(URL_search, params = {'token': three_messages['token'], 'query_str': "Good"})
    
    search_result = json.loads(response.text)
    
    correct_output = {
        'messages' : [{
            'message_id' : three_messages['message1_ID'],
            'u_id': three_messages["user_id"],
            'message' : "Good Message",
            'time_sent': three_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }]}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_three_of_three_channel(three_messages):
    response = requests.get(URL_search, params = {'token': three_messages['token'], 'query_str': "Message"})
    search_result = json.loads(response.text)
    
    correct_output = {
        'messages' : [{
            'message_id' : three_messages['message3_ID'],
            'u_id': three_messages["user_id"],
            'message' : "Extraordinary Message",
            'time_sent': three_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }, {
            'message_id' : three_messages['message2_ID'],
            'u_id': three_messages["user_id"],
            'message' : "Better Message",
            'time_sent': three_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }, {
            'message_id' : three_messages['message1_ID'],
            'u_id': three_messages["user_id"],
            'message' : "Good Message",
            'time_sent': three_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }]}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_one_of_three_dm(three_dm_messages):
    response = requests.get(URL_search, params = {'token': three_dm_messages['first_token'], 'query_str': "Good"})
    
    search_result = json.loads(response.text)
    
    correct_output = {
        'messages' : [{
            'message_id' : three_dm_messages['message1_ID'],
            'u_id': three_dm_messages["first_user_id"],
            'message' : "Good Message",
            'time_sent': three_dm_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }]}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_three_of_three_dm(three_dm_messages):
    response = requests.get(URL_search, params = {'token': three_dm_messages['first_token'], 'query_str': "Message"})
    
    search_result = json.loads(response.text)
    
    correct_output = {
        'messages' : [{
            'message_id' : three_dm_messages['message3_ID'],
            'u_id': three_dm_messages["first_user_id"],
            'message' : "Extraordinary Message",
            'time_sent': three_dm_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }, {
            'message_id' : three_dm_messages['message2_ID'],
            'u_id': three_dm_messages["first_user_id"],
            'message' : "Better Message",
            'time_sent': three_dm_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }, {
            'message_id' : three_dm_messages['message1_ID'],
            'u_id': three_dm_messages["first_user_id"],
            'message' : "Good Message",
            'time_sent': three_dm_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }]}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_mixed(first_user_flask, first_dm_multiple_users_flask, first_channel_public_flask):
    dm_message_response = requests.post(URL_message_senddm, json={"token": first_dm_multiple_users_flask['token'], 
    "dm_id": first_dm_multiple_users_flask['dm_id'], "message" : "DM Message"})
    channel_message_response = requests.post(URL_message_send, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message" : "Channel Message"})
    time_now = datetime.datetime.now()
    dm_message = json.loads(dm_message_response.text)
    channel_message = json.loads(channel_message_response.text)

    response = requests.get(URL_search, params = {'token': first_dm_multiple_users_flask['token'], 'query_str': "Message"})

    correct_message = {
        'messages' : [{
            'message_id' : channel_message['message_id'],
            'u_id': first_user_flask["auth_user_id"],
            'message' : "Channel Message",
            'time_sent': int(time_now.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }, {
            'message_id' : dm_message['message_id'],
            'u_id': first_user_flask["auth_user_id"],
            'message' : "DM Message",
            'time_sent': int(time_now.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }]
    }
    assert json.loads(response.text) == correct_message
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_correct_output_other_user(three_messages, second_user_flask):
    response = requests.get(URL_search, params = {'token': second_user_flask['token'], 'query_str': "Good"})
    search_result = json.loads(response.text)
    correct_output = {
        'messages' : []}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_user_reacted(three_messages):
    requests.post(URL_message_react, json={"token": three_messages['token'], 
    "message_id" : three_messages['message1_ID'], "react_id": THUMBS_UP_REACT})
    response = requests.get(URL_search, params = {'token': three_messages['token'], 'query_str': "Good"})
    search_result = json.loads(response.text)
    
    
    correct_output = {
        'messages' : [{
            'message_id' : three_messages['message1_ID'],
            'u_id': three_messages["user_id"],
            'message' : "Good Message",
            'time_sent': three_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [three_messages["user_id"]], 
                        "is_this_user_reacted": True}],
            'is_pinned': False
        }]}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS
    
def test_VALID_STATUS_case_insensitive(three_messages):
    response = requests.get(URL_search, params = {'token': three_messages['token'], 'query_str': "gOOD"})
    
    search_result = json.loads(response.text)
    
    correct_output = {
        'messages' : [{
            'message_id' : three_messages['message1_ID'],
            'u_id': three_messages["user_id"],
            'message' : "Good Message",
            'time_sent': three_messages['time_now'],
            'reacts': [{"react_id": 1,
                        "u_ids": [], 
                        "is_this_user_reacted": False}],
            'is_pinned': False
        }]}
    assert search_result == correct_output
    assert response.status_code == VALID_STATUS