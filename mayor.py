import os
import sys
import time
import random
import json
import asyncio
import websockets
from agent.agent.mayor import Mayor
import traceback

abs_path = os.path.dirname(os.path.realpath(__file__))
stop_seconds = 10
count_limit = 0
args = sys.argv
print(args)
if len(args) > 1:
    count_limit = int(args[1])

class Mayors(object):
    def __init__(self) -> None:
        self.json_filename = os.path.join(abs_path, "snapshot", "mayors.json")
        self.output_filename = os.path.join(abs_path, "logs", "mayors.log")
        self.mayors = dict()
        self.websockets = dict()
    
    def log(self, info):
        print(info)
        with open(self.output_filename, "a", encoding="utf-8") as log_file:
            log_file.write(f"{info}\n")
    
    # async def add_mayor(self, mayor: Mayor):
    #     self.mayors[mayor.uid] = mayor
    #     async with websockets.connect("ws://localhost:8000/ws", ping_interval=None) as websocket:
    #         self.websockets[mayor.uid] = websocket
    
    async def load_mayors(self):
        if not os.path.exists(self.json_filename):
            return
        with open(self.json_filename, "r", encoding="utf-8") as json_file:
            json_obj = json.loads(json_file.read())
            if "uids" in json_obj:
                for uid in json_obj["uids"]:
                    mayor = Mayor(uid)
                    if uid in json_obj.get("states", dict()):
                        mayor.from_json(json_obj["states"][uid])
                    if uid not in self.mayors:
                        self.mayors[uid] = mayor
                    if uid not in self.websockets:
                        websocket = await websockets.connect("ws://localhost:8000/ws", ping_interval=None)
                        await websocket.recv()
                        self.websockets[uid] = websocket

    def save_mayors(self):
        saving = {
            "uids": list(),
            "states": dict()
        }
        for uid, mayor in self.mayors.items():
            mayor = mayor.to_json()
            saving["uids"].append(uid)
            saving["states"][uid] = mayor
        with open(self.json_filename, "w", encoding="utf-8") as json_file:
            json_file.write(json.dumps(saving, ensure_ascii=False, separators=(",", ":")))

    async def mayor_tick(self, uid):
        ws = self.websockets.get(uid)
        mayor = self.mayors.get(uid)
        # mayor = Mayor(uid)
        if not ws or not mayor:
            return
        await mayor.get_mayor_info(ws)
        await mayor.decision()
        if mayor.result["result"] != "success":
            return
        self.log(mayor.mayor)
        action = mayor.mayor.get("action", "")
        if action == "Building" and mayor.result["result"] != "fail":
            building_type = mayor.mayor.get("type", "")
            x = mayor.mayor.get("position", dict()).get("x", 0)
            y = mayor.mayor.get("position", dict()).get("y", 0)
            create_building = json.dumps({"uid": uid, "uri": "command.building.Create", "method": "POST", "data": {"building_type": building_type, "name": "", "x": x, "y": y, "rotation": 0}}, ensure_ascii=False, separators=(",", ":"))
            self.log(f"{uid} Send: {create_building}")
            await ws.send(create_building)
            msg = await ws.recv()
            self.log(f"{uid} Received: {msg}")
            result = {}
            try:
                result = json.loads(msg)
            except Exception as e:
                pass
            if "code" in result and result["code"] != 200:
                mayor.result = {"result": "fail", "msg": result["msg"]}
        elif action == "NPC" and mayor.result["result"] != "fail":
            asset = f"premade_0{random.randint(1, 8)}"
            name = mayor.mayor.get("name", "")
            bio = mayor.mayor.get("bio", "")
            goal = mayor.mayor.get("goal", "")
            home_building = mayor.mayor.get("home_building", 0)
            npc_cash = 10000
            create_npc = json.dumps({"uid": uid, "uri": "command.npc.Create", "method": "POST", "data": {"asset": asset, "model": "gpt-4", "memorySystem": "LongShortTermMemories", "planSystem": "QAFramework", "homeBuilding": home_building, "workBuilding": 0, "nickname": name, "bio": bio, "goal": goal, "cash": npc_cash}}, ensure_ascii=False, separators=(",", ":"))
            self.log(f"{uid} Send: {create_npc}")
            await ws.send(create_npc)
            msg = await ws.recv()
            self.log(f"{uid} Received: {msg}")
            result = {}
            try:
                result = json.loads(msg)
            except Exception as e:
                pass
            if "code" in result and result["code"] != 200:
                mayor.result = {"result": "fail", "msg": result["msg"]}

    async def flush(self):
        calls = list()
        for uid in self.mayors.keys():
            calls.append(asyncio.create_task(self.mayor_tick(uid)))
        for call in calls:
            await call
    
    async def loop(self):
        counter = 0
        try:
            while True:
                await self.load_mayors()
                flush_task = asyncio.create_task(self.flush())
                await asyncio.sleep(stop_seconds)
                await flush_task
                self.save_mayors()
                counter += 1
                if count_limit and counter >= count_limit:
                    break
        except Exception as e:
            self.log(f"got Exception: {e.__class__}: {e}")
            traceback_str = traceback.format_tb(e.__traceback__)
            self.log("Traceback:")
            self.log(''.join(traceback_str))
            await self.close()
        raise ValueError("stop mayor")
    
    async def close(self):
        for ws in self.websockets.values():
            await ws.close()

# async def listen_server(websocket):
#     while True:
#         msg = await websocket.recv()
#         print(f"Received: {msg}")

# async def ping(websocket):
#     # info = json.dumps({"uri": "command.auth.Register", "method": "POST", "data": {"nickname": "fisher", "email": "abc@def.com", "cryptoPWD": "WWW"}}, ensure_ascii=False, separators=(",", ":"))
#     # await websocket.send(info)
#     uid = "Mayor-10001"
#     while True:
#         info = json.dumps({"uid": uid, "uri": "ping", "method": "GET", "data": {}}, ensure_ascii=False, separators=(",", ":"))
#         print(f"Send: {info}")
#         await websocket.send(info)
#         await asyncio.sleep(10)

async def main():
    mayors_factory = Mayors()
    loop_task = asyncio.create_task(mayors_factory.loop())
    await loop_task

asyncio.run(main())