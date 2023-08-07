from typing import List, Dict, Any

class Cache:
    def __init__(self) -> None:
        self.act_cache = list()
        # [{"speaker": "", "content": ""}]
        self.chat_cache = list()
        self.memory_cache = list()
        # cache experience after plan finished
        self.experience_cache = list()
        self.plan_cache = list()
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "act_cache": self.act_cache,
            "chat_cache": self.chat_cache,
            "memory_cache": self.memory_cache,
            "experience_cache": self.experience_cache,
            "plan_cache": self.plan_cache,
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.act_cache = obj.get("act_cache", list())
        self.chat_cache = obj.get("chat_cache", list())
        self.memory_cache = obj.get("memory_cache", list())
        self.experience_cache = obj.get("experience_cache", list())
        self.plan_cache = obj.get("plan_cache", list())
