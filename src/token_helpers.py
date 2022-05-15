from src.data_store import data_store
import jwt

SECRET = 'CAMEL'
INVALID_TOKEN = -1

def generate_new_session(auth_user_id: int):
    '''  
    Purpose:
        generate new session for auth id
    
    Parameters:
        auth_user_id
    
    Return Type:
        new_session
    
    '''
    store = data_store.get()
    users = store['users']
    user = users[auth_user_id]
    if "sessions" not in user.keys():
        user["sessions"] = []

    session_list = user["sessions"]
    num_sessions = len(session_list)
    new_session = num_sessions + 1
    session_list.append(new_session)

    data_store.set(store)

    return new_session

def generate_jwt(auth_user_id: int):
    session_num = generate_new_session(auth_user_id)
    return jwt.encode({"auth_user_id": auth_user_id,
     "session_id": session_num}, SECRET, algorithm='HS256')

def decode_jwt(encoded_jwt):
    try:
        decoded =  jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    except(jwt.InvalidTokenError):
        return INVALID_TOKEN
    return decoded

def validate_jwt(encoded_jwt):
    '''  
    Purpose:
        validate current token
    
    Parameters:
        encoded_jwt
    
    Return Type:
        auth_user_id
    
    '''
    jwt_info = decode_jwt(encoded_jwt)
    if jwt_info == INVALID_TOKEN:
        return INVALID_TOKEN
    current_session = jwt_info["session_id"]
    current_id = jwt_info["auth_user_id"]

    store = data_store.get()
    users = store['users']
    user = users[current_id]
    user_sessions = user["sessions"]
    if current_session in user_sessions:
        return current_id
    else:
        return INVALID_TOKEN