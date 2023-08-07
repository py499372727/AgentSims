import json
import time
import sys
import asyncio
import websockets

count_limit = 0
args = sys.argv
print(args)
if len(args) > 1:
    count_limit = int(args[1])

async def listen_server(websocket):
    while True:
        msg = await websocket.recv()
        print(f"Received: {msg}")

async def ping(websocket):
    # info = json.dumps({"uri": "command.auth.Register", "method": "POST", "data": {"nickname": "fisher", "email": "abc@def.com", "cryptoPWD": "WWW"}}, ensure_ascii=False, separators=(",", ":"))
    # await websocket.send(info)
    uid = "tick-10001"
    while True:
        info = json.dumps({"uid": uid, "uri": "ping", "method": "GET", "data": {}}, ensure_ascii=False, separators=(",", ":"))
        print(f"Send: {info}")
        await websocket.send(info)
        await asyncio.sleep(10)

async def call_timetick(websocket):
    uid = "tick-10001"
    call = json.dumps({"uid": uid, "uri": "command.timetick.Tick", "method": "POST"}, ensure_ascii=False, separators=(",", ":"))
    # sendings = list()
    counter = 0
    while True:
        sending = asyncio.create_task(websocket.send(call))
        print(f"Sending: {call}")
        # receive = await websocket.recv()
        await asyncio.sleep(1)
        await sending
        counter += 1
        if count_limit and count_limit <= counter:
            raise ValueError("Stop tick")
    # for sending in sendings:
    #     await sending

async def main():
    async with websockets.connect("ws://localhost:8000/ws", ping_interval=None) as websocket:
        timer_task = asyncio.create_task(call_timetick(websocket))
        ping_task = asyncio.create_task(ping(websocket))
        server_task = asyncio.create_task(listen_server(websocket))

        await server_task
        await timer_task
        await ping_task

asyncio.run(main())