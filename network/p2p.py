print("LOADED NODE CLASS FROM:", __file__)
import asyncio
from aiohttp import web, ClientSession, WSMsgType
import json
from typing import List, Dict, Callable, Optional

class Node:
    def __init__(self, host: str = 'localhost', port: int = 8765, peers: Optional[List[str]] = None):
        self.host = host
        self.port = port
        self.peers = set(peers) if peers else set()
        self.server = None
        self.connections = set()
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.app = web.Application()
        self.app.add_routes([web.get('/ws', self.handle_connection)])
        self.runner = None
        self.site = None

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        self.running = True
        print(f"[P2P] Node started on {self.host}:{self.port}")
        await self.connect_to_peers()

    async def connect_to_peers(self):
        for peer in list(self.peers):
            try:
                session = ClientSession()
                ws = await session.ws_connect(peer.replace('ws://', 'http://') + '/ws')
                self.connections.add(ws)
                asyncio.create_task(self.listen(ws))
                print(f"[P2P] Connected to peer {peer}")
            except Exception as e:
                print(f"[P2P] Failed to connect to {peer}: {e}")

    async def handle_connection(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.connections.add(ws)
        print(f"[P2P] Incoming connection from {request.remote}")
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self.handle_message(msg.data, ws)
                elif msg.type == WSMsgType.ERROR:
                    print(f"[P2P] WS connection closed with exception {ws.exception()}")
        finally:
            self.connections.discard(ws)
        return ws

    async def listen(self, ws):
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self.handle_message(msg.data, ws)
                elif msg.type == WSMsgType.ERROR:
                    print(f"[P2P] WS connection closed with exception {ws.exception()}")
        except Exception as e:
            print(f"[P2P] Connection closed: {e}")
        finally:
            self.connections.discard(ws)

    async def handle_message(self, message, websocket):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            payload = data.get('payload')
            handler = self.handlers.get(msg_type)
            if handler:
                await handler(payload, websocket)
            else:
                print(f"[P2P] Unknown message type: {msg_type}")
        except Exception as e:
            print(f"[P2P] Error handling message: {e}")

    def on(self, msg_type: str, handler: Callable):
        self.handlers[msg_type] = handler

    async def broadcast(self, msg_type: str, payload):
        message = json.dumps({'type': msg_type, 'payload': payload})
        for ws in list(self.connections):
            try:
                await ws.send_str(message)
            except Exception as e:
                print(f"[P2P] Failed to send to peer: {e}")

    async def stop(self):
        self.running = False
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        for ws in list(self.connections):
            await ws.close()
        self.connections.clear()
        print(f"[P2P] Node stopped.") 