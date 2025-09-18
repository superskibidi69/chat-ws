import asyncio, websockets, json, os

PORT = int(os.environ.get("PORT", 8765))
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
        raw = await websocket.recv()
        hello = json.loads(raw)
        username = hello.get("user", "anon")
        clients[websocket] = username

        await broadcast({"system": f"{username} joined the chat"})

        async for raw in websocket:
            data = json.loads(raw)
            await broadcast(data)

    except Exception as e:
        print("Error:", e)
    finally:
        username = clients.pop(websocket, "anon")
        await broadcast({"system": f"{username} left the chat"})

# this handles non-WebSocket requests (like HEAD from Render)
async def http_handler(path, request_headers):
    return 200, [], b"api ok"

async def main():
    async with websockets.serve(
        handler, "0.0.0.0", PORT, process_request=http_handler
    ):
        print(f"server running ws://0.0.0.0:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
