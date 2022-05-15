from calendar import c
from operator import index
from re import L
from pytest import raises
import datetime
import threading
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import THUMBS_UP_REACT
from src.token_helpers import validate_jwt, INVALID_TOKEN
from src.other import OWNER_PERMISSION, MEMBER_PERMISSION
from src.helper_functions import channel_find, channel_user_search, dm_find, dm_user_search
from src.channel import channel_messages_v1


def message_send_v1(token, channel_id, message):
    '''  
    Purpose:
        Sends a message from authorised user to the channel specified by the channel_id. 
    
    Parameters:
        token, channel_id, message
    
    Return Type:
        message_id
    
    InputError:
      channel_id does not refer to a valid channel
      length of message is less than 1 or over 1000 characters  
    
    AccessError:
      channel_id is valid and the authorised user is not a member of the channel  
    
    
    '''
    store = data_store.get()

    messages = store['messages']
    
    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
 
    #Raise input error if the message length is nto appropriate:
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Invalid message length')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)
    
    # Getting in a message ID: 
    '''
    The idea is to generate a message_id, suhc that it corresponds its first digit as channel_id +1 1(To avoid the zero error), 
    followed by the index of the message, which will always be unique

    message_id type = int
    
    '''
    messages_length = len(messages)
    if messages_length == 0:
        message_id = 0
    else:
        currently_newest = messages[messages_length - 1]
        if currently_newest['message_id'] == -1:
            message_id = currently_newest['future_message_id'] + 1
        else:
            message_id = currently_newest['message_id'] + 1
            
    # Getting the instantaneous time when this function is called:
    # The time when this function is called is equivalent to time sent
    msg_time = datetime.datetime.now()
    messages.append(
            {
            'c_id' : channel_id,
            'dm_id': -1,
            'message_id' : message_id,
            'u_id' : token_valid_check,
            'message': message,
            'time_sent' : int(msg_time.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": []}],
            'is_pinned': False,
            'time_notified': msg_time.timestamp()
            })
    
    data_store.set(store)
    
    return {'message_id': message_id}

def message_edit_v1(token, message_id, message):
    '''
    Purpose: Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
    
    Return Type: NIL

    INPUT ERROR: 
        length of message is over 1000 characters
        message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    
    ACCESS ERROR:
        message_id refers to a valid message in a joined channel/DM and none of the following are true:
            the message was sent by the authorised user making this request
            the authorised user has owner permissions in the channel/DM

    '''

    store = data_store.get()

    channels = store['channels']
    messages = store['messages']
    dms = store['dms']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description="Invalid token")

    #Raise input error if the message length is not appropriate:
    remove = False
    if len(message) > 1000:
        raise InputError(description="message too long")

    elif len(message) < 1:
        remove = True

    # Check if channel exists
    channel_id = -1
    dm_id = -1
    message_sender = -1
    message_index = 0
    for current_message in messages:
        if current_message['message_id'] == message_id:
            channel_id = current_message['c_id']
            dm_id = current_message['dm_id']
            message_sender = current_message['u_id']
            break
        message_index += 1
    if message_sender == -1:
        raise InputError(description='User not found')

    if channel_id == -1 and dm_id != -1:
        # Check if user is in dm
        finding_user = -1
        user_permissions_owner = False
        for member in dms[dm_id]['members']:
            check_for_user = member['u_id']
            if check_for_user == token_valid_check:
                finding_user = member['u_id']
                if member['permission_id'] == OWNER_PERMISSION:
                    user_permissions_owner = True
                break
        # Raise an access error if user is not found
        if finding_user == -1:
            raise AccessError(description='User not found')
        if message_sender != token_valid_check and user_permissions_owner == False:
            raise AccessError(description='Message sent by another user')
    elif dm_id == -1 and channel_id != -1:
        # Check if user is in channel and check users permissions.
        finding_member = -1
        user_permissions_owner = False
        for member in channels[channel_id]['all_members']:
            check_for_user = member['u_id']
            if check_for_user == token_valid_check:
                finding_member = member['u_id']
                if member['permission_id'] == OWNER_PERMISSION:
                    user_permissions_owner = True
                break
        if finding_member == -1:
            raise InputError(description='Member not found')
        if message_sender != token_valid_check and user_permissions_owner == False:
            raise AccessError(description='Message sent by another user')

    # if no exceptions, edit message with given message.
    if remove == True:
        messages.pop(message_index)
    else:
        messages[message_index]['message'] = message
        msg_time = datetime.datetime.now()
        messages[message_index]['time_notified'] = msg_time.timestamp()

    data_store.set(store)

def message_remove_v1(token, message_id):
    '''
    Purpose: Remove message
    
    Return Type: NIL

    INPUT ERROR: 
        message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    
    ACCESS ERROR:
        message_id refers to a valid message in a joined channel/DM and none of the following are true:
            the message was sent by the authorised user making this request
            the authorised user has owner permissions in the channel/DM

    '''

    store = data_store.get()

    channels = store['channels']
    messages = store['messages']
    dms = store['dms']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
    
    # Check if channel exists
    channel_id = -1
    dm_id = -1
    message_sender = -1
    message_index = 0
    for current_message in messages:
        if current_message['message_id'] == message_id:
            channel_id = current_message['c_id']
            dm_id = current_message['dm_id']
            message_sender = current_message['u_id']
            break
        message_index += 1
    if message_sender == -1:
        raise InputError(description='User not found')

    if channel_id == -1 and dm_id != -1:
        # Check if user is in dm
        finding_user = -1
        user_permissions_owner = False
        for member in dms[dm_id]['members']:
            check_for_user = member['u_id']
            if check_for_user == token_valid_check:
                finding_user = member['u_id']
                if member['permission_id'] == OWNER_PERMISSION:
                    user_permissions_owner = True
                break
        # Raise an access error if user is not found
        if finding_user == -1:
            raise AccessError(description='User not found')
        if message_sender != token_valid_check and user_permissions_owner == False:
            raise AccessError(description='Message sent by another user')
    elif dm_id == -1 and channel_id != -1:
        # Check if user is in channel and check users permissions.
        finding_member = -1
        user_permissions_owner = False
        for member in channels[channel_id]['all_members']:
            check_for_user = member['u_id']
            if check_for_user == token_valid_check:
                finding_member = member['u_id']
                if member['permission_id'] == OWNER_PERMISSION:
                    user_permissions_owner = True
                break
        if finding_member == -1:
            raise InputError(description='Member not found')
        if message_sender != token_valid_check and user_permissions_owner == False:
            raise AccessError(description='Message sent by another user')

    #if not exceptions thrown, remove message.

    messages.pop(message_index)
    data_store.set(store)

def message_senddm_v1(token, dm_id, message):
    '''  
    Purpose:
        Sends a message from authorised user to the dm specified by the dm_id. 
    
    Parameters:
        token, dm_id, message
    
    Return Type:
        message_id
    
    InputError:
      dm_id does not refer to a valid dm
      length of message is less than 1 or over 1000 characters  
    
    AccessError:
      dm_id is valid and the authorised user is not a member of the dm  
    '''

    store = data_store.get()

    messages = store['messages']

    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
 
    # Raise input error if the message length is not appropriate:
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Invalid message length')

    # Check if the given dm_id is valid and raise an input error otherwise
    dm_index = dm_find(dm_id)

    # Check if user is in dm and raise an access error if user is not found
    dm_user_search(dm_index, token_valid_check, True)
    
    # Getting in a message ID: 
    '''
    The idea is to generate a message_id, suhc that it corresponds its first digit as dm_id +1 1(To avoid the zero error), 
    followed by the index of the message, which will always be unique

    message_id type = int
    
    '''
    messages_length = len(messages)
    if messages_length == 0:
        message_id = 0
    else:
        currently_newest = messages[messages_length - 1]
        if currently_newest['message_id'] == -1:
            message_id = currently_newest['future_message_id'] + 1
        else:
            message_id = currently_newest['message_id'] + 1
            
    # Getting the instantaneous time when this function is called:
    # The time when this function is called is equivalent to time sent
    msg_time = datetime.datetime.now()
    messages.append(
            {
            'c_id' : -1,
            'dm_id': dm_id,
            'message_id' : message_id,
            'u_id' : token_valid_check,
            'message': message,
            'time_sent' : int(msg_time.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": []}],
            'is_pinned': False,
            'time_notified': msg_time.timestamp()
            })
    
    data_store.set(store)
    
    return {'message_id': message_id}

def message_pin_v1(token, message_id):
    '''  
    Purpose:
        Given a message within a channel or DM, mark it as "pinned". 
    
    Parameters:
        token, message_id
    
    Return Type:
        Returns nothing
    
    InputError:
      - message_id is not a valid message within a channel or DM 
      that the authorised user has joined
      - the message is already pinned
    
    AccessError:
      - message_id refers to a valid message in a joined 
      channel/DM and the authorised user does not have owner permissions
      in the channel/DM
      - Invalid token

    '''
    
    store = data_store.get()

    channels = store['channels']
    dms = store['dms']
    messages = store['messages']

    # Check if token is valid otherwise raise an access error
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check is message_id is valid otherwise raise an input error
    # Check if the message is not pinned otherwise raise an input error
    message_found = False
    message_pinned = False
    for current_message in messages:
        if current_message['message_id'] == message_id:
            curr_message = current_message
            message_found = True
            if current_message['is_pinned'] == True:
                message_pinned = True
            break
    
    if message_found == False:
        raise InputError(description='Invalid message_id')

    c_id = -1
    dm_id = -1
    if curr_message['c_id'] != -1:
        c_id = curr_message['c_id']
    elif curr_message['dm_id'] != -1:
        dm_id = curr_message['dm_id']

    member_found = False
    if c_id != -1:
        for member in channels[c_id]['all_members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break

    if member_found == False:
        raise InputError(description='User not in channel/dm')
    elif message_pinned == True:
        raise InputError(description='Message already pinned')

    # Check if the token_user has owner permissions in the channel/dm
    # otherwise raise an access error
    owner_permission = False
    if c_id != -1:
        for member in channels[c_id]['all_members']:
            permission_id = member['permission_id']
            if member['u_id'] == token_valid_check and permission_id == OWNER_PERMISSION:
                owner_permission = True
                break
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            permission_id = member['permission_id']
            if member['u_id'] == token_valid_check and permission_id == OWNER_PERMISSION:
                owner_permission = True
                break
    
    if owner_permission == False:
        raise AccessError(description='User does not have permission')

    # If no errors are raised, then pin the message
    for current_message in messages:
        if current_message['message_id'] == message_id:
            current_message['is_pinned'] = True
            break

    data_store.set(store)
    
    return {}

def message_unpin_v1(token, message_id):
    '''  
    Purpose:
        Given a message within a channel or DM, remove its mark as pinned. 
    
    Parameters:
        token (string) - Authorised user identification string
        message_id (integer) - The id of the message
    
    Return Type:
        Returns nothing
    
    InputError:
      - message_id is not a valid message within a channel or 
      DM that the authorised user has joined
      - the message is not already pinned
    
    AccessError:
      - message_id refers to a valid message in a joined
      channel/DM and the authorised user does not have owner
      permissions in the channel/DM
      - Invalid token

    '''
    
    store = data_store.get()

    channels = store['channels']
    dms = store['dms']
    messages = store['messages']

    # Check if token is valid otherwise raise an access error
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check is message_id is valid otherwise raise an input error
    # Check if the message is pinned otherwise raise an input error
    message_found = False
    message_pinned = True
    for current_message in messages:
        if current_message['message_id'] == message_id:
            curr_message = current_message
            message_found = True
            if current_message['is_pinned'] == False:
                message_pinned = False
            break
    
    if message_found == False:
        raise InputError(description='Invalid message_id')

    c_id = -1
    dm_id = -1
    if curr_message['c_id'] != -1:
        c_id = curr_message['c_id']
    elif curr_message['dm_id'] != -1:
        dm_id = curr_message['dm_id']

    member_found = False
    if c_id != -1:
        for member in channels[c_id]['all_members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break

    if member_found == False:
        raise InputError(description='User not in channel/dm')
    elif message_pinned == False:
        raise InputError(description='Message not already pinned')

    # Check if the token_user has owner permissions in the channel/dm
    # otherwise raise an access error
    owner_permission = False
    if c_id != -1:
        for owner in channels[c_id]['owner_members']:
            permission_id = owner['permission_id']
            if owner['u_id'] == token_valid_check and permission_id == OWNER_PERMISSION:
                owner_permission = True
                break      
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            permission_id = member['permission_id']
            if member['u_id'] == token_valid_check and permission_id == OWNER_PERMISSION:
                owner_permission = True
                break
    
    if owner_permission == False:
        raise AccessError(description='User does not have permission')

    # If no errors are raised, then unpin the message
    for current_message in messages:
        if current_message['message_id'] == message_id:
            current_message['is_pinned'] = False
            break

    data_store.set(store)
    
    return {}

def message_react_v1(token, message_id, react_id):
    '''  
    Purpose:
        Given a message within a channel or DM the authorised user is part of,
        add a "react" to that particular message. 
    
    Parameters:
        token, message_id, react_id
    
    Return Type:
        Returns nothing
    
    InputError:
      - message_id is not a valid message within
      a channel or DM that the authorised user has joined
      - react_id is not a valid react ID - currently, the
      only valid react ID the frontend has is 1
      - the message already contains a react with ID react_id
      from the authorised user
    
    AccessError:
      - Invalid token

    '''
    
    store = data_store.get()

    channels = store['channels']
    dms = store['dms']
    messages = store['messages']
    users = store['users']

    # Check if token is valid otherwise raise an access error
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check react id is valid otherwise raise an input error
    if react_id != THUMBS_UP_REACT:
        raise InputError(description='Invalid react_id')

    # Check is message_id is valid otherwise raise an input error
    # Check if the message has not been reacted to otherwise raise an
    # input error
    message_found = False
    message_reacted = False
    for current_message in messages:
        if current_message['message_id'] == message_id:
            curr_message = current_message
            message_found = True
            break

    for u_id in current_message['reacts'][0]['u_ids']:
        if u_id == token_valid_check:
            message_reacted = True
            break
    
    if message_found == False:
        raise InputError(description='Invalid message_id')

    c_id = -1
    dm_id = -1
    if curr_message['c_id'] != -1:
        c_id = curr_message['c_id']
    elif curr_message['dm_id'] != -1:
        dm_id = curr_message['dm_id']

    member_found = False
    if c_id != -1:
        for member in channels[c_id]['all_members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break

    if member_found == False:
        raise InputError(description='User not in channel/dm')
    elif message_reacted == True:
        raise InputError(description='Message already reacted to')

    # If no errors are raised then react to the message
    curr_message['reacts'][0]['u_ids'].append(token_valid_check)

    # Find user
    user_index = -1
    for count, user in enumerate(users):
        if user['u_id'] == curr_message['u_id']:
            user_index = count
            break
    # Add notification for reacted user
    if c_id != -1:
        name = channels[c_id]['name']
    else:
        name = dms[dm_id]['name']
    msg_time = datetime.datetime.now()
    users[user_index]['notifications'].append({
        'channel_id': c_id,
        'dm_id': dm_id,
        'notification_message': users[token_valid_check]['handle_str'] + " reacted to your message in " + name,
        'time_notified': msg_time.timestamp()
    })

    data_store.set(store)
    
    return {}

def message_unreact_v1(token, message_id, react_id):
    '''  
    Purpose:
        Given a message within a channel or DM the authorised
        user is part of, remove a "react" to that particular message. 
    
    Parameters:
        token, message_id, react_id
    
    Return Type:
        Returns nothing
    
    InputError:
      - message_id is not a valid message within
      a channel or DM that the authorised user has joined
      - react_id is not a valid react ID - currently, the
      only valid react ID the frontend has is 1
      - the message does not contain a react with ID react_id
      from the authorised user
    
    AccessError:
      - Invalid token

    '''
    
    store = data_store.get()

    channels = store['channels']
    dms = store['dms']
    messages = store['messages']

    # Check if token is valid otherwise raise an access error
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check react id is valid otherwise raise an input error
    if react_id != THUMBS_UP_REACT:
        raise InputError(description='Invalid react_id')

    # Check is message_id is valid otherwise raise an input error
    # Check if the message has not been reacted to otherwise raise an
    # input error
    message_found = False
    message_reacted = False
    for current_message in messages:
        if current_message['message_id'] == message_id:
            curr_message = current_message
            message_found = True
            break

    for u_id in current_message['reacts'][0]['u_ids']:
        if u_id == token_valid_check:
            message_reacted = True
            break
    
    if message_found == False:
        raise InputError(description='Invalid message_id')

    c_id = -1
    dm_id = -1
    if curr_message['c_id'] != -1:
        c_id = curr_message['c_id']
    elif curr_message['dm_id'] != -1:
        dm_id = curr_message['dm_id']

    member_found = False
    if c_id != -1:
        for member in channels[c_id]['all_members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            if member['u_id'] == token_valid_check:
                member_found = True
                break

    if member_found == False:
        raise InputError(description='User not in channel/dm')
    elif message_reacted == False:
        raise InputError(description='Message not already reacted to')

    # If no errors are raised then unreact to the message
    for current_message in messages:
        if current_message['message_id'] == message_id:
            current_message['reacts'][0]['u_ids'].pop(token_valid_check)
            break

    data_store.set(store)
    
    return {}

def sending_later(message, message_id, time_sent, channel_id, token_valid_check):
    store = data_store.get()
    messages = store['messages']
    
    update_message = 0
    for stored_message in messages:
        if stored_message['message_id'] == -1:
            if stored_message['future_message_id'] == message_id:
                update_message = stored_message

    update_message.pop("future_message_id")
    update_message.update(
            {
            'message_id' : message_id,
            'message': message,
            'time_sent' : int(datetime.datetime.now().timestamp()),
            'time_notified': time_sent,
            })
    
    data_store.set(store)
    return

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Purpose: Send message in channel at given time.
    
    Parameters:
        token, channel_id, message, time_sent

    Return Type:
        message_id
    
    InputError:
      channel_id does not refer to a valid channel
      length of message is less than 1 or over 1000 characters  
      time_sent is a time in the past
    
    AccessError:
      channel_id is valid and the authorised user is not a member of the channel  
    '''
    store = data_store.get()
    messages = store['messages']
    
 
    #Raise input error if the message length is nto appropriate:
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Invalid message length')
    
    # Check if token is valid
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given chanel_id is valid and raise input error 
    # if channel id does not refer to a valid channel
    channel_index = channel_find(channel_id)

    # Check if user is in channel and raise an access error if user is not found
    channel_user_search(channel_index, token_valid_check, True)

    # check time_sent is not in the past
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_length = time_sent - current_time_int
    if time_length <= 0:
        raise InputError(description='Time must be in the future.')

    messages_length = len(messages)
    if messages_length == 0:
        message_id = 0
    else:
        currently_newest = messages[messages_length - 1]
        if currently_newest['message_id'] == -1:
            message_id = currently_newest['future_message_id'] + 1
        else:
            message_id = currently_newest['message_id'] + 1
            
    # set placer message until time_sent is reached
    messages.append(
            {
            'c_id' : channel_id,
            'dm_id': -1,
            'message_id' : -1,
            'future_message_id': message_id,
            'u_id' : token_valid_check,
            'message': '',
            'time_sent' : 0,
            'reacts': [{"react_id": 1,
                        "u_ids": []}],
            'is_pinned': False,
            'time_notified': 0
            })
    
    data_store.set(store)

    timer = threading.Timer(time_length, sending_later, [message, message_id, time_sent, channel_id, token_valid_check])
    timer.start()
    return {'message_id': message_id}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Purpose:
        Shares the contents of og_message_id to channel_id or dm_id, and return shared_message_id
    
    Parameters:
        token, og_message_id, message, channel_id, dm_id
    
    Return Type:
        shared_message_id
    
    InputError:
      - both channel_id and dm_id are invalid
      - neither channel_id or dm_id are -1
      - og_message_id is not a valid message within
      a channel or DM that the authorised user has joined
      - message length is over 1000 characters
    
    AccessError:
      - Invalid token
      - User is not part of channel_id or dm_id they are sharing message to
    '''
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']
    
    # Check if token is valid otherwise raise an access error
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
    # check message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description='Message too long')

    # check at least one of channel_id or dm_id are -1
    if channel_id != -1 and dm_id != -1:
        raise InputError(description='Both dm and channel IDs are given')

    # check the non -1 id is a valid dm or channel
    channel_found = False
    for channel in channels:
        if channel['c_id'] == channel_id:
            channel_found = True
    dm_found = False
    for dm in dms:
        if dm['dm_id'] == dm_id:
            dm_found = True
    if dm_found == False and channel_found == False:
        raise InputError(description='Invalid dm and channel ID')

    # check the user has joined the valid dm or channel
    if dm_found == True:
        user_in_dm = False
        dm = dms[dm_id]
        for member in dm['members']:
            if member['u_id']== token_valid_check:
                user_in_dm = True
        if user_in_dm == False:
            raise AccessError(description='User not in dm')
    if channel_found == True:
        user_in_channel = False
        channel = channels[channel_id]
        for member in channel['all_members']:
            if member['u_id']== token_valid_check:
                user_in_channel = True
        if user_in_channel == False:
            raise AccessError(description='User not in channel')
            
    # check the user has joined the channel/dm og_message_id is from / og_message_id is valid
    message_found = False
    for current_message in messages:
        if current_message['message_id'] == og_message_id:
            c_id = current_message['c_id']
            dm_id = current_message['dm_id']
            message_contents = current_message['message']
            message_found = True
    if message_found == False:
        raise InputError(description='Message is not found in given channel/dm')
    current_member = False
    if c_id != -1:
        for member in channels[c_id]['all_members']:
            if member['u_id'] == token_valid_check:
                current_member = True      
    elif dm_id != -1:
        for member in dms[dm_id]['members']:
            if member['u_id'] == token_valid_check:
                current_member = True
    if current_member == False:
        raise InputError(description='Message is not found in given channel/dm')

    # get contents of og_message_id, send it with message as a new message in channel/dm -> return message id
    messages_length = len(messages)
    currently_newest = messages[messages_length - 1]
    message_id = currently_newest['message_id'] + 1
    msg_time = datetime.datetime.now()
    messages.append(
            {
            'c_id' : channel_id,
            'dm_id': dm_id,
            'message_id' : message_id,
            'u_id' : token_valid_check,
            'message': '"' + message_contents + '"' + message,
            'time_sent' : int(msg_time.timestamp()),
            'reacts': [{"react_id": 1,
                        "u_ids": []}],
            'is_pinned': False,
            'time_notified': msg_time.timestamp()
            })
    
    data_store.set(store)
    
    return {'shared_message_id': message_id}

def message_sendlater_dm_v1(token, dm_id, message, time_sent):
    '''
    Purpose: Send message in DM at given time.
    
    Parameters:
        token, dm_id, message, time_sent

    Return Type:
        message_id
    
    InputError:
      dm_id does not refer to a valid channel
      length of message is less than 1 or over 1000 characters  
      time_sent is a time in the past
    
    AccessError:
      dm_id is valid and the authorised user is not a member of the channel  
    '''
    store = data_store.get()

    messages = store['messages']
    
 
    #Raise input error if the message length is not appropriate:
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description='Invalid message length')
    
    # Check if token is valid   
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')

    # Check if the given dm_id is valid and raise an input error otherwise
    dm_index = dm_find(dm_id)

    # Check if user is in dm and raise an access error if user is not found
    dm_user_search(dm_index, token_valid_check, True)

    # check time_sent is not in the past
    current_time = datetime.datetime.now()
    current_time_int = int(current_time.timestamp())
    time_length = time_sent - current_time_int
    if time_length <= 0:
        raise InputError(description='Time must be in the future.')

    messages_length = len(messages)
    if messages_length == 0:
        message_id = 0
    else:
        currently_newest = messages[messages_length - 1]
        if currently_newest['message_id'] == -1:
            message_id = currently_newest['future_message_id'] + 1
        else:
            message_id = currently_newest['message_id'] + 1
            
    # set placer message until time_sent is reached
    messages.append(
            {
            'c_id' : -1,
            'dm_id': dm_id,
            'message_id' : -1,
            'future_message_id': message_id,
            'u_id' : token_valid_check,
            'message': '',
            'time_sent' : 0,
            'reacts': [{"react_id": 1,
                        "u_ids": []}],
            'is_pinned': False,
            'time_notified': 0
            })
    
    data_store.set(store)

    timer = threading.Timer(time_length, sending_later, [message, message_id, time_sent, dm_id, token_valid_check])
    timer.start()
    return {'message_id': message_id}
