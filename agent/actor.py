from typing import List, Dict, Any
from agent.agent.agent import Agent
import datetime

class Actor:
    """
        agent:
            init -> QA -> plan
        plan -> building -> moving
        moving -> act -> use / chat
        use -> critic ? plan : act
        chat -> set maxInteraction to 5 -> storeMemory -> plan
        critic true -> pack act to experience
        timetick -> storeMemory -> memory_store -> Memory
    """
    def __init__(self, name: str, bio: str, goal: str, model: str, memorySystem: str, planSystem: str, buildings: List[str], cash: int, start_time: float) -> None:
        self.using = False
        self.agent = Agent(name, bio, goal, model, memorySystem, planSystem, buildings, cash, start_time)
    
    # def _init(self):
    #     self.agent.plan()
    def from_json(self, obj: Dict[str, Any]):
        self.agent.from_json(obj)
        return self
    
    def to_json(self) -> Dict[str, Any]:
        return self.agent.to_json()
    
    async def react(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """_summary_

        Args:
            observation (Dict[str, Any]): 
            supposed to contains fields like:
                : source : str : timetick-finishMoving / timetick-finishUse / chatted / addBuilding / timetick-storeMemory
                : data : dict : 

        Returns:
            Dict[str, Any]: _description_
        """
        ret_dict = {"status": 500, "message": "", "data": dict()}
        if self.using:
            ret_dict["message"] = "still using" # to avoid message overwhelming
            if observation['source'] != 'chatted':
                return ret_dict
        self.using = True
        self.agent.state.equipments = observation.get("data", dict()).get("equipments", list())
        self.agent.state.people = observation.get("data", dict()).get("people", list())
        self.agent.state.cash = observation.get("data", dict()).get("cash", list())
        self.agent.state.game_time = datetime.datetime.fromtimestamp(observation.get("data", dict()).get("game_time", datetime.datetime.now().timestamp() * 1000) / 1000)
        if observation['source'] == 'timetick-finishMoving':
            ret_dict["data"] = await self._act()
        elif observation['source'] == 'timetick-finishUse':
            ret_dict["data"] = await self._critic()
        elif observation['source'] == 'timetick-finishChatting':
            await self._store_memory()
            ret_dict["data"] = await self._plan()
        elif observation['source'] == 'inited':
            ret_dict["data"] = await self._plan()
        elif observation['source'] == 'chatted':
            person = observation.get("data", dict()).get("person", "")
            topic = observation.get("data", dict()).get("topic", "")
            self.agent.cache.chat_cache = observation.get("data", dict()).get("chat_cache", list())
            ret_dict["data"] = await self._chat(person, topic)
        elif observation['source'] == "addBuilding":
            self._addBuilding(observation['data']['building_name'])
        elif observation['source'] == 'timetick-storeMemory':
            ret_dict["data"] = await self._store_memory()
        elif observation['source'] == 'cover-prompt':
            # ret_dict["data"] = self._cover_prompt()
            prompt_type = observation.get("data", dict()).get("prompt_type", "")
            prompt_text = observation.get("data", dict()).get("prompt_text", "")
            self.agent.cover_prompt(prompt_type, prompt_text)
        ret_dict["prompts"] = self.agent.state.get_prompts()
        self.using = False
        ret_dict["status"] = 200
        return ret_dict

    async def _critic(self) -> Dict[str, Any]:
        # ret_dict = dict()
        if self.agent.cache.experience_cache:
            acts = self.agent.cache.experience_cache
            act = dict()
            if acts:
                act = acts.pop(0)
            self.agent.cache.experience_cache = acts
            if not act:
                return await self._act()
            return {"use": {"continue_time": act["continue_time"], "result": act["result"]}, "equipment": act['equipment'], "operation": act['operation']}
        if self.agent.state.execute_experience:
            self.agent.state.execute_experience = False
            return await self._plan()
        await self.agent.critic()
        if self.agent.state.critic:
            result = self.agent.state.critic.get("result", "fail")
            if result == "success" or result == "fail":
                await self._store_memory()
                if result == "success":
                    self.agent.experience()
                    self.agent.cache.plan_cache.append(self.agent.state.plan)
                else:
                    self.agent.cache.act_cache.clear()
                return await self._plan()
                # ret_dict["newPlan": self.agent.state.plan]
            else:
                return await self._act()
    
    async def _plan(self) -> Dict[str, Any]:
        ret_dict = dict()
        await self.agent.plan()
        # ret_dict = self._act()
        ret_dict["newPlan"] = self.agent.state.plan
        return ret_dict

    async def _act(self) -> Dict[str, Any]:
        await self.agent.act()
        if self.agent.state.act:
            action = self.agent.state.act.get("action", "")
            # target = self.agent.state.act.get("target", "")
            if action == "use":
                equipment = self.agent.state.act.get("equipment", "")
                operation = self.agent.state.act.get("operation", "")
                description = ""
                menu = dict()
                # TODO: find nearest
                for e in self.agent.state.equipments:
                    if equipment in e["name"]:
                        description = e["description"]
                        menu = e["menu"]
                        break
                await self.agent.use(equipment, operation, description, menu)
                if self.agent.state.use["bought_thing"] in menu and isinstance(self.agent.state.use["amount"], int):
                    self.agent.state.use["cost"] = self.agent.state.use["amount"] * menu[self.agent.state.use["bought_thing"]]
                return {"use": self.agent.state.use, "equipment": equipment, "operation": operation}
            elif action == "chat":
                person = self.agent.state.act.get("person", "")
                topic = self.agent.state.act.get("topic", "")
                await self.agent.chat(person, topic)
                return {"chat": self.agent.state.chat, "person": person, "topic": topic}
            elif action == "experience":
                experienceID = self.agent.state.act.get("experienceID", "")
                print(experienceID)
                experience = self.agent.memory_data.experience.get(experienceID, dict())
                print(experience)
                if not experience:
                    experience = dict()
                acts = experience.get("acts", list())
                act = dict()
                if acts:
                    act = acts.pop(0)
                print(act)
                self.agent.cache.experience_cache = acts
                # if acts:
                if not act:
                    return {"use": {"continue_time": 0, "result": "fail", "cost": 0, "earn": 0}, "equipment": "", "operation": "nothing to do"}
                self.agent.state.execute_experience = True
                print(act)
                return {"use": {"continue_time": act["continue_time"], "result": act["result"], "cost": act.get("cost", 0), "earn": act.get("earn", 0)}, "equipment": act['equipment'], "operation": act['operation']}
    
    async def _chat(self, person: str, topic: str) -> Dict[str, Any]:
        await self.agent.chat(person, topic)
        return {"chat": self.agent.state.chat, "person": person, "topic": topic}

    def _addBuilding(self, building_name: str):
        self.agent.state.buildings.append(building_name)
    
    async def _store_memory(self):
        await self.agent.memory_store()
        if self.agent.state.memory:
            people = self.agent.state.memory.get("people", dict())
            for name, info in people.items():
                if name not in self.agent.memory_data.people:
                    self.agent.memory_data.people[name] = {
                        "name": name,
                        "relationShip": "",
                        "episodicMemory": list(),
                    }
                self.agent.memory_data.people[name]["impression"] = info["impression"]
                self.agent.memory_data.people[name]["episodicMemory"].append(info["newEpisodicMemory"])
            building = self.agent.state.memory.get("building", dict())
            for name, info in building.items():
                if name not in self.agent.memory_data.building:
                    self.agent.memory_data.building[name] = {
                        "name": name,
                        "relationShip": "",
                        "episodicMemory": list(),
                    }
                self.agent.memory_data.building[name]["impression"] = info["impression"]
                self.agent.memory_data.building[name]["episodicMemory"].append(info["newEpisodicMemory"])
        return {"stored": True}
        # self.agent.state.buildings.append(building_name)
