import asyncio
import websockets
import json

clients = {}  # map websocket -> username

async def broadcast(data):
    dead = []
    for ws in list(clients.keys()):
        try:
            await ws.send(json.dumps(data))
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.pop(ws, None)

async def handler(websocket):
    try:
        # wait for first message to set username
        raw = await websocket.recv()
        hello = json.loads(raw)
        username = hello.get("user","anon")
        clients[websocket] = username

        # announce join
        await broadcast({"system": f"{username} joined the chat"})

        # normal loop
        async for raw in websocket:
            data = json.loads(raw)
            await broadcast(data)

    except Exception as e:
        print("Error:", e)
    finally:
        username = clients.pop(websocket, "anon")
        await broadcast({"system": f"{username} left the chat"})

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("server running ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
