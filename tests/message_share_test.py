from urllib import response
from pytest import fixture
import pytest 
import requests
import json
from src.error import InputError, AccessError, ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_auth_register, URL_channel_invite, URL_channel_details, URL_channel_messages, URL_channels_create, URL_clear, URL_message_send, URL_message_share

def test_VALID_STATUS_validshare_channel(three_messages):
    response = requests.post(URL_message_share, json={'token': three_messages['token'], 
    'og_message_id': three_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': three_messages['c_id'], 'dm_id': -1})
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_validshare_dm(three_dm_messages):
    response = requests.post(URL_message_share, json={'token': three_dm_messages['first_token'], 
    'og_message_id': three_dm_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': -1, 'dm_id': three_dm_messages['dm_id']})
    assert response.status_code == VALID_STATUS

def test_ACCESS_ERROR_invalid_token(three_messages):
    response = requests.post(URL_message_share, json={'token': three_messages['token'] + '1', 
    'og_message_id': three_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': three_messages['c_id'], 'dm_id': -1})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_dmchannel(three_messages):
    response = requests.post(URL_message_share, json={'token': three_messages['token'], 
    'og_message_id': three_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': -1, 'dm_id': -1})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_neither_negative(three_messages, three_dm_messages):
    response = requests.post(URL_message_share, json={'token': three_messages['token'], 
    'og_message_id': three_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': three_messages['c_id'], 'dm_id': three_dm_messages['dm_id']})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalidmessage(three_messages, three_dm_messages, third_user_flask):
    # add third user to the channel from three_messages
    requests.post(URL_channel_invite, json={"token": three_messages['token'], 
    "channel_id": three_messages['c_id'], "u_id": third_user_flask['auth_user_id']})
    # get third user to request to share a message from thee_dm_messageds dm
    response = requests.post(URL_message_share, json={'token': third_user_flask['token'], 
    'og_message_id': three_dm_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': three_messages['c_id'], 'dm_id': -1})
    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_messagetoolong(three_messages):
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
    response = requests.post(URL_message_share, json={'token': three_messages['token'], 
    'og_message_id': three_messages['message1_ID'], 'message': new_message, 
    'channel_id': three_messages['c_id'], 'dm_id': -1})
    assert response.status_code == INPUT_ERROR

def test_ACCESS_ERROR_notmember_channel(three_messages, second_user_flask):
    response = requests.post(URL_message_share, json={'token': second_user_flask['token'], 
    'og_message_id': three_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': three_messages['c_id'], 'dm_id': -1})
    assert response.status_code == ACCESS_ERROR

def test_ACCESS_ERROR_notmember_dm(three_dm_messages, third_user_flask):
    response = requests.post(URL_message_share, json={'token': third_user_flask['token'], 
    'og_message_id': three_dm_messages['message1_ID'], 'message': 'sharing this', 
    'channel_id': -1, 'dm_id': three_dm_messages['dm_id']})
    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_no_message(three_messages):
    response = requests.post(URL_message_share, json={'token': three_messages['token'], 
    'og_message_id': 8, 'message': 'sharing this', 
    'channel_id': three_messages['c_id'], 'dm_id': -1})
    assert response.status_code == INPUT_ERROR