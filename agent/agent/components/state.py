from typing import List, Dict, Any
import datetime

class State:
    def __init__(self) -> None:
        # Buildings in scene
        self.buildings = list()
        # Equipments in sight
        # [{"name": "xxx", "description": "xxx"}]
        self.equipments = list()
        # People in sight
        self.people = list()
        self.cash = 10000
        self.execute_experience = False
        self.game_time = datetime.datetime.now()

        self.question = {}
        self.question_prompt = ""
        self.answer = {}
        self.answer_prompt = ""
        self.plan = {}
        self.plan_prompt = ""
        self.act = {}
        self.act_prompt = ""
        self.use = {}
        self.use_prompt = ""
        self.chat = {}
        self.chat_prompt = ""
        self.critic = {}
        self.critic_prompt = ""
        self.memory = {}
        self.memory_prompt = ""
    
    def get_prompts(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "question_prompt": self.question_prompt,
            "answer": self.answer,
            "answer_prompt": self.answer_prompt,
            "plan": self.plan,
            "plan_prompt": self.plan_prompt,
            "act": self.act,
            "act_prompt": self.act_prompt,
            "use": self.use,
            "use_prompt": self.use_prompt,
            "chat": self.chat,
            "chat_prompt": self.chat_prompt,
            "critic": self.critic,
            "critic_prompt": self.critic_prompt,
            "memory": self.memory,
            "memory_prompt": self.memory_prompt,
        }
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "buildings": self.buildings,
            "equipments": self.equipments,
            "people": self.people,
            "cash": self.cash,
            "execute_experience": self.execute_experience,
            "game_time": self.game_time.timestamp(),
            "question": self.question,
            "question_prompt": self.question_prompt,
            "answer": self.answer,
            "answer_prompt": self.answer_prompt,
            "plan": self.plan,
            "plan_prompt": self.plan_prompt,
            "act": self.act,
            "act_prompt": self.act_prompt,
            "use": self.use,
            "use_prompt": self.use_prompt,
            "chat": self.chat,
            "chat_prompt": self.chat_prompt,
            "critic": self.critic,
            "critic_prompt": self.critic_prompt,
            "memory": self.memory,
            "memory_prompt": self.memory_prompt,
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.buildings = obj.get("buildings", list())
        self.equipments = obj.get("equipments", list())
        self.people = obj.get("people", list())
        self.cash = obj.get("cash", 10000)
        self.execute_experience = obj.get("execute_experience", False)
        self.game_time = datetime.datetime.fromtimestamp(obj.get("game_time", 0))

        self.question = obj.get("question", {})
        self.question_prompt = obj.get("question_prompt", "")
        self.answer = obj.get("answer", {})
        self.answer_prompt = obj.get("answer_prompt", "")
        self.plan = obj.get("plan", {})
        self.plan_prompt = obj.get("plan_prompt", "")
        self.act = obj.get("act", {})
        self.act_prompt = obj.get("act_prompt", "")
        self.use = obj.get("use", {})
        self.use_prompt = obj.get("use_prompt", "")
        self.chat = obj.get("chat", {})
        self.chat_prompt = obj.get("chat_prompt", "")
        self.critic = obj.get("critic", {})
        self.critic_prompt = obj.get("critic_prompt", "")
        self.memory = obj.get("memory", {})
        self.memory_prompt = obj.get("memory_prompt", "")
