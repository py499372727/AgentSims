import os
import time
import datetime
import importlib
import json
from agent.actor import Actor
from config import Config, BuildingConfig, NPCConfig, EquipmentConfig, FrameworkConfig, EconomicConfig, EvalConfig
from utils import utils

abs_path = os.path.dirname(os.path.realpath(__file__))

class App:
    def __init__(self) -> None:
        self.ws_cache = dict()
        self.id_to_ws = dict()
        self.inited = set()
        self.movings = set()
        self.chatted = set()
        self.using = set()
        self.cache = list()
        # {uid(NPC-xxx): Actor}
        self.actors = dict()
        self.evals = {}
        self.start_time = self.get_nowtime()
        self.last_real_time = self.get_nowtime()
        self.last_game_time = self.get_nowtime()
        self.tick_state = {
            "start_time": 0,
            "tick_count": 0,
            "start": False,
        }
        self.mayor_state = {
            "start_time": 0,
            "start": False,
        }

        self.config = Config(os.path.join(abs_path, 'config', 'app.json'))

        self.load_building_configs(os.path.join(abs_path, 'config', 'buildings.json'))
        self.load_npc_configs(os.path.join(abs_path, 'config', 'agent.json'))
        self.load_framework_configs(os.path.join(abs_path, 'config', 'framework.json'))
        self.load_equipment_configs(os.path.join(abs_path, 'config', 'equipments.json'))
        self.load_economic_configs(os.path.join(abs_path, 'config', 'economics.json'))
        self.load_eval_configs(os.path.join(abs_path, 'config', 'eval.json'))
        self.snapshot_path = os.path.join(abs_path, 'snapshot', 'app.json')
        self.load_snapshot()

    def load_snapshot(self):
        if os.path.exists(self.snapshot_path):
            with open(self.snapshot_path, "r", encoding="utf-8") as snapshot:
                obj = json.loads(snapshot.read())
                self.inited = set(obj.get("inited", list()))
                self.movings = set(obj.get("movings", list()))
                self.chatted = set(obj.get("chatted", list()))
                self.using = set(obj.get("using", list()))
                self.cache = obj.get("cache", list())
                self.actors = {k: Actor("", "", "", "", "", "", list(), 0, self.get_game_time()).from_json(v) for k, v in obj.get("actors", dict()).items()}
                self.last_real_time = obj.get("last_real_time", self.get_nowtime())
                self.last_game_time = obj.get("last_game_time", self.get_nowtime())
                self.tick_state = obj.get("tick_state", {
                    "start_time": 0,
                    "tick_count": 0,
                    "start": False,
                })
                self.mayor_state = obj.get("mayor_state", {
                    "start_time": 0,
                    "start": False,
                })
    
    def save_snapshot(self):
        info = {
            "inited": list(self.inited),
            "movings": list(self.movings),
            "chatted": list(self.chatted),
            "using": list(self.using),
            "cache": self.cache,
            "actors": {k: v.to_json() for k, v in self.actors.items()},
            "last_real_time": self.last_real_time,
            "last_game_time": self.last_game_time,
            "tick_state": self.tick_state,
            "mayor_state": self.mayor_state,
        }
        # print(info)
        info = json.dumps(info, ensure_ascii=False, separators=(",", ":"))
        with open(self.snapshot_path, "w", encoding="utf-8") as snapshot:
            snapshot.write(info)

    def add_moving(self, entity_type, entity_id, map_id):
        self.movings.add((entity_type, entity_id, map_id))

    def log(self, info: str) -> None:
        print(info)

    def register(self, ws):
        if ws not in self.ws_cache:
            self.ws_cache[ws] = dict()
        self.log("somebody linked.")
        ws.write_message({"code": 200, "uri": "welcome", "msg": "Welcome"})

    def logout(self, ws):
        if ws in self.ws_cache:
            if self.ws_cache[ws]:
                del self.id_to_ws[self.ws_cache[ws]["uid"]]
                self.log(f'{self.ws_cache[ws]["uid"]} is logging out')
            else:
                self.log("somebody is logging out.")
            del self.ws_cache[ws]
        else:
            self.log("somebody is logging out.")

    def broadcast(self, entityType=None, message=""):
        for uid, ws in self.id_to_ws.items():
            if not entityType or uid.startswith(entityType):
                if not isinstance(message, str):
                    message = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
                ws.write_message(message)

    def login(self, ws, uid):
        self.ws_cache[ws]["uid"] = uid
        self.ws_cache[ws]["loginTime"] = self.get_nowtime()
        self.log(f"{uid} logging in at {self.get_formatter(self.ws_cache[ws]['loginTime'])}")
    
    def send(self, uid: str, message=""):
        if not isinstance(message, str):
            message = json.dumps(message, ensure_ascii=False, separators=(",", ":"))
        if uid in self.id_to_ws:
            try:
                print(f"sending message to {uid}: {message}")
                self.id_to_ws[uid].write_message(message)
            except Exception as e:
                print("sending message and met error:", e)
                del self.id_to_ws[uid]
        # TODO: mayor get player's actions
        # if uid.startswith("Player") and uid.replace("Player", "Mayor") in self.id_to_ws:
        #     muid = uid.replace("Player", "Mayor")
        #     try:
        #         print(f"sending message to {muid}: {message}")
        #         self.id_to_ws[muid].write_message(message)
        #     except Exception:
        #         del self.id_to_ws[muid]

    async def execute(self, ws, message):
        try:
            info = json.loads(message)
        except Exception as e:
            return ws.write_message('message received:' + message)
        ret_data = {"code": 500, "data": {}, "uid": None, "msg": "no URI appointed"}
        uid = ""
        mayor_uid = ""
        if "uid" in info:
            uid = info["uid"]
            if uid not in self.id_to_ws:
                self.id_to_ws[uid] = ws
            if not self.ws_cache[ws]:
                self.login(ws, uid)
                ret_data["uid"] = uid
                ret_data["code"] = 200
                ret_data["data"]["register"] = True
                ret_data["msg"] = ""
        self.log(f"{uid} send: {message}")
        if uid.startswith("Mayor") and "uri" in info and "ping" != info["uri"]:
            mayor_uid = uid
            uid = mayor_uid.replace("Mayor", "Player") # mayor mode works as player mode
            info["uid"] = uid
            info["mayor"] = True # log marker
            print("uid", uid)
            print("mayor_uid:", mayor_uid)
            print(info)
        if "uri" in info and "method" in info:
            # "method": 处理服务器请求，此处无用
            if "ping" == info["uri"]: # ping , for linkage websocket connection
                ret_data["uid"] = info.get("uid")
                ret_data["code"] = 200
                ret_data["data"]["ping"] = True
                ret_data["msg"] = ""
            elif info["uri"].startswith("command."): # {'uri': 'command.building.Create', "data": {'uid': , 'building_type': }}
                # Import module.
                module = importlib.import_module(info["uri"])
                # Get class.
                cls = getattr(module, info["uri"].split('.')[-1])
                # Create the command object.
                cmd = cls(self)
                # Execute command.
                res = await cmd._execute(info)
                # Close db connections.
                for db in cmd.db_cache.values():
                    db.close()
                # Return response.
                if "error" in res:
                    ret_data["code"] = 500 if res.get('doRefresh', False) else 501
                    ret_data["data"] = ""
                    ret_data["uid"] = info.get("uid")
                    ret_data["msg"] = res['error']
                else:
                    ret_data["uid"] = info.get("uid")
                    ret_data["code"] = 200
                    ret_data["data"] = res["data"]
                    ret_data["msg"] = ""
            ret_data["uri"] = info["uri"]
        if ret_data["code"] == 200 and ret_data["uri"] == "command.auth.Register":
            print(ret_data["data"])
            uid = ret_data["data"]["uid"]
            # if uid not in self.id_to_ws:
            print(f"bound websocket to {uid}")
            self.id_to_ws[uid] = ws
            if not self.ws_cache[ws]:
                self.login(ws, uid)
                ret_data["data"]["register"] = True
            # buildings_model = cmd.get_single_model("Buildings", create=False)
            # if buildings_model:
            #     ws.write_message(json.dumps({"code":200,"data":{'buildings': buildings_model.buildings},"uid":uid,"msg":"","uri":"command.building.GetBuildings"}, ensure_ascii=False, separators=(",", ":")))
            # else:
            #     ws.write_message(json.dumps({"code":200,"data":{'buildings': []},"uid":uid,"msg":"","uri":"command.building.GetBuildings"}, ensure_ascii=False, separators=(",", ":")))
            # npcs_model = cmd.get_single_model("NPCs", create=False)
            # if npcs_model:
            #     ws.write_message(json.dumps({"code":200,"data":{'npcs': [cmd.get_single_model("NPC", id=x["id"], create=True).as_object(True) for x in npcs_model.npcs if cmd.get_single_model("NPC", id=x["id"], create=False)]},"uid":uid,"msg":"","uri":"command.npc.GetNPCs"}, ensure_ascii=False, separators=(",", ":")))
            # else:
            #     ws.write_message(json.dumps({"code":200,"data":{'npcs': []},"uid":uid,"msg":"","uri":"command.npc.GetNPCs"}, ensure_ascii=False, separators=(",", ":")))
        if mayor_uid and ret_data["code"] == 200 and ret_data["uri"] == "command.npc.Create":
            # Send Message To Player
            self.send(uid, {"code": 200, "data": ret_data["data"], "uid": mayor_uid, "msg": "", "uri": "mayor.npc.Create"})
        if mayor_uid and ret_data["code"] == 200 and ret_data["uri"] == "command.building.Create":
            # Send Message To Player
            self.send(uid, {"code": 200, "data": ret_data["data"], "uid": mayor_uid, "msg": "", "uri": "mayor.building.Create"})
        self.save_snapshot()
        return ws.write_message(json.dumps(ret_data, ensure_ascii=False, separators=(",", ":")))

    def get_nowtime(self):
        return int(time.time() * 1000)

    def get_formatter(self, timestamp_ms, format_str='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format_str, time.localtime(timestamp_ms / 1000))

    def get_nowtime_seconds(self):
        return int(time.time())
    
    def get_game_time(self):
        return self.last_game_time

    def load_eval_configs(self, path):
        self.eval_configs = {}
        objs = utils.load_json_file(path)
        # Read data.
        for obj in objs:
            config = EvalConfig(obj)
            self.eval_configs[config.id] = config

    def load_building_configs(self, path):
        self.building_configs = {}
        # Load json file.
        objs = utils.load_json_file(path)
        # Read data.
        for obj in objs:
            config = BuildingConfig(obj)
            self.building_configs[config.id] = config

    def get_building_config(self, id):
        return self.building_configs[id]

    def load_equipment_configs(self, path):
        self.equipment_configs = {}
        # Load json file.
        objs = utils.load_json_file(path)
        # Read data.
        for obj in objs:
            config = EquipmentConfig(obj)
            self.equipment_configs[config.id] = config

    def get_equipment_config(self, id):
        return self.equipment_configs[id]
    
    def load_economic_configs(self, path):
        self.economic_configs = {}
        # Load json file.
        objs = utils.load_json_file(path)
        # Read data.
        for obj in objs:
            config = EconomicConfig(obj)
            self.economic_configs[config.id] = config

    def get_economic_config(self, id):
        return self.economic_configs[id]

    def load_npc_configs(self, path):
        self.npc_configs = NPCConfig(path)

    def get_npc_config(self):
        return self.npc_configs
    
    def load_framework_configs(self, path):
        self.framework_configs = FrameworkConfig(path)

    def get_framework_config(self):
        return self.framework_configs
