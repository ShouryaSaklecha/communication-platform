from re import M
import sys
import signal
from json import dumps
from tracemalloc import start
from flask import Flask, request
from flask_mail import Mail, Message
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config
from src.echo import echo
from src.auth import auth_login_v1, auth_logout_v1, auth_register_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.admin import admin_permission_change_v1, admin_remove_user_v1
from src.channels import channels_create_v1, channels_list_v1,channels_listall_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_removeowner_v1 
from src.channel import channel_leave_v1, channel_messages_v1, channel_addowner_v1
from src.other import clear_v1
from src.users import users_all_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src.message import message_edit_v1, message_remove_v1, message_send_v1, message_senddm_v1, message_share_v1
from src.message import message_pin_v1, message_unpin_v1, message_react_v1, message_unreact_v1, message_sendlater_v1, message_sendlater_dm_v1
from src.users import users_all_v1, user_profile_setname_v1, user_profile_setemail_v1, user_stats_v1, users_stats_v1
from src.users import user_profile_sethandle_v1, user_profile_v1, user_profile_uploadphoto_v1
from src.dm import dm_create_v1, dm_details_v1, dm_leave_v1, dm_list_v1, dm_messages_v1, dm_remove_v1
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.notifications import search_v1, notifications_get_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/imgurl/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS
APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'F13Ateamcamel@gmail.com'
APP.config['MAIL_PASSWORD'] = 'projectbackend234'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)

# Example
@APP.route("/echo", methods=['GET'])
def echo_v1():
    data = request.args.get('data')
    ret = echo(data)
    return dumps({
        'data': ret
    })

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})

@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()
    ret = auth_login_v1(data['email'], data['password'])
    return dumps({
        'token': ret['token'],
        'auth_user_id': ret['auth_user_id']
    })

@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()
    ret = auth_register_v1(data['email'], data['password'],
    data['name_first'], data['name_last'])
    return dumps({
        'token': ret['token'],
        'auth_user_id': ret['auth_user_id']
    })

@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    data = request.get_json()
    auth_logout_v1(data['token'])
    return dumps({})

@APP.route("/channels/create/v2", methods=['POST'])
def create():
    data = request.get_json()
    ret = channels_create_v1(data['token'], data['name'], data['is_public'])
    return dumps({
        'channel_id': ret['channel_id']
    })

@APP.route("/channel/details/v2", methods=['GET'])
def details():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v1(token, channel_id))

@APP.route("/channel/join/v2", methods=['POST'])
def join():
    data = request.get_json()
    channel_join_v1(data['token'], data['channel_id'])
    return dumps({})

@APP.route("/channel/invite/v2", methods=['POST'])
def invite():
    data = request.get_json()
    channel_invite_v1(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route("/channel/messages/v2", methods = ['GET'])
def message():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    return dumps(channel_messages_v1(token, channel_id, start))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    channel_leave_v1(data['token'], data['channel_id'])
    return dumps({})

@APP.route("/channel/addowner/v1", methods=['POST'])
def addowner():
    data = request.get_json()
    channel_addowner_v1(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route("/channel/removeowner/v1", methods=['POST'])
def removeowner():
    data = request.get_json()
    channel_removeowner_v1(data['token'], data['channel_id'], data['u_id'])
    return dumps({})

@APP.route("/channels/list/v2", methods=['GET'])
def channel_list():
    token = request.args.get('token')
    return dumps(channels_list_v1(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channel_list_all():
    token = request.args.get('token')
    return dumps(channels_listall_v1(token))

@APP.route("/users/all/v1", methods=['GET'])
def all():
    token = request.args.get('token')
    return dumps(users_all_v1(token))

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def setname():
    data = request.get_json()
    user_profile_setname_v1(data['token'], data['name_first'], data['name_last'])
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def sethandle():
    data = request.get_json()
    user_profile_sethandle_v1(data['token'], data['handle_str'])
    return dumps({})

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def setemail():
    data = request.get_json()
    user_profile_setemail_v1(data['token'], data['email'])
    return dumps({})

@APP.route("/user/profile/v1", methods=['GET'])
def profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return dumps(user_profile_v1(token, u_id))

@APP.route("/user/profile/uploadphoto/v1", methods={'POST'})
def profile_upload_photo():
    data = request.get_json()
    user_profile_uploadphoto_v1(data['token'], data['img_url'], data['x_start'],
                                data['y_start'], data['x_end'], data['y_end'])
    return dumps({})

@APP.route('/imgurl/<path:path>')
def send_photo(path):
    return send_from_directory('', path)

@APP.route("/message/send/v1", methods = ['POST'])
def send_message():
    data = request.get_json()
    ret = message_send_v1(data['token'], data['channel_id'], data['message'])
    return dumps({'message_id': ret['message_id']})

@APP.route("/message/remove/v1", methods = ['DELETE'])
def remove_message():
    data = request.get_json()
    message_remove_v1(data['token'], data['message_id'])
    return dumps({})

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def remove_user():
    data = request.get_json()
    admin_remove_user_v1(data['token'], data['u_id'])
    return dumps({})

@APP.route("/message/edit/v1", methods = ['PUT'])
def edit_message():
    data = request.get_json()
    message_edit_v1(data['token'], data['message_id'], data['message'])
    return dumps({})

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    ret = dm_create_v1(data['token'], data['u_ids'])
    return dumps({
        'dm_id': ret['dm_id']
    })

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    return dumps(dm_details_v1(token, dm_id))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    dm_leave_v1(data['token'], data['dm_id'])
    return dumps({})

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    dm_remove_v1(data['token'], data['dm_id'])
    return dumps({})

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    return dumps(dm_list_v1(token))

@APP.route("/message/senddm/v1", methods = ['POST'])
def send_messagedm():
    data = request.get_json()
    ret = message_senddm_v1(data['token'], data['dm_id'], data['message'])
    return dumps({'message_id': ret['message_id']})

@APP.route("/message/pin/v1", methods = ['POST'])
def message_pin():
    data = request.get_json()
    message_pin_v1(data['token'], data['message_id'])
    return dumps({})

@APP.route("/message/unpin/v1", methods = ['POST'])
def message_unpin():
    data = request.get_json()
    message_unpin_v1(data['token'], data['message_id'])
    return dumps({})

@APP.route("/message/react/v1", methods = ['POST'])
def message_react():
    data = request.get_json()
    message_react_v1(data['token'], data['message_id'], data['react_id'])
    return dumps({})

@APP.route("/message/unreact/v1", methods = ['POST'])
def message_unreact():
    data = request.get_json()
    message_unreact_v1(data['token'], data['message_id'], data['react_id'])
    return dumps({})

@APP.route("/dm/messages/v1", methods = ['GET'])
def dm_message():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    return dumps(dm_messages_v1(token, dm_id, start))

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def change_permissions():
    data = request.get_json()
    admin_permission_change_v1(data['token'], data['u_id'], data['permission_id'])
    return dumps({})

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    ret = standup_start_v1(data['token'], data['channel_id'], data['length'])
    return dumps({
        'time_finish': ret['time_finish']
    })

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(standup_active_v1(token, channel_id))

@APP.route("/search/v1", methods = ['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(search_v1(token, query_str))

@APP.route("/notifications/get/v1", methods = ['GET'])
def notifications_get():
    token = request.args.get('token')
    return dumps(notifications_get_v1(token))

@APP.route("/auth/passwordreset/request/v1", methods = ['POST'])
def passwordreset_request():
    data = request.get_json()
    returns = auth_passwordreset_request_v1(data['email'])
    if returns != False:
        msg = Message('Your Password Reset Code', sender = 'F13Ateamcamel@gmail.com', recipients = [data['email']])
        msg.body = returns
        mail.send(msg)
    return dumps({})

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    standup_send_v1(data['token'], data['channel_id'], data['message'])
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def passwordreset_reset():
    data = request.get_json()
    auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    return dumps({})

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    data = request.get_json()
    returns = message_share_v1(data['token'], data['og_message_id'], data['message'], 
    data['channel_id'], data['dm_id'])
    return dumps({'shared_message_id': returns["shared_message_id"]})

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    data = request.get_json()
    returns = message_sendlater_v1(data['token'], data['channel_id'], data['message'], 
    data['time_sent'])
    return dumps({'message_id': returns["message_id"]})

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlater_dm():
    data = request.get_json()
    returns = message_sendlater_dm_v1(data['token'], data['dm_id'], data['message'], 
    data['time_sent'])
    return dumps({'message_id': returns["message_id"]})

@APP.route("/user/stats/v1", methods = ['GET'])
def user_stats_get():
    token = request.args.get('token')
    return dumps(user_stats_v1(token))

@APP.route("/users/stats/v1", methods = ['GET'])
def users_stats_get():
    token = request.args.get('token')
    return dumps(users_stats_v1(token))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port

