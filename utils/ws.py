#!/usr/bin/python3
#encoding: utf-8

from websocket import create_connection
import json

api_url = "ws://111.231.102.248/ws_api/"
event_url = "ws://111.231.102.248/ws_event/"
qqid = "3309196071"
token = "curranbot"

ws = create_connection(event_url, header={"X-Self-ID" : qqid, "Authorization" : "Token %s" % token})

evt = {'self_id': 3309196071, 'post_type': 'message', 'message': '/gakki', 'time': 1534090199, 'font': 34167840, 'sub_type': 'friend', 'user_id': 188223673, 'message_type': 'private', 'message_id': 19078, 'raw_message': '/gakki'}
print(json.dumps(evt))

ws.send(json.dumps(evt))
result = ws.recv()
print(result)
ws.close()


