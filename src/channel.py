from pytest import raises
from src.data_store import data_store
from src.admin import check_user_valid
from src.error import InputError, AccessError
from src.token_helpers import validate_jwt, INVALID_TOKEN
from src.other import OWNER_PERMISSION, MEMBER_PERMISSION
from src.helper_functions import channel_find, channel_user_search
import datetime

def channel_invite_v1(token, channel_id, u_id):
    '''
    Invites a user with ID u_id to join a channel with ID channel_id. Once invited,
    the user is added to the channel immediately. In both public and private channels,
    all members are able to invite users.

    Arguments:
        token (string) - string identifying user is logged in.
        channel_id (integer) - The channel id that the new user is being invited to.
        u_id (integer) - The user id of the user who is being invited to join the channel.

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or
                      u_id does not refer to a valid user or u_id refers to a user
                      who is already a member of the channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                      not a member of the channel

    Return Value:
        Returns nothing

    '''

    store = data_store.get()

    channels = store['channels']
    users = store['users']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Raise input error if invited user is not a valid member of seams
    if check_user_valid(u_id) != True:
        raise InputError(description='User not valid')

    # Check if user is in channel and raise an input error if user is found
    channel_user_search(channel_index, u_id, False)

    # Check if the token_user is in the channel and raise an access error if 
    # token_user is not found in the channel
    channel_user_search(channel_index, token_valid_check, True)

    # Create a new dictionary with details of invited user without password to add to channel
    invited_user = users[u_id]
    invited_user_details = {'u_id': invited_user['u_id'],
                            'email': invited_user['email'], 
                            'name_first': invited_user['name_first'],
                            'name_last': invited_user['name_last'],
                            'handle_str': invited_user['handle_str'],
                            'permission_id': invited_user['permission_id'],
                            'profile_img_url': invited_user['profile_img_url'],
                            }

    # If no errors are raised then invited user is allowed to join the channel
    channels[channel_index]['all_members'].append(invited_user_details)
    
   
    # Add notification for invited user
    msg_time = datetime.datetime.now()
    users[u_id]['notifications'].append({
        'channel_id': channel_id,
        'dm_id': -1,
        'notification_message': users[token_valid_check]['handle_str'] + " added you to " + channels[channel_id]['name'],
        'time_notified': msg_time.timestamp()
    })

    data_store.set(store)

    return {
    }

def channel_details_v1(token, channel_id):
    ''' 
    Generates dictionary containing information about channel if user is a part of channel

     Arguments:
        token (string) - string identifying user is logged in.
        channel_id (integer) - integer identifying channel

    Exceptions:
        InputError - Occurs when channel_id don't exist in data_store
        AccessError - Occurs when token is invalid or no user with id auth_user_id is in channel with id channel_id

    Return Value:
        Returns dictionary containing { name, is_public, owner_members, all_members } on the 
        condition that no exceptions are thrown.
    
    
    '''
    
    store = data_store.get()

    channels = store['channels']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)
    
    #Assign channel variable
    channel = channels[channel_index]

    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)

    # Create return value from channels dictionary without channel id
    owner_members = channel['owner_members']
    all_members = channel['all_members']
    details = {"name": channel['name'],
               "is_public": channel['is_public'],
               "owner_members": [{data:member[data] for data in member if (data != 'permission_id')} for member in owner_members],
               "all_members": [{data:member[data] for data in member if (data != 'permission_id')} for member in all_members]}
    return details
    

def channel_messages_v1(token, channel_id, start):
    '''
    Returns upto 50 messages from an index starting with the most recent message.

    Return Type: 
        {messages, start, end} Here start and end are index position of messages.
    
    Arguments: 
        auth_user_id (integer) - The user is of the authorised user requesting messages
        channel_id (integer) - The channel id of the messages being requested from
        start (integer) - Refers to the starting message with 0 meaning most recent message
    
    Exceptions: 
        InputError: When channel_id is invalid or starting index is greater than the total number of messages in the channel. 
        AccessError: channel_id is valid however the authorised user is not a member of the channel.
    '''
    
    store = data_store.get()

    messages = store['messages']

    # Check if the given token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)

    if len(messages) < start:
        raise InputError(description='Invalid start')
    
    channel_messages = []

    for message in messages:
        if message['c_id'] == channel_id:
            channel_messages.append({data:message[data] for data in message if (data != 'c_id' and data != 'dm_id' and data != 'time_notified')})
   
    #Check the number of messages and assign a value to end accordingly
    channel_messages.reverse()
    if len(channel_messages) - start < 50:
        end = -1  
        channel_messages = channel_messages[start:]
    else:
        end = start + 50
        channel_messages = channel_messages[start:end]

    # Add is_this_user_reacted to each message in list
    for message in channel_messages:
        for react in message['reacts']:
            if token_valid_check in react['u_ids']:
                react['is_this_user_reacted'] = True
            else: react['is_this_user_reacted'] = False

    return {'messages': channel_messages,
        'start': start,
        'end': end}


def channel_join_v1(token, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.

    Arguments:
        token (string) - string identifying user is logged in.
        channel_id (integer) - The channel id of the channel that the user is trying to join.

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel or
                      the authorised user is already a member of the channel
        AccessError - Occurs when channel_id refers to a channel that is private and the 
                      authorised user is not already a channel member and is not a global owner

    Return Value:
        Returns nothing

    '''

    store = data_store.get()

    channels = store['channels']
    users = store['users']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Check if user is in channel and raise an input error if user is found
    channel_user_search(channel_index, token_valid_check, False)

    # Check if the channel is private and if it is ensure user is an owner 
    # in order to join
    if channels[channel_index]['is_public'] == False:
        if users[token_valid_check]['permission_id'] != OWNER_PERMISSION:
            raise AccessError(description='Private channel requires owner permission')

    # Create a new dictionary with details of new user without password to add to channel
    new_user = users[token_valid_check]
    new_user_details = {'u_id': new_user['u_id'],
                        'email': new_user['email'], 
                        'name_first': new_user['name_first'],
                        'name_last': new_user['name_last'],
                        'handle_str': new_user['handle_str'],
                        'permission_id': new_user['permission_id'],
                        'profile_img_url': new_user['profile_img_url'],
                        }

    # If no errors are raised then user is allowed to join the channel
    channels[channel_id]['all_members'].append(new_user_details)

    data_store.set(store)

    return {
    }

def channel_leave_v1(token, channel_id):
    ''' 
    Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the 
    channel. Their messages should remain in the channel. If the only channel owner leaves, 
    the channel will remain.

     Arguments:
        token (string) - string identifying user is logged in.
        channel_id (integer) - integer identifying channel

    Exceptions:
        InputError - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns nothing
    '''    

    store = data_store.get()

    channels = store['channels']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)

    # If there are no errors raised then user details are deleted in 'all_members'
    index = 0
    for member in channels[channel_index]['all_members']:
        if member['u_id'] == token_valid_check:
            channels[channel_index]['all_members'].pop(index)
        index += 1

    # Then user details are deleted in 'owner_members'
    index = 0
    for owner in channels[channel_index]['owner_members']:
        owner_find = owner['u_id']
        if owner_find == token_valid_check:
            channels[channel_index]['owner_members'].pop(index)
            break
        index += 1

    data_store.set(store)

    return {
    }

def channel_addowner_v1(token, channel_id, u_id):
    '''
    Adds user with auth_user_id u_id as owners list to channel specified by channel_id and gives them owner permissions in that channel.

    Arguments:
        token (string) - string identifying user is logged in.
        channel_id (integer) - The channel id that the user from u_id is becoming owner of.
        u_id (integer) - The user id of the user who is being made owner of the channel.

    Exceptions:
        InputError when any of:
        - channel_id does not refer to a valid channel
        - u_id does not refer to a valid user
        - u_id refers to a user who is not a member of the channel
        - u_id refers to a user who is already an owner of the channel
      
      AccessError when:
        - channel_id is valid and the authorised user does not have owner permissions in the channel
        - token is invalid

    Return Value:
        Returns nothing
    '''
    store = data_store.get()

    channels = store['channels']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Make channel variable
    channel = channels[channel_index]
    all_members = channel['all_members']
    owner_members = channel['owner_members']

    if check_user_valid(u_id) != True:
        raise InputError(description='User not valid')

    # Check if user is in channel and raise InputError otherwise
    finding_user = -1
    for count, member in enumerate(all_members):
        if member['u_id'] == u_id:
            finding_user = count
            break
    if finding_user == -1:
        raise InputError(description='User not found')

    # Check if user is already owner of channel and raise InputError otherwise
    found_owner = False
    for member in owner_members:
        if member['u_id'] == u_id:
            found_owner = True
            break
    if found_owner == True:
        raise InputError(description='User is already owner')

    # Check if the token_user is in channel and has owner_permissions and raise AccessError otherwise
    token_user_has_owner_permissions = False
    for member in all_members:
        if member['u_id'] == token_valid_check and member['permission_id'] == OWNER_PERMISSION:
            token_user_has_owner_permissions = True
            break
    if token_user_has_owner_permissions == False:
        raise AccessError(description='Token_user requires owner permission')

    # If no errors are raised set permission of user in all_members as owner permission
    all_members[finding_user]['permission_id'] = OWNER_PERMISSION

    # Add user to owner members list
    channel['owner_members'].append(all_members[finding_user])
    
    data_store.set(store)

    return {
    }

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    Removes user with u_id from owners list to channel specified by channel_id and gives them 
    member permissions in that channel.

    Arguments:
        token (string) - string identifying user is logged in.
        channel_id (integer) - The channel id that the user from u_id is being removed from being an owner of.
        u_id (integer) - The user id of the user who is being removed as an owner of the channel.

    Exceptions:
        InputError when any of:
        - channel_id does not refer to a valid channel
        - u_id does not refer to a valid user
        - u_id refers to a user who is not an owner of the channel
        - u_id refers to a user who is the only owner of the channel
      
      AccessError when:
        - channel_id is valid and the authorised user does not have owner permissions in the channel
        - token is invalid

    Return Value:
        Returns nothing
    '''
    store = data_store.get()

    channels = store['channels']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Make channel variable
    channel = channels[channel_index]
    all_members = channel['all_members']
    owner_members = channel['owner_members']

    if check_user_valid(u_id) != True:
        raise InputError(description='User not valid')

    
    # Check if auth user is currently an owner of channel
    token_user_has_owner_permissions = False
    for member in all_members:
        if member['u_id'] == token_valid_check and member['permission_id'] == OWNER_PERMISSION:
            token_user_has_owner_permissions = True
            break
    if token_user_has_owner_permissions == False:
        raise AccessError(description='User_id requires owner permission')
    
    # check if u_id is currently an owner of channel
    removing_owner = False
    for member in all_members:
        if member['u_id'] == u_id and member['permission_id'] == OWNER_PERMISSION:
            removing_owner = True
            break
    if removing_owner == False:
        raise InputError(description='User_id does not have owner permissions')

    # check if only owner is being removed.
    if len(owner_members) == 1 and removing_owner == True:
        raise InputError(description='Only owner can not be removed')
    
    # If no errors are raised set permission of user in all_members as member permission
    all_members[u_id]['permission_id'] = MEMBER_PERMISSION

    # Add user to owner members list
    channel['owner_members'].pop(u_id)
    
    data_store.set(store)

    return {
    }
