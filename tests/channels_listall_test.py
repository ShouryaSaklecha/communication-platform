from tests.conftest import first_channel_public_flask
from urllib import request, response
from pytest import fixture
import pytest
import json
import requests
from src.error import ACCESS_ERROR, AccessError, VALID_STATUS
from tests.routes_test import URL_channel_listall, URL_channels_create

def test_ACCESS_ERROR_invalid_token(first_user_flask, first_channel_public_flask):
    response = requests.get(URL_channel_listall,
    params={'token': first_user_flask['token'] + '1',})
    assert response.status_code == ACCESS_ERROR

def test_VALID_STATUS_one_channel(first_user_flask, first_channel_public_flask):
    response = requests.get(URL_channel_listall,
    params={'token': first_user_flask['token']})
    details = {
        'channels': [
            {
        		'channel_id': 0,
        		'name': 'new channel',
        	}
        ]
    }
    assert json.loads(response.text) == details
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_many_channel(first_user_flask, second_user_flask):
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'new channel', "is_public": True})
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'newer channel', "is_public": True})
    requests.post(URL_channels_create, 
    json={"token": first_user_flask['token'],
    "name": 'newest channel', "is_public": True})
    requests.post(URL_channels_create, 
    json={"token": second_user_flask['token'],
    "name": 'newester channel', "is_public": True})
    response = requests.get(URL_channel_listall,
    params={'token': first_user_flask['token']})
    details = {
        'channels': [
        	{
        		'channel_id': 0,
        		'name': 'new channel',
        	},
            {
                'channel_id': 1,
        		'name': 'newer channel',
            },
            {
                'channel_id': 2,
        		'name': 'newest channel',
            },
            {
                'channel_id': 3,
        		'name': 'newester channel',
            }
        ]
    }
    assert json.loads(response.text) == details
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_no_channels(first_user_flask):
    response = requests.get(URL_channel_listall,
    params={'token': first_user_flask['token']})
    details = {'channels': []}
    assert json.loads(response.text) == details
    assert response.status_code == VALID_STATUS
