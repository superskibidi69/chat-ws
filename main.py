import asyncio, websockets, json, os

PORT = int(os.environ.get("PORT", 8765))
rooms = {"chat": {}, "newroom": {}}  # websocket -> username per room

async def broadcast(room, data):
    dead = []
    for ws in list(rooms[room].keys()):
        try:
            await ws.send(json.dumps(data))
        except:
            dead.append(ws)
    for ws in dead:
        rooms[room].pop(ws, None)

async def handler(websocket, path):
    if path not in rooms:
        rooms[path] = {}
    room = path
    try:
        raw = await websocket.recv()
        hello = json.loads(raw)
        username = hello.get("user", "anon")
        rooms[room][websocket] = username

        await broadcast(room, {"system": f"{username} joined {room}"})

        async for raw in websocket:
            data = json.loads(raw)
            await broadcast(room, data)

    except Exception as e:
        print("Error:", e)
    finally:
        username = rooms[room].pop(websocket, "anon")
        await broadcast(room, {"system": f"{username} left {room}"})

async def http_handler(path, request_headers):
    # health checks etc
    if request_headers.get("Upgrade", "").lower() == "websocket":
        return None
    if request_headers.get("Method", "").upper() in ["GET", "HEAD"]:
        return 200, [("Content-Type", "text/plain")], b"ok"
    return 400, [("Content-Type", "text/plain")], b"bad request"

async def main():
    async with websockets.serve(
        handler, "0.0.0.0", PORT, process_request=http_handler
    ):
        print(f"server running ws://0.0.0.0:{PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
