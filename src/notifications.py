from pytest import raises
from src.data_store import data_store
from src.error import InputError, AccessError
from src.admin import check_user_valid
from src.token_helpers import validate_jwt, INVALID_TOKEN
from src.other import OWNER_PERMISSION, MEMBER_PERMISSION
from typing import List, Dict, Union

def search_v1(token: str, query_str: str) -> Dict[str, List[Dict[str, Union[int, str, List[Dict[str, Union[int, List[int], bool]]], bool]]]]:
    '''
    Returns all messages in all the channels and dms token user is in that contain a query string.

    Return Type: 
        {messages} - messages is a list containing message dictionaries which contain 
                { message_id, u_id, message, time_sent, reacts, is_pinned  }
    
    Arguments: 
        token (string) - string identifying user is logged in.
        query_str (string) - string to be checked for in each message
    
    Exceptions: 
        InputError: when string is less than 1 or more than 1000 characters. 
        AccessError: when token is invalid.
    '''
    
    store = data_store.get()

    dms = store['dms']
    channels = store['channels']
    messages = store['messages']

    # Check if the token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Raise input error if the message length is not appropriate:
    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description='Invalid query length')

    search_messages = []
    
    # Find all messages with query string where user in dm/channel
    for message in messages:
        if query_str.lower() in message['message'].lower():
            if message['dm_id'] != -1:
                # Check if user is in dm
                for member in dms[message['dm_id']]['members']:
                    if member['u_id'] == token_valid_check:
                        search_messages.append({data:message[data] for data in message if (data != 'c_id' and data != 'dm_id' and data != 'time_notified')})
                        break
            else: 
                # Check if user is in channel
                for member in channels[message['c_id']]['all_members']:
                    if member['u_id'] == token_valid_check:
                        search_messages.append({data:message[data] for data in message if (data != 'c_id' and data != 'dm_id' and data != 'time_notified')})
                        break


    # Reverse order to make most recent first in list
    search_messages.reverse()

    # Add is_this_user_reacted to each message in list
    for message in search_messages:
        for react in message['reacts']:
            if token_valid_check in react['u_ids']:
                react['is_this_user_reacted'] = True
            else: react['is_this_user_reacted'] = False

    return {'messages': search_messages}


def notifications_get_v1(token: str) -> Dict[str, List[Dict[str, Union[int, str]]]]:
    '''
    Return the user's most recent 20 notifications, ordered from most recent to least recent.
    Return Type: 
        {notifications} - notifications is a list containing notification dictionaries which contain 
                { channel_id, dm_id, notification_message }
    
    Arguments: 
        token (string) - string identifying user is logged in.
    
    Exceptions: 
        AccessError: when token is invalid.
    '''
    
    store = data_store.get()
    users = store['users']
    messages = store['messages']
    channels = store['channels']
    dms = store['dms']

    # Check if the token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Find user
    user_index = -1
    for count, user in enumerate(users):
        if user['u_id'] == token_valid_check:
            user_index = count
    
    notifications = users[user_index]['notifications']
    handle = '@' + users[user_index]['handle_str']
    for message in messages:
        if handle in message['message']:
            tagger = users[message['u_id']]
            if len(message['message']) <= 20:
                message_str = message['message']
            else: 
                message_str = message['message'][0:20]
            
            if message['c_id'] != -1:
                name = channels[message['c_id']]['name']
            else:
                name = dms[message['dm_id']]['name']
            
            notifications.append({
                'channel_id': message['c_id'],
                'dm_id': message['dm_id'],
                'notification_message': tagger['handle_str'] + " tagged you in " + name + ": " + message_str,
                'time_notified': message['time_notified']
            })
    notifications.sort(key=lambda notification: notification.get('time_notified'))

    output = []
    for notification in notifications:
        output.append({data:notification[data] for data in notification if (data != 'time_notified')})
    output.reverse()
    if len(output) <= 20:
        return {'notifications': output}
    else:
        return {'notifications': output[0:20]}