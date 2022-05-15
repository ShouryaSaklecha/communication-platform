from pytest import fixture
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.data_store import data_store
from src.token_helpers import *

def test_session_1(clear):
    first_user = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    store = data_store.get()
    users = store['users']
    user = users[first_user["auth_user_id"]]
    assert user["sessions"] == [1]

def test_session_2(clear):
    first_user = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    auth_login_v1('newemail@gmail.com', 'password')
    store = data_store.get()
    users = store['users']
    user = users[first_user["auth_user_id"]]
    assert user["sessions"] == [1,2]

def test_return_id(clear):
    first_user = auth_register_v1('newemail@gmail.com', 'password', 'John', 'Smith')
    new_jwt = generate_jwt(first_user["auth_user_id"])
    returns = validate_jwt(new_jwt)
    assert returns == 0