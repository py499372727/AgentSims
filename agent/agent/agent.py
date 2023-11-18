from typing import List, Dict, Any

from agent.agent.components.memory_store import MemoryData
from agent.agent.components.state import State
from agent.agent.components.cache import Cache
from agent.agent.components.prompt import Prompts
from agent.agent.components.controller import Controller
from agent.utils.llm import LLMCaller
from agent.prompt.utils import TradeFailure_NoMoney

import re
import os
import json
import datetime

abs_path = os.path.dirname(os.path.realpath(__file__))


class Agent:
    def __init__(self, name: str, bio: str, goal: str, model: str, memorySystem: str, planSystem: str, buildings: List[str], cash: int, start_time: float) -> None:
        self.memory_data = MemoryData()
        self.state = State()
        self.start_time = datetime.datetime.fromtimestamp(start_time / 1000)
        self.state.buildings = buildings
        self.state.cash = cash
        # todo set the profession from param
        self.state.profession = ""
        self.cache = Cache()
        self.name = name
        self.bio = bio
        self.goal = goal
        if model:
            self.caller = LLMCaller(model)
        self.prompt_log_path = os.path.join(abs_path, "..", "..", "logs", f"{name}_prompt.txt")
        self.prompts = Prompts()
        self.controller = Controller(memorySystem, planSystem)

    def log_prompt(self, input: Any, sperate_signal:str ='\n'):
        if not sperate_signal.endswith('\n'): sperate_signal += '\n'
        if not isinstance(input, str):
            input = json.dumps(input, ensure_ascii=False, separators=(",", ":"))
        with open(self.prompt_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{sperate_signal}{input}\n")

    async def plan(self) -> None:
        # QAFramework Experience
        if self.controller.planSystem == "QAFramework":
            await self._qa_framework()
        game_time = self.get_game_time()
        self.state.plan_prompt = self.prompts.get_text("plan", {
            "{time}": game_time,
            "{plan_cache}": self.cache.plan_cache,
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": self.memory_data.get_impression_memory(),
            "{buildings}": self.state.buildings,
            "{question}": self.state.question,
            "{answer}": self.state.answer,
            "{npc_items}": self.state.npc_items,
        })
        self.log_prompt(self.state.plan_prompt, '[**Plan_Prompt**]\n')
        # {"building": "xxx", "purpose": "xxx"}
        self.state.plan = await self.caller.ask(self.state.plan_prompt)
        self.log_prompt(self.state.plan,'[**Plan_Res**]\n')

    async def use(
            self,
            equipment: str,
            act_operation: str,
            description: str,
            # menu: str
    ) -> None:
        # can fail
        # equipment returns usage infomation
        self.state.use_prompt = self.prompts.get_text("use", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{buildings}": self.state.buildings,
            "{plan}": self.state.plan,
            "{act}": self.state.act,
            "{equipment}": equipment,
            "{operation}": act_operation,
            "{description}": description,
            "{act_cache}": self.cache.act_cache,
            "{equipment_items}": self.state.equipments_items,
            "{npc_items}": self.state.npc_items
        })
        # act plan 都需要输入个人身上物品333
        if 'counter' in equipment:
            if 'buy' in act_operation:
                results = self.state.equipments_items # when 'buy', results contains commodities for selling
                self.state.use = {"continue_time" : 6480000000,
                                    "result" : results
                                }
            elif 'sell' in act_operation:
                self.state.use = {"continue_time": 6480000000,
                                  "result": self.state.npc_items
                                  }
        else:
            self.log_prompt(self.state.use_prompt, '[**Use_Prompt**]')
            self.state.use = await self.caller.ask(self.state.use_prompt)
        self.log_prompt(self.state.use, '[**Use_Res**]')

        if "continue_time" in self.state.use and isinstance(self.state.use["continue_time"], str):
            if re.findall(r"\d+?", self.state.use["continue_time"], re.DOTALL):
                time_string = self.state.use["continue_time"]
                base = 60 * 60 * 1000
                if "minute" in time_string:
                    base = 60 * 1000
                    time_string = time_string.replace("minutes", "").replace("minute", "")
                elif "hour" in time_string:
                    base = 60 * 60 * 1000
                    time_string = time_string.replace("hours", "").replace("hour", "")
                elif "day" in time_string:
                    base = 24 * 60 * 60 * 1000
                    time_string = time_string.replace("days", "").replace("day", "")
                elif "month" in time_string:
                    base = 30 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("months", "").replace("month", "")
                elif "season" in time_string:
                    base = 3 * 30 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("seasons", "").replace("season", "")
                elif "year" in time_string:
                    base = 365 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("years", "").replace("year", "")
                elif "decade" in time_string:
                    base = 10 * 365 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("decades", "").replace("decade", "")
                elif "century" in time_string:
                    base = 100 * 365 * 24 * 60 * 60 * 1000
                    time_string = time_string.replace("centuries", "").replace("century", "")
                elif time_string.endswith("s"):
                    time_string = re.findall(r"\d+", time_string, re.DOTALL)[0]
                    if float(time_string) < 1:
                        time_string = "0.5"
                self.state.use["continue_time"] = int(float(time_string) * base)
            else:
                self.state.use["continue_time"] = 30 * 60 * 1000
        if "continue_time" not in self.state.use:
            self.state.use["continue_time"] = 30 * 60 * 1000
        if "result" not in self.state.use:
            self.state.use["result"] = "failed"
        if "bought_thing" not in self.state.use:
            self.state.use["bought_thing"] = ""
        if "amount" not in self.state.use:
            self.state.use["amount"] = 0
        else:
            try:
                self.state.use["amount"] = int(self.state.use["amount"])
            except Exception:
                self.state.use["amount"] = 1
        if "earn" not in self.state.use:
            self.state.use["earn"] = 0
        else:
            try:
                self.state.use["earn"] = int(self.state.use["earn"])
            except Exception:
                self.state.use["earn"] = 200
        self.log_prompt(self.state.use, '[**Use_Res**]')

        # 判断是否要进行交易
        if "buy" in act_operation or "sell" in act_operation:
            await self.trade()

        self.cache.act_cache.append({
            "equipment": equipment,
            "operation": act_operation,
            "continue_time": self.state.use['continue_time'],
            "result": self.state.use['result'],
            "tradeResult": self.state.trade
        })

    # 交易
    async def trade(self):
        """
         transaction_records参数格式：[
             {"price": price,
              "fromUid": fromUid,
              "toUid": toUid,
              "time": time,
                "actionType": actionType}
                ]

            输出：买{"actionType": "buy","itemid" : "xxx"}
        卖{"actionType": "sell","itemid" : "xxx","price" ： "xxx"}
        """
        ## give all equipment_item info to the agent for decision
        equipment_items = self.state.use['result'] # all relavent items info [{'id': 1, 'name': 'ice_cream_1', 'price': '50', 'belongUid': 1}, {...}]
        
        self.state.trade_prompt = self.prompts.get_text("trade", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": self.state.memory,
            "{plan}": self.state.plan,
            "{equipment_items}": equipment_items,
            "{npc_items}": self.state.npc_items,
            # "{transaction_records}": transaction_records
        })
        self.log_prompt(self.state.trade_prompt, '[**Trade_Prompt**]')
        self.state.trade = await self.caller.ask(self.state.trade_prompt)
        if self.state.trade['actionType'] == 'buy':
            item_price = -1
            for itm in equipment_items:
                if itm['id'] == int(self.state.trade['itemid']):
                    item_price = int(itm['price'])
                    break
            assert item_price > 0, f' item to buy not found, target itemid: {int(self.state.trade["itemid"])}, item list:\n {equipment_items}'
            self.state.trade['price'] = item_price
            if self.state.cash - item_price < 0:
                self.state.trade['actionType'] = TradeFailure_NoMoney

        self.log_prompt(self.state.trade, '[**Trade_Res**]')


    async def memory_store(self) -> None:
        # memory cache -> memory data
        # self.experience()
        self.state.memory_prompt = self.prompts.get_text("memory_store", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": self.memory_data.get_memory(),
            "{buildings}": self.state.buildings,
            "{plan}": self.state.plan,
            "{act_cache}": self.cache.act_cache,
            "{chatCache}": self.cache.chat_cache,
            "{issuccess}": self.state.critic.get("result", "fail"),
        })
        self.log_prompt(self.state.memory_prompt,"[**Mem_Prompt**]")
        # {
        #    "people": {"John": {"impression": "xxx", "newEpisodicMemory": "xxx"}},
        #    "building": {"School": {"impression": "xxx", "newEpisodicMemory": "xxx"}},
        # }
        self.state.memory = await self.caller.ask(self.state.memory_prompt)
        self.log_prompt(self.state.memory, "[**Mem_Res**]")

    def to_json(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.timestamp(),
            "memory_data": self.memory_data.to_json(),
            "state": self.state.to_json(),
            "cache": self.cache.to_json(),
            "caller": self.caller.model,
            "prompts": self.prompts.to_json(),
            "controller": self.controller.to_json(),
            "name": self.name,
            "bio": self.bio,
            "goal": self.goal,
        }

    def from_json(self, obj: Dict[str, Any]):
        self.start_time = datetime.datetime.fromtimestamp(obj.get("start_time", 0))
        self.memory_data.from_json(obj.get("memory_data", dict()))
        self.state.from_json(obj.get("state", dict()))
        self.cache.from_json(obj.get("cache", dict()))
        self.caller = LLMCaller(obj.get("caller", "gpt-3.5"))
        self.prompts.from_json(obj.get("prompts", dict()))
        self.controller.from_json(obj.get("controller", dict()))
        self.name = obj.get("name", "")
        self.bio = obj.get("bio", "")
        self.goal = obj.get("goal", "")

    def cover_prompt(self, prompt_type: str, text: str) -> None:
        self.prompts.prompts[prompt_type].cover(text)

    async def _qa_framework(self) -> None:
        """
        flexible
        """
        # Bio Goal Memory Buildings
        self.state.question_prompt = self.prompts.get_text("qa_framework_question", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": self.memory_data.get_impression_memory(),
            "{buildings}": self.state.buildings,
        })
        self.log_prompt(self.state.question_prompt, "[**Ques_Prompt**]")
        self.state.question = await self.caller.ask(self.state.question_prompt)
        self.log_prompt(self.state.question, "[**Ques_Res**]")
        self.state.answer_prompt = self.prompts.get_text("qa_framework_answer", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": self.memory_data.get_impression_memory(),
            "{buildings}": self.state.buildings,
            "{question}": self.state.question,
        })
        self.log_prompt(self.state.answer_prompt, "[**Ans_Prompt**]")
        self.state.answer = await self.caller.ask(self.state.answer_prompt)
        self.log_prompt(self.state.answer, "[**Ans_Res**]")

    async def act(self) -> None:
        memory = {
            "people": {k: {"name": v["name"], "relationShip": v["relationShip"], "impression": v["impression"]} for k, v in self.memory_data.people.items()},
            "building": self.memory_data.get_building_memory(self.state.plan.get("building", "")),
            # "experience": self.memory_data.experience,
        }
        # peopleInVision equipmentInVision
        self.state.act_prompt = self.prompts.get_text("act", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": memory,
            # todo Haoran
            "{equipments}": [{"name": f["name"], "equipmentId": f["id"]} for f in self.state.equipments],
            "{people}": self.state.people,
            "{plan}": self.state.plan,
            "{act_cache}": self.cache.act_cache,
            "{npc_items}": self.state.npc_items,
            "{experience}": self.memory_data.experience,
        })
        self.log_prompt(self.state.act_prompt, "[**Act_Prompt**]")
        # {"action": "use/chat/experience", "equipment": "ifUse",equipmentId："1", "operation": "ifUse", "person": "ifChat", "topic": "ifChat", "experienceID": "id"}
        self.state.act = await self.caller.ask(self.state.act_prompt)
        self.log_prompt(self.state.act,"[**Act_Res**]")

    async def chat(self, person: str, topic: str) -> None:
        self.state.chat_prompt = self.prompts.get_text("chat", {
            "{name}": self.name,
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": self.memory_data.get_people_memory(person),
            "{buildings}": self.state.buildings,
            "{plan}": self.state.plan,
            "{act}": self.state.act,
            "{chatTo}": person,
            "{chatTopic}": topic,
            "{chats}": self.cache.chat_cache,
        })
        # {"context": "xxx"}
        self.log_prompt(self.state.chat_prompt,"[**Chat_Prompt**]")
        self.state.chat = await self.caller.ask(self.state.chat_prompt)
        self.log_prompt(self.state.chat, "[**Chat_Res**]")

    async def critic(self) -> None:
        # _use: usage infomation plan
        # decides whether plan finished
        memory = self.memory_data.get_impression_memory()
        memory["experience"] = self.memory_data.experience
        self.state.critic_prompt = self.prompts.get_text("critic", {
            "{bio}": self.bio,
            "{goal}": self.goal,
            "{memory}": memory,
            "{buildings}": self.state.buildings,
            "{plan}": self.state.plan,
            "{act}": self.state.act,
            "{use}": self.state.use,
            "{act_cache}": self.cache.act_cache,
            "{num_acts}": len(self.cache.act_cache)
        })
        self.log_prompt(self.state.critic_prompt, "[**Crit_Prompt**]")
        # {"result": "success", "fitScore": 0-10}
        # {"result": "fail", "needToDo": "xxx"}
        # {"result": "not_finished_yet"}
        self.state.critic = await self.caller.ask(self.state.critic_prompt)
        self.log_prompt(self.state.critic, "[**Crit_Res**]")

    def experience(self) -> None:
        # packing act caches & plan to experience
        # self.cache.experienceCache.append({"plan": self.state.plan, "acts": self.cache.act_cache})
        if self.cache.act_cache:
            print(self.cache.act_cache)
            eid = str(len(self.memory_data.experience) + 1)
            self.memory_data.experience[eid] = {"experienceID": eid, "plan": self.state.plan,
                                                "acts": self.cache.act_cache.copy()}
            print(self.memory_data.experience[eid])
            self.cache.act_cache = list()
            print(self.cache.act_cache)
            print(self.memory_data.experience[eid])
            # self.cache.plan_cache.append({"time": self.get_game_time(), "plan": self.state.plan})

    def get_game_time(self):
        game_time = self.state.game_time - self.start_time
        return f"day {game_time.days} {self.state.game_time.strftime('%H:%M')}"



