from time import sleep
from pytest import fixture
import pytest 
import requests
import json
import datetime
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_message_sendlater, URL_message_edit, URL_channel_details, URL_channel_messages, URL_channels_create, URL_clear, URL_message_sendlater

def test_INPUT_ERROR_invalid_channel_id(first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 10
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": (first_channel_public_flask['channel_id'] + 1), "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_short(first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 10
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": "", 
    "time_sent": time_finish})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_message_long(first_channel_public_flask):
    new_message = """Lorem ipsum dolor sit amet, consectetuer adipiscing 
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
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 10
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": new_message, 
    "time_sent": time_finish})
    assert response.status_code == INPUT_ERROR

def test_ACSESS_ERROR_invalid_token(first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 10
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'] + '1', 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == ACCESS_ERROR

def test_ACSESS_ERROR_token_user_not_in_channel(first_channel_public_flask, second_user_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 10
    response = requests.post(URL_message_sendlater, json={"token": second_user_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_past_time(first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int - 10
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == INPUT_ERROR

def test_VALID_STATUS_message_send(first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 10
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_message_send_output(three_dm_messages, first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 5
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == VALID_STATUS
    sleep(5)
    compare_response = requests.get(URL_channel_messages, params = {'token': first_channel_public_flask['token'],
     'channel_id': first_channel_public_flask['channel_id'], 'start' : 0})
    assert compare_response.status_code == VALID_STATUS
    message = json.loads(response.text)
    time_now = int(datetime.datetime.now().timestamp())
    time_finishes = [time_now - 1, time_now, time_now + 1]
    output_correct = False
    for time in time_finishes:
        correct_message = {
            'messages' : [{
                'message_id' : message['message_id'],
                'u_id': 0,
                'message' : "loremipsum",
                'time_sent': time,
                'reacts': [{"react_id": 1,
                            "u_ids": [], 
                            "is_this_user_reacted": False}],
                'is_pinned': False
            }],
            'start' : 0,
            'end' : -1,
        }
        if json.loads(compare_response.text) == correct_message:
            output_correct = True
    assert output_correct

def test_VALID_STATUS_cannotedit(first_channel_public_flask):
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + 5
    response = requests.post(URL_message_sendlater, json={"token": first_channel_public_flask['token'], 
    "channel_id": first_channel_public_flask['channel_id'], "message": "loremipsum", 
    "time_sent": time_finish})
    assert response.status_code == VALID_STATUS
    message = json.loads(response.text)
    response = requests.put(URL_message_edit, json={"token": first_channel_public_flask['token'],
    "message_id": message['message_id'], "message": "newmessage"})
    assert response.status_code == INPUT_ERROR
    sleep(5)
    response = requests.put(URL_message_edit, json={"token": first_channel_public_flask['token'],
    "message_id": message['message_id'], "message": "newmessage"})
    assert response.status_code == VALID_STATUS