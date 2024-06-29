from flask import Flask, request
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')
socket_ids = {}


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('register')
def handle_register(data):
    socket_ids[data['user_id']] = request.sid


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('chat')
def handle_message(msg_info):
    sender_id = msg_info['sender_id']
    msg = msg_info['message']
    receiver_id = msg_info['receiver_id']

    receiver_sid = socket_ids.get(receiver_id)
    if receiver_sid:
        emit('message_from_server', msg_info, to=receiver_sid)
    else:
        print('Receiver not connected')


if __name__ == '__main__':
    socketio.run(app, port=5000)
