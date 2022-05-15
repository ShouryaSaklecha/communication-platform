from src.error import InputError

def echo(value):
    if value == 'echo':
        raise InputError(description='Input cannot be echo')
    return value
