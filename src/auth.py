from src.token_helpers import generate_jwt, validate_jwt, decode_jwt, INVALID_TOKEN
from pytest import raises
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import OWNER_PERMISSION, MEMBER_PERMISSION, GENERIC_PROFILE_URL
import hashlib
import random
import re
from typing import Union, Dict

def auth_login_v1(email: str, password: str) -> Dict[str, Union[str, int]]:
    '''
    Returns u_id for a specific user

    Arguments:
        email (string) - string containing users email.
        password (string) - string containing users password.

    Exceptions:
        InputError - Occurs when email is not found/stored,
        password is not correct for given email.

    Return Value:
        Returns auth_user_id on the condition that no exceptions are thrown.
    '''
    # check if email registered before or list is empty.
    store = data_store.get()

    users = store['users']

    finding_user = -1
    if users:
        for x in users:
            check_email = x['email']
            if check_email == email:
                finding_user = x['u_id']
    else:
        raise InputError(description='Users not found in datastore')

    if finding_user == -1:
        raise InputError(description='Invalid u_id')

    # check if password matches
    attempting_login = users[finding_user]
    stored_password = attempting_login['password']

    if hashlib.sha256(password.encode()).hexdigest() != stored_password:
        raise InputError(description='Invalid password')
    else:
        auth_user_id = attempting_login['u_id']

    new_token = generate_jwt(auth_user_id)

    return {
        'token': new_token,
        'auth_user_id': auth_user_id,
    }

def auth_register_v1(email: str, password: str, name_first: str, name_last: str) -> Dict[str, Union[str, int]]:
    '''
    Generates u_id and handle, stores data in a dictionary and returns u_id.

    Arguments:
        email (string) - string containing users email.
        password (string) - string containing users password.
        name_first (string) - string containing users first name.
        name_last (string) - string containing users last name.

    Exceptions:
        InputError - Occurs when email is invalid format or not unique,
        password is less than 6 characters, name_first and name_last
        aren't between 1 and 50 characters inclusive.

    Return Value:
        Returns auth_user_id on the condition that no exceptions are thrown.
    '''

    # check email is valid, not a duplicate
    valid = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not (re.fullmatch(valid, email)):
        raise InputError(description='Invalid email')

    store = data_store.get()
    
    users = store['users']

    if users:
        for x in users:
            check_email = x['email']
            if check_email == email:
                raise InputError(description='Email same as current set email')

    # check password is valid
    if len(password) < 6:
        raise InputError(description='Invalid password length (Too short)')

    # check name_first and name_last are valid
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description='Invalid first name length')

    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description='Invalid last name length')

    # generate handle + unique check
    handle = name_first + name_last
    handle = re.sub(r'\W+', '', handle)
    handle = handle[:20]
    handle = handle.lower()
    modified_handle = handle

    if users:
        additional = 0
        for x in users:
            check_handle = x['handle_str']
            if check_handle == modified_handle:
                modified_handle = handle + str(additional)
                additional = additional + 1
    
    # generate u_id
    auth_user_id = len(users)

    # give global owner permissions to first user to register
    if auth_user_id == 0:
        permission_id = OWNER_PERMISSION
    else:
        permission_id = MEMBER_PERMISSION

    # store all data as a dictionary
    users.append({
        "u_id": auth_user_id,
        "email": email,
        "name_first": name_first,
        "name_last": name_last,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "handle_str": modified_handle,
        "profile_img_url": GENERIC_PROFILE_URL,
        "permission_id": permission_id,
        "notifications": [],
    })

    data_store.set(store)

    new_token = generate_jwt(auth_user_id)

    # return u_id as auth_user_id
    return {
        'token': new_token,
        'auth_user_id': auth_user_id,
    }

def auth_logout_v1(token: str):
    '''  
    Purpose:
        Logout user and invalidate token.
    
    Parameters:
        token
    
    Return Type:
        NA
    
    AccessError:
        token is invalid 
    
    '''
    token_valid_check = validate_jwt(token)
    if token_valid_check == INVALID_TOKEN:
        raise AccessError(description='Invalid token')
    
    token_info = decode_jwt(token)

    store = data_store.get()
    users = store['users']
    logged_in_user = users[token_valid_check]

    current_session = token_info['session_id']
    logged_in_user['sessions'].remove(current_session)

    data_store.set(store)

def auth_passwordreset_request_v1(email: str):
    '''  
    Purpose:
        Generates random 5-digit code to be used as a reset code.
    
    Parameters:
        email
    
    Return Type:
        NA
    '''
    # generates a random code
    store = data_store.get()
    users = store['users']
    stored_codes = store['codes']
    code = ''

    unique_code = False
    while unique_code == False:
        code_list = []
        i = 0
        while i < 5:
            code_list.append(random.randint(0,5))
            i += 1
        code = ''.join([str(digit) for digit in code_list])

        checked_all_unique = True
        for stored_code in stored_codes:
            if stored_code['code'] == code:
                checked_all_unique = False
        if checked_all_unique == True:
            unique_code = True
    
    # check email belongs to a user, record user_id
    email_valid = False
    user_id = -1
    for user in users:
        if user['email'] == email:
            user_id = user['u_id']
            email_valid = True
    
    if email_valid == True:
        stored_codes.append({
            'code': code,
            'email': email
        })
        users[user_id]["sessions"] = []
        data_store.set(store)
        return code
    else:
        return False
    
def auth_passwordreset_reset_v1(reset_code: str, new_password:str):
    '''  
    Purpose:
        Changes user from reset_code's password to new_password.
    
    Parameters:
        reset_code, new_password
    
    Return Type:
        NA
    
    InputError:
        reset_code in invalid
        new_password is less than 6 characters 
    '''
    store = data_store.get()
    users = store['users']
    stored_codes = store['codes']
    requestor_email = ''

    checked_all_valid = False
    for stored_code in stored_codes:
        if stored_code['code'] == reset_code:
            checked_all_valid = True
            requestor_email = stored_code['email']
    if checked_all_valid == False:
        raise InputError(description='Reset code invalid')
    if len(new_password) < 6:
        raise InputError(description='Password too short')

    finding_user = -1
    if users:
        for user in users:
            check_email = user['email']
            if check_email == requestor_email:
                finding_user = user['u_id']
    resetting_user = users[finding_user]
    resetting_user["password"] = hashlib.sha256(new_password.encode()).hexdigest()
    data_store.set(store)
