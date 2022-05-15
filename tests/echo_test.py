import pytest
import requests
import json
from src import config
from src.echo import echo
from src.error import InputError, INPUT_ERROR, VALID_STATUS
from tests.routes_test import URL_echo
from src.echo import echo
from src.error import InputError

def test_VALID_STATUS_echo():
    response = requests.get(URL_echo, params={'data': "hello"})
    assert json.loads(response.text) == {'data': "hello"}
    response.status_code == VALID_STATUS

def test_INPUT_ERROR_echo():
    response = requests.get(URL_echo, params={'data': "echo"})
    assert response.status_code == INPUT_ERROR

'''
OLD TESTS
def test_echo():
    assert echo("1") == "1", "1 == 1"
    assert echo("abc") == "abc", "abc == abc"
    assert echo("trump") == "trump", "trump == trump"


def test_echo_except():
    with pytest.raises(InputError):
        assert echo("echo")

'''