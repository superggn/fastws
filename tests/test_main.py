import json

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from fastws.constants import INIT_MESSAGE, MessageType
from fastws.main import app
from utils.redis_client import RedisClient

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_get(anyio_backend):
    async with AsyncClient(app=app) as ac:
        resp = await ac.get("http://test/")
        print('------------------')
        print('r', resp)
        print('------------------')


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_simple_ws(anyio_backend):
    client = TestClient(app)
    with client.websocket_connect('/simple_ws/1') as ws:
        text = 'hello, ws!'
        ws.send_text(text)
        resp = ws.receive_text()
        assert resp == f'Message received: {text}'
        return


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_ws(anyio_backend):
    # 测试
    # init 消息
    # 自己的消息回返
    # 别人的消息广播到自己这里
    # emoji 编码
    client = TestClient(app)
    RedisClient.clear()
    with client.websocket_connect('/ws/1') as ws_1:
        msg = get_json_msg(ws_1)
        assert msg['msg'] == INIT_MESSAGE
        assert msg['msg_type'] == MessageType.INIT
        ws_1_username = 'ws_1'
        ws_1_msg_1 = f'{ws_1_username} msg_1'
        msg = {
            'username': ws_1_username,
            'msg': ws_1_msg_1,
        }
        ws_1.send_text(json.dumps(msg))
        msg = get_json_msg(ws_1)
        assert msg['msg'] == ws_1_msg_1
        assert msg['msg_type'] == MessageType.REAL_TIME
        with client.websocket_connect('/ws/1') as ws_2:
            msg = get_json_msg(ws_2)
            assert msg['msg'] == INIT_MESSAGE
            assert msg['msg_type'] == MessageType.INIT
            msg = get_json_msg(ws_2)
            assert msg['msg'] == ws_1_msg_1
            assert msg['msg_type'] == MessageType.HISTORY
            ws_2_username = 'ws_2'
            ws_2_msg_1 = f'{ws_2_username} msg_1'
            msg = {
                'username': ws_2_username,
                'msg': ws_2_msg_1,
            }
            send_json_msg(ws_2, msg)
            # test 自己能收到自己的消息
            msg = get_json_msg(ws_2)
            assert msg['msg'] == ws_2_msg_1
            assert msg['msg_type'] == MessageType.REAL_TIME
            # test 别人能收到自己的消息
            msg = get_json_msg(ws_1)
            assert msg['msg'] == ws_2_msg_1
            assert msg['msg_type'] == MessageType.REAL_TIME
    return


def get_json_msg(ws):
    resp = ws.receive_text()
    return json.loads(resp)


def send_json_msg(ws, json_msg):
    json_str = json.dumps(json_msg)
    ws.send_text(json_str)
