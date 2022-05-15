from pytest import fixture
import pytest
import requests
import json
from src import config
from src.error import ACCESS_ERROR, INPUT_ERROR, VALID_STATUS
from src.other import GENERIC_PROFILE_URL
from tests.routes_test import URL_user_profile, URL_user_profile_uploadphoto
from tests.routes_test import URL_channel_details, URL_dm_details

RICHARD_BUCKLAND = "http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png"
TAJ = "http://www.dpgraph.com/taj.jpg"
BOAT = "http://www.dpgraph.com/boot.jpg"
SERVER_BOAT = config.url + "imgurl/" + "ebf927c1739941f054c8.jpg"

def test_ACCESS_ERROR_invalid_token(first_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": (first_user_flask['token'] + '1'), 
    "img_url" : TAJ, "x_start": 0, "y_start": 0, "x_end": 50, "y_end": 50})

    assert response.status_code == ACCESS_ERROR

def test_INPUT_ERROR_invalid_x_y_start(first_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": first_user_flask['token'], 
    "img_url" : TAJ, "x_start": 100, "y_start": 100, "x_end": 200, "y_end": 102})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_invalid_x_y_end(first_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": first_user_flask['token'], 
    "img_url" : TAJ, "x_start": 0, "y_start": 0, "x_end": 200, "y_end": 100})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_same_x_y_end(first_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": first_user_flask['token'], 
    "img_url" : TAJ, "x_start": 0, "y_start": 0, "x_end": 0, "y_end": 0})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_small_x_y_end(first_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": first_user_flask['token'], 
    "img_url" : TAJ, "x_start": 10, "y_start": 10, "x_end": 0, "y_end": 0})

    assert response.status_code == INPUT_ERROR

def test_INPUT_ERROR_png_img_url(first_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": first_user_flask['token'], 
    "img_url" : RICHARD_BUCKLAND, "x_start": 0, "y_start": 0, "x_end": 100, "y_end": 100})

    assert response.status_code == INPUT_ERROR

def test_VALID_STATUS_BOAT_channels_img_url(first_channel_public_flask, second_channel_public_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": second_channel_public_flask['token'], 
    "img_url" : BOAT, "x_start": 0, "y_start": 0, "x_end": 96, "y_end": 72})

    response_1 = requests.get(URL_channel_details, 
    params={'token': second_channel_public_flask['token'],
    'channel_id': second_channel_public_flask['channel_id']})
    
    assert response_1.status_code == VALID_STATUS

    correct_output = {
        'name': 'newer channel',
        'is_public': True,
        'owner_members': [
            {
                'u_id': second_channel_public_flask['user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': SERVER_BOAT,
            }
        ],
        'all_members': [
            {
                'u_id': second_channel_public_flask['user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': SERVER_BOAT,
            },
        ],
    }

    assert json.loads(response_1.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_BOAT_dms_img_url(first_dm_flask, second_dm_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": second_dm_flask['second_token'], 
    "img_url" : BOAT, "x_start": 0, "y_start": 0, "x_end": 96, "y_end": 72})

    response_1 = requests.get(URL_dm_details, params={"token": second_dm_flask['first_token'], 
    "dm_id": second_dm_flask['dm_id']})
    
    assert response_1.status_code == VALID_STATUS

    correct_output = {
        "name": 'jakesmith, tomzombom',
        "members": [
            {
                'u_id': second_dm_flask['first_user_id'],
                'email': 'neweremail@gmail.com',
                'name_first': 'Jake',
                'name_last': 'Smith',
                'handle_str': 'jakesmith',
                'profile_img_url': GENERIC_PROFILE_URL,
            },
            {
                'u_id': second_dm_flask['second_user_id'],
                'email': 'thirdemail@gmail.com',
                'name_first': 'Tom',
                'name_last': 'Zombom',
                'handle_str': 'tomzombom',
                'profile_img_url': SERVER_BOAT,
            },
        ],
    }

    assert json.loads(response_1.text) == correct_output
    assert response.status_code == VALID_STATUS

def test_VALID_STATUS_double_TAJ_img_url(first_user_flask, second_user_flask):
    response = requests.post(URL_user_profile_uploadphoto, json={"token": first_user_flask['token'], 
    "img_url" : TAJ, "x_start": 0, "y_start": 0, "x_end": 50, "y_end": 70})
    response_1 = requests.post(URL_user_profile_uploadphoto, json={"token": second_user_flask['token'], 
    "img_url" : TAJ, "x_start": 0, "y_start": 0, "x_end": 20, "y_end": 40})

    response_2 = requests.get(URL_user_profile,
    params={'token': first_user_flask['token'], 'u_id': first_user_flask['auth_user_id']})
    
    assert response_2.status_code == VALID_STATUS

    response_3 = requests.get(URL_user_profile,
    params={'token': second_user_flask['token'], 'u_id': second_user_flask['auth_user_id']})
    
    assert response_3.status_code == VALID_STATUS

    correct_output = {'user': {'u_id': first_user_flask['auth_user_id'],
                               'email': 'newemail@gmail.com',
                               'name_first': 'John',
                               'name_last': 'Smith',
                               'handle_str': 'johnsmith',
                               'profile_img_url': (GENERIC_PROFILE_URL[:-4] + "(1).jpg"),
                                }
                    }

    correct_output_1 = {'user': {'u_id': second_user_flask['auth_user_id'],
                               'email': 'neweremail@gmail.com',
                               'name_first': 'Jake',
                               'name_last': 'Smith',
                               'handle_str': 'jakesmith',
                               'profile_img_url': (GENERIC_PROFILE_URL[:-4] + "(2).jpg"),
                                }
                    }

    assert json.loads(response_2.text) == correct_output
    assert json.loads(response_3.text) == correct_output_1
    assert response.status_code == VALID_STATUS
    assert response_1.status_code == VALID_STATUS

    