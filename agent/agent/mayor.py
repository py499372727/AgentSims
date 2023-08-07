import json
import asyncio
import datetime
import time
from typing import List, Dict, Any

# from agent.agent.components.memory_store import MemoryData
# from agent.agent.components.state import State
# from agent.agent.components.cache import Cache
# from agent.agent.components.prompt import Prompts
# from agent.agent.components.controller import Controller
from agent.utils.llm import LLMCaller
from agent.prompt.prompt import Prompt

import re

class Mayor:
    def __init__(self, uid: str) -> None:
        self.prompt = Prompt("mayor")
        self.uid = uid
        self.caller = LLMCaller("gpt-4")
        self.mayor_prompt = ""
        self.mayor = dict()
        self.mayor_info = dict()
        self.result = dict()

    def to_json(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "prompt": "mayor",
            "caller": self.caller.model,
            "mayor_prompt": self.mayor_prompt,
            "mayor": self.mayor,
            "mayor_info": self.mayor_info,
            "result": self.result,
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.caller = LLMCaller(obj.get("caller", "gpt-4"))
        self.prompt = Prompt(obj.get("prompt", "mayor"))
        self.uid = obj["uid"]
        self.mayor_prompt = obj.get("mayor_prompt", "")
        self.mayor = obj.get("mayor", dict())
        self.mayor_info = obj.get("mayor_info", dict())
        self.result = obj.get("result", dict())

    async def get_mayor_info(self, ws) -> None:
        get_info = json.dumps({"uid": self.uid, "uri": "command.mayor.GetInfo", "method": "GET", "data": {}}, ensure_ascii=False, separators=(",", ":"))
        await ws.send(get_info)
        msg = await ws.recv()
        if msg:
            info = json.loads(msg)
            if info["code"] == 200:
                self.mayor_info = info["data"]
    
    def transfer_timestamp(self, timestamp: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp / 1000)

    async def decision(self) -> None:
        game_time = self.transfer_timestamp(self.mayor_info.get("last_game_time", int(time.time() * 1000) / 1000))
        start_time = self.transfer_timestamp(self.mayor_info.get("start_time", int(time.time() * 1000) / 1000))
        self.mayor_prompt = self.prompt.to_string({
            "{time}": game_time.strftime("%H:%M"),
            "{day}": (start_time - game_time).days,
            "{revenue}": self.mayor_info.get("revenue", 0),
            "{building_state}": [{"name": x["name"], "x": x["x"], "y": x["y"], "income": x["income"], "freebeds": x["beds"] - len(x["livings"])} for x in self.mayor_info.get("buildings", list())],
            "{name,bio,goal,cash}": [{"name": x["name"], "bio": x["bio"], "goal": x["goal"], "cash": x["cash"]} for x in self.mayor_info.get("npcs", list())],
            "{last_action}": self.mayor,
            "{last_result}": self.result,
            "{building_list}": [x["type"] for x in self.mayor_info.get("building_types", list())],
        })
        self.mayor = await self.caller.ask(self.mayor_prompt)
        print(self.mayor)
        self.result = {"result": "success"}
        if "action" not in self.mayor:
            print(self.mayor)
        elif self.mayor["action"] == "Building":
            building_type = self.mayor.get("type", "1")
            building_type_to_id = {x["type"]: x["id"] for x in self.mayor_info.get("building_types", list())}
            # print(building_type, building_type_to_id)
            if building_type not in building_type_to_id:
                self.result = {"result": "fail", "msg": "type not in choices"}
            else:
                building_type = building_type_to_id[building_type]
                position = self.mayor.get("position", {"x": 1, "y": 1})
                if not isinstance(position, dict):
                    position = {"x": 1, "y": 1}
                if "x" not in position:
                    position["x"] = 1
                if "y" not in position:
                    position["y"] = 1
                self.mayor["position"] = position
                self.mayor["type"] = building_type
        elif self.mayor["action"] == "NPC":
            if not self.mayor["name"]:
                self.result = {"result": "fail", "msg": "name is blank"}
            elif not self.mayor["bio"]:
                self.result = {"result": "fail", "msg": "bio is blank"}
            elif not self.mayor["goal"]:
                self.result = {"result": "fail", "msg": "goal is blank"}
            home_building = self.mayor["home_building"]
            home_building_to_id = {x["name"]: x["id"] for x in self.mayor_info.get("buildings", list())}

            if home_building not in home_building_to_id:
                self.result = {"result": "fail", "msg": "home_building not in choices"}
            else:
                home_building = home_building_to_id[home_building]
                self.mayor["home_building"] = home_building
