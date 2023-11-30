import json

from starlette.websockets import WebSocket


class ConnectionManager:
    _peak_conn_cnt = 0

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self._peak_conn_cnt = max(
            self._peak_conn_cnt,
            len(self.active_connections),
        )
        print('self._peak_conn_cnt', self._peak_conn_cnt)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_text(self, text: str):
        broken_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(text)
            except Exception as e:
                # mark the connection for removal
                print('e', e)
                broken_connections.append(connection)
        # Remove broken connections
        for connection in broken_connections:
            self.active_connections.remove(connection)

    async def broadcast_msg(self, msg: dict):
        text_msg = json.dumps(msg)
        await self.broadcast_text(text_msg)

    @staticmethod
    async def send_plain_text(websocket: WebSocket, text: str):
        await websocket.send_text(text)

    @staticmethod
    async def send_json(websocket: WebSocket, msg: dict):
        await websocket.send_json(msg, mode='binary')


connection_manager = ConnectionManager()
