import asyncio
import websockets

async def handler(websocket, path):
    print("Handler called", websocket, path)
    await websocket.wait_closed()

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("Server started on localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 