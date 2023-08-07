from typing import List, Dict, Any

class Controller:
    def __init__(self, memorySystem: str, planSystem: str) -> None:
        self.memorySystem = memorySystem
        self.planSystem = planSystem
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "memorySystem": self.memorySystem,
            "planSystem": self.planSystem,
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.memorySystem = obj.get("memorySystem", "LongShortTermMemories")
        self.planSystem = obj.get("planSystem", "QAFramework")
