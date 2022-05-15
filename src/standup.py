from calendar import c
from operator import index
from re import L
from pytest import raises
import datetime
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import THUMBS_UP_REACT
from src.token_helpers import validate_jwt, INVALID_TOKEN
from src.other import OWNER_PERMISSION, MEMBER_PERMISSION
from src.channel import channel_messages_v1
from src.message import message_send_v1
from src.helper_functions import channel_find, channel_user_search
import threading
import time
from typing import List, Dict, Union

def standup_end(standup_id: int, channel_id: int, token: str):
    store = data_store.get()
    standups = store['standups']
    if standups[standup_id]['messages'] != []:
        message = "\n".join(standups[standup_id]['messages'])
        message_send_v1(token, channel_id, message)
    
    standups.remove(standups[standup_id])
    data_store.set(store)
    return

def standup_start_v1(token: str, channel_id: int, length: int) -> Dict[str, int]:
    '''  
    Purpose:
        Starts a standup period whereby for the next "length" seconds if 
        someone calls "standup/send" with a message, it is buffered during 
        the X second window then at the end of the X second window a message 
        will be added to the message queue in the channel from the user who 
        started the standup.
    
    Parameters:
        token (str), channel_id (int), length (int)
    
    Return Type:
        time_finish (int)
    
    InputError:
      channel_id does not refer to a valid channel
      length is negative integer 
      active standup is already running in channel 
    
    AccessError:
      channel_id is valid and the authorised user is not a member of the channel  
      token is invalid
    
    '''
    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
    
    store = data_store.get()

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)
    
    #Raise input error if length is negatie
    if length < 0:
        raise InputError(description='Invalid length')
    
    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)
    
    standups = store['standups']
    
    # Check if channel already has an active standup
    active = standup_active_v1(token, channel_id)
    if active['is_active'] == True:
        raise InputError(description='Active standup currently running')
    
    # Getting the instantaneous time when this function is called:
    # The time when this function is called is equivalent to time sent
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_finish = current_time_int + length
    standups.append(
            {
            'c_id' : channel_id,
            'u_id' : token_valid_check,
            'time_start': current_time_int,
            'time_finish' : time_finish,
            'messages': []
            })
    
    data_store.set(store)
    
    timer = threading.Timer(length, standup_end, [len(standups) - 1, channel_id, token])
    timer.start()
    return {'time_finish': time_finish}



def standup_active_v1(token: str, channel_id: int) -> Dict[str, Union[bool, int]]:
    '''  
    Purpose:
        For a given channel return whether a standup is active in it and when it finishes
    
    Parameters:
        token (str), channel_id (int)
    
    Return Type:
        is_active (boolean)
        time_finish (int)

    
    InputError:
      channel_id does not refer to a valid channel
    
    AccessError:
      channel_id is valid and the authorised user is not a member of the channel  
      token is invalid 
    
    '''
    store = data_store.get()

    standups = store['standups']
    
    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)
    
    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)
    
    # Find active standup if it exists and return appropriate values.
    standup_index = -1
    for index, standup in enumerate(standups):
        if standup['c_id'] == channel_id:
            standup_index = index
    
    if standup_index == -1:
        return {'is_active': False,
                'time_finish': None}
    else:
        return {'is_active': True,
                'time_finish': standups[standup_index]['time_finish']}


def standup_send_v1(token: str, channel_id: int, message: str):
    '''  
    Purpose:
        Sending a message to get buffered in the standup queue, assuming a standup is currently active.
    
    Parameters:
        token (str), channel_id (int), message (str)
    
    Return Type:
        empty dictionary
    
    InputError:
      channel_id does not refer to a valid channel
      message length is over 1000 characters 
      no active standup in channel 
    
    AccessError:
      channel_id is valid and the authorised user is not a member of the channel  
      token is invalid
    
    '''
    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
    
    store = data_store.get()

    users = store['users']

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)
    
    #Raise input error if length is negatie
    if len(message) > 1000:
        raise InputError(description='Invalid length')
    
    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)
    
    standups = store['standups']
    
    # Check if channel has an active standup
    active = standup_active_v1(token, channel_id)
    if active['is_active'] == False:
        raise InputError(description='Noo active standup currently running')
    
    # Find standup and add message with handle to string
    standup_id = -1
    for count, standup in enumerate(standups):
        if channel_id == standup['c_id']:
            standup_id = count
    
    message_to_add = users[token_valid_check]['handle_str'] + ': ' + message
    standups[standup_id]['messages'].append(message_to_add)
    
    data_store.set(store)
    return {}


