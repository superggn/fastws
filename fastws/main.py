import json
from typing import Union

import time
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

from fastws.constants import INIT_MESSAGE, MessageType
from utils.format_utils import get_refined_message
from utils.redis_client import cache_get_list, cache_lpush
from utils.ws_utils import connection_manager

app = FastAPI()
active_connections = []

history_cache_key = 'HISTORY'

cnt = 0


@app.get('/')
async def read_root():
    global cnt
    cnt += 1
    print('cnt', cnt)
    return {'Hello': 'World'}


@app.post('/')
async def read_root():
    return {'Hello': 'you are post!!!'}


# @app.get('/items/{item_id}')
# async def read_item(item_id: str, q: Union[str, None] = None):
#     print('q: ', q)
#     print('type(item_id): ', type(item_id))
#     print('item_id: ', item_id)
#     if item_id == '10':
#         q = 'haha'
#     return {'item_id': item_id, 'q': q}


@app.get('/items/{item_id}')
async def read_item(item_id: str, request: Request, q: Union[str, None] = None):
    headers = request.headers  # Using the request object as needed
    user_agent = headers.get("user-agent")
    print('User-Agent:', user_agent)
    print('q: ', q)
    print('type(item_id): ', type(item_id))
    print('item_id: ', item_id)
    if item_id == '10':
        q = 'haha'
    return {'item_id': item_id, 'q': q}


@app.websocket('/simple_ws/{room_id}')
async def simple_ws(websocket: WebSocket, room_id: int):
    await connection_manager.connect(websocket)
    # await websocket.send_text('init message')
    start_time = time.time()
    # raise Exception
    try:
        while True:
            text = await websocket.receive_text()
            print('text', text)
            await websocket.send_text(f'Message received: {text}')
    except WebSocketDisconnect:
        print('one client left the chat')
        end_time = time.time()
        print('start_time - end_time = ', start_time - end_time)


@app.websocket('/ws/{room_id}')
async def ws_chat(websocket: WebSocket, room_id: int):
    await connection_manager.connect(websocket)
    # print('type(websocket.headers)', type(websocket.headers))
    # print('websocket.headers', websocket.headers)
    # headers = dict(websocket.headers)
    # print('type(headers)', type(headers))
    # print('headers', headers)
    # username = headers.get('username', '')
    # if username:
    #     username = username.lower()
    # print('------')
    # print('type(websocket.scope["query_string"])', type(websocket.scope['query_string']))
    # print('websocket.scope["query_string"]', websocket.scope['query_string'])
    # # 注意这里的 value 是 list
    # query_dict = parse_qs(websocket.scope['query_string'])
    print('room_id', room_id)
    await send_init_messages(websocket)
    await send_history_messages(websocket)
    try:
        while True:
            json_str = await websocket.receive_text()
            print('server json_str', json_str)
            raw_msg = json.loads(json_str)
            raw_msg['msg_type'] = MessageType.REAL_TIME
            refined_msg = get_refined_message(raw_msg)
            print('server refined_msg', refined_msg)
            store_history(refined_msg)
            """
            {
                'username': 'superggn',
                'msg': 'hello~',
                # timestamp in milliseconds
                'timestamp': 1693971390000,
                'msg_type': 'real_time',
            }
            """
            await connection_manager.broadcast_msg(refined_msg)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast_text('Client left the chat')


async def send_history_messages(websocket: WebSocket):
    print('history start')
    history_str_list = cache_get_list(history_cache_key)
    print('history_str_list', history_str_list)
    history_str_list.reverse()
    for message in history_str_list:
        await websocket.send_text(message)
    print('history ends')


async def send_init_messages(websocket: WebSocket):
    print('init sending start')
    msg = {
        'username': 'admin',
        'msg': INIT_MESSAGE,
        'timestamp': int(time.time() * 1000),
        'msg_type': MessageType.INIT,
    }
    msg_str = json.dumps(msg)
    await websocket.send_text(msg_str)


def store_history(escaped_msg):
    original_type = escaped_msg['msg_type']
    escaped_msg['msg_type'] = MessageType.HISTORY
    history_str = json.dumps(escaped_msg)
    cache_lpush(history_cache_key, history_str)
    escaped_msg['msg_type'] = original_type
