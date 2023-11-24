

class WSManager:
    def __init__(self):
        self.active_connections = []

    async def add(self, websocket):
        self.active_connections.append(websocket)

    def delete(self, websocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(websocket, message):
        await websocket.send_str(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_str(message)

    async def broadcast_without_ws(self, message, without_ws):
        for connection in self.active_connections:
            if connection != without_ws:
                await connection.send_str(message)
