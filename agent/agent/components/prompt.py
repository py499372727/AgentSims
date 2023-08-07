from typing import List, Dict, Any
from agent.prompt.prompt import Prompt

class Prompts:
    def __init__(self) -> None:
        self.prompts = {
            "qa_framework_question": Prompt("qa_framework_question"),
            "qa_framework_answer": Prompt("qa_framework_answer"),
            "plan": Prompt("plan"),
            "act": Prompt("act"),
            "use": Prompt("use"),
            "chat": Prompt("chat"),
            "critic": Prompt("critic"),
            "memory_store": Prompt("memory_store"),
        }
    
    def get_text(self, part: str, params: Dict[str, Any]) -> str:
        return self.prompts[part].to_string(params)
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "prompts": {k: v.part for k, v in self.prompts.items()},
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.prompts = {k: Prompt(v) for k, v in obj.get("prompts", {
            "qa_framework_question": "qa_framework_question",
            "qa_framework_answer": "qa_framework_answer",
            "plan": "plan",
            "act": "act",
            "use": "use",
            "chat": "chat",
            "critic": "critic",
            "memory_store": "memory_store",
        }).items()}
