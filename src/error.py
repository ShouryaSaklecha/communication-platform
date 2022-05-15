from werkzeug.exceptions import HTTPException

ACCESS_ERROR = 403
VALID_STATUS = 200
INPUT_ERROR = 400

class AccessError(HTTPException):
    code = ACCESS_ERROR
    message = 'No message specified'

class InputError(HTTPException):
    code = INPUT_ERROR
    message = 'No message specified'
