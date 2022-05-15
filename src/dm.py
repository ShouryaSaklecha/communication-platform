from pytest import raises
from src.data_store import data_store
from src.error import InputError, AccessError
from src.admin import check_user_valid
from src.token_helpers import validate_jwt, INVALID_TOKEN
from src.other import OWNER_PERMISSION, MEMBER_PERMISSION
from src.helper_functions import dm_find, dm_user_search
import datetime
from typing import List, Dict, Union

def dm_create_v1(token: str, u_ids: List[int]) -> Dict[str, int]:
    ''' 
    Generates dm_id and name of dm, makes creator owner of dm, adds other users, and returns dm_id.

     Arguments:
        token (string) - string identifying user is logged in.
        u_ids (list of integers) - list of user ids to be invited to dm

    Exceptions:
        InputError - any u_id in u_ids does not refer to a valid user or
        there are duplicate 'u_id's in u_ids

    Return Value:
        Returns dm_id in dictionary on the condition that no exceptions are thrown.
    '''

    store = data_store.get()

    users = store['users']
    dms = store['dms']
    
    # Check if token is invalid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if any u_id in u_ids is invalid
    for u_id in u_ids:
        if check_user_valid(u_id) != True:
            raise InputError(description='User not valid')
            
    # Check for duplicates
    if len(u_ids) != len(set(u_ids)):
        raise InputError(description='Duplicate u_id')

    # Generate dm_id
    dm_id = len(dms)
    
    # Make members list with all users and give creator owner permission
    creator = users[token_valid_check]
    creator_details = {'u_id': creator['u_id'],
                      'email': creator['email'], 
                      'name_first': creator['name_first'],
                      'name_last': creator['name_last'],
                      'handle_str': creator['handle_str'],
                      'permission_id': OWNER_PERMISSION,
                      'profile_img_url': creator['profile_img_url'],
                      }
    members = [creator_details]
    for u_id in u_ids:
        user = users[u_id]
        members.append(
            {'u_id': user['u_id'],
             'email': user['email'], 
             'name_first': user['name_first'],
             'name_last': user['name_last'],
             'handle_str': user['handle_str'],
             'permission_id': MEMBER_PERMISSION,
             'profile_img_url': user['profile_img_url'],
            })

    # Make name for dm
    handle_list = [users[token_valid_check]['handle_str']]
    for u_id in u_ids:
        handle_list.append(users[u_id]['handle_str'])
    sorted_handle_list = sorted(handle_list)
    name = ", ".join(sorted_handle_list)

    # Store all data as a dictionary

    dms.append({
        "dm_id": dm_id,
        "name": name,
        "members": members
    })

    # Add notification for invited user
    msg_time = datetime.datetime.now()
    for u_id in u_ids:
        users[u_id]['notifications'].append({
            'channel_id': -1,
            'dm_id': dm_id,
            'notification_message': users[token_valid_check]['handle_str'] + " added you to " + name,
            'time_notified': msg_time.timestamp()
        })

    data_store.set(store)

    return {
        'dm_id': dm_id,
    }

def dm_details_v1(token, dm_id):
    ''' 
    Generates dictionary containing information about dm if user is a part of dm

     Arguments:
        token (string) - string identifying user is logged in.
        dm_id (integer) - integer identifying dm

    Exceptions:
        InputError - Occurs when dm_id don't exist in data_store
        AccessError - Occurs when token is invalid or no user with id auth_user_id is in dm with id dm_id

    Return Value:
        Returns dictionary containing { name, is_public, owner_members, all_members } on the 
        condition that no exceptions are thrown.
    
    
    '''
    
    store = data_store.get()

    dms = store['dms']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if dm id is in dms and assign dm variable
    dm_index = dm_find(dm_id)
    
    dm = dms[dm_index]

    # Check if user is in dm and raise an access error if user is not found
    dm_user_search(dm_index, token_valid_check, True)

    # Create return value from dms dictionary without permission id in members list
    members = dm['members']
    return {"name": dm['name'],
            "members": [{data:member[data] for data in member if (data != 'permission_id')} for member in members]}


def dm_leave_v1(token, dm_id):
    ''' 
    Given a DM ID, the user is removed as a member of this DM. The creator 
    is allowed to leave and the DM will still exist if this happens. This does not
    update the name of the DM.

     Arguments:
        token (string) - string identifying user is logged in.
        dm_id (integer) - an integer identifying the dm.

    Exceptions:
        InputError - dm_id does not refer to a valid DM.
        AccessError - dm_id is valid and the authorised user is not a member of the DM
         or token is invalid

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()

    dms = store['dms']

    # Check if token is invalid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given dm_id is valid and raise a input error otherwise
    dm_index = dm_find(dm_id)

    # Check if user is in dm and raise an access error if user is not found
    user_index = dm_user_search(dm_index, token_valid_check, True)

    dms[dm_index]['members'].pop(user_index)

    data_store.set(store)

    return {
    }

def dm_list_v1(token):
    '''
    Lists all dms that a user is part of, returning a list of these dms.

     Arguments:
        token (string) - string identifying user is logged in.

    Exceptions:
        AccessError - occurs when token is invalid

    Return Value:
        Returns dictionary dms on the condition that no exceptions are thrown.
    '''
    store = data_store.get()

    dms = store['dms']
    
    # If authorised user id is not a valid id then an access error is raised
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Search for dms that contain the user's id
    dms_list = []

    for dm in dms:
        members = dm["members"]
        for user in members:
            id = user["u_id"]
            # Add to dm_dict
            if id == token_valid_check:
                dm_dict = {
                    'dm_id': dm["dm_id"],
                    'name': dm["name"]
                }
                dms_list.append(dm_dict)

    data_store.set(store)

    return { 'dms': dms_list
    }

def dm_messages_v1(token, dm_id, start):
    '''
    Returns upto 50 messages from an index starting with the most recent message.

    Return Type: 
        {messages, start, end} Here start and end are index position of messages.
    
    Arguments: 
        auth_user_id (integer) - The user is of the authorised user requesting messages
        dm_id (integer) - The dm id of the messages being requested from
        start (integer) - Refers to the starting message with 0 meaning most recent message
    
    Exceptions: 
        InputError: When dm_id is invalid or starting index is greater than the total number of messages in the dm. 
        AccessError: dm_id is valid however the authorised user is not a member of the dm.
    '''
    
    store = data_store.get()

    messages = store['messages']

    # Check if the token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given dm_id is valid and raise input error 
    # if dm_id does not refer to a valid dm
    dm_index = dm_find(dm_id)

    # Check if user is in dm and raise an access error if user is not found
    dm_user_search(dm_index, token_valid_check, True)

    if len(messages) < start:
        raise InputError(description='Invalid start')
    
    dm_messages = []

    for message in messages:
        if message['dm_id'] == dm_id:
            dm_messages.append({data:message[data] for data in message if (data != 'c_id' and data != 'dm_id' and data != 'time_notified')})
   
    #Check the number of messages and assign a value to end accordingly
    dm_messages.reverse()
    if len(dm_messages) - start < 50:
        end = -1  
        dm_messages = dm_messages[start:]
    else:
        end = start + 50
        dm_messages = dm_messages[start:end]

    # Add is_this_user_reacted to each message in list
    for message in dm_messages:
        for react in message['reacts']:
            if token_valid_check in react['u_ids']:
                react['is_this_user_reacted'] = True
            else: react['is_this_user_reacted'] = False

    return {'messages': dm_messages,
        'start': start,
        'end': end}

def dm_remove_v1(token, dm_id):
    ''' 
    Remove an existing DM, so all members are no longer in the DM.
    This can only be done by the original creator of the DM.

     Arguments:
        token (string) - string identifying user is logged in.
        dm_id (integer) - an integer identifying the dm.

    Exceptions:
        InputError - dm_id does not refer to a valid DM.
        AccessError - dm_id is valid and the authorised user is not 
        the original DM creator or dm_id is valid and the authorised user
        is no longer in the DM or token is invalid

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()

    dms = store['dms']

    # Check if token is invalid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given dm_id is valid and raise an input error otherwise
    dm_index = dm_find(dm_id)

    # Check if the given token_user is in the dm and a creator and raise an 
    # access error otherwise
    creator_found = False
    for member in dms[dm_index]['members']:
        if member['u_id'] == token_valid_check and member['permission_id'] == OWNER_PERMISSION:
            creator_found = True
            break
    if creator_found == False:
        raise AccessError(description='User is not creator or not in the dm')

    # If no errors are raised then the dm with dm_id is removed
    del dms[dm_index]

    data_store.set(store)

    return {
    }
