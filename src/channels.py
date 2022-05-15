from pytest import raises
from src.data_store import data_store
from src.error import InputError, AccessError
from src.token_helpers import validate_jwt, INVALID_TOKEN
from typing import Union, List, Dict

def channels_list_v1(token: str) -> Dict[str, List[Dict[str, Union[int, str]]]]:
    '''
    Lists all channels that a user is part of, returning a list of these channels.

     Arguments:
        token (string) - string identifying user is logged in.

    Exceptions:
        AccessError - occurs when token is invalid

    Return Value:
        Returns dictionary channels on the condition that no exceptions are thrown.
    '''
    store = data_store.get()

    channels = store['channels']
    users = store['users']

    # If authorised user id is not a valid id then an access error is raised
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Search for channels that contain the user's id
    channels_list = []

    for channel in channels:
        members = channel["all_members"]
        for users in members:
            id = users["u_id"]
            # Add to channel_dict
            if id == token_valid_check:
                channel_dict = {
                    'channel_id': channel["c_id"],
                    'name': channel["name"]
                }
                channels_list.append(channel_dict)

    data_store.set(store)

    return { 'channels': channels_list
    }

def channels_listall_v1(token: str) -> Dict[str, List[Dict[str, Union[int, str]]]]:
    '''
    Lists all channels that have been created, both private and public, returning a list of these channels.

     Arguments:
        token (string) - string identifying user is logged in.

    Exceptions:
        AccessError - occurs when token is invalid

    Return Value:
        Returns dictionary channels on the condition that no exceptions are thrown.
    '''
    store = data_store.get()

    channels = store['channels']

    channels_list = []

    # If authorised user id is not a valid id then an access error is raised
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Loop through all the channels
    for channel in channels:
        channel_dict = {
            'channel_id': channel["c_id"],
            'name': channel["name"]
        }
        channels_list.append(channel_dict)

    data_store.set(store)

    return {
        'channels': channels_list,
    }

def channels_create_v1(token: str, name: str, is_public: bool) -> Dict[str, int]:
    ''' 
    Generates channel_id, makes creator user part of owner_members and all_members, and returns channel_id.

     Arguments:
        token (string) - string identifying user is logged in.
        name (string) - string containing channel's name.
        is_public (boolean) - boolean determining if channel will be public after creation
                              1 if public, 0 if private

    Exceptions:
        InputError - Occurs when length of name is less than 1 or 
        more than 20 characters
        AccessError - Occurs when token is invalid

    Return Value:
        Returns dictionary channel_id on the condition that no exceptions are thrown.
    '''
    # Raise input error if name is incorrect length
    if len(name) > 20 or len(name) < 1:
        raise InputError(description='Invalid name length')

    store = data_store.get()

    channels = store['channels']
    users = store['users']
    
    # Check if token is invalid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Generate channel_id
    channel_id = len(channels)
    
    # Make owner_members list and all_members list and add creator to both
    user_1 = users[token_valid_check]
    user_1_details = {'u_id': user_1['u_id'],
                      'email': user_1['email'], 
                      'name_first': user_1['name_first'],
                      'name_last': user_1['name_last'],
                      'handle_str': user_1['handle_str'],
                      'permission_id': user_1['permission_id'],
                      'profile_img_url': user_1['profile_img_url'],
                      }
    owner_members = [user_1_details]
    all_members = [user_1_details]

    # Store all data as a dictionary

    channels.append({
        "c_id": channel_id,
        "name": name,
        "is_public": is_public,
        "owner_members": owner_members,
        "all_members": all_members
    })

    data_store.set(store)

    return {
        'channel_id': channel_id,
    }
