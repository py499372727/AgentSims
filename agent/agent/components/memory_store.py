from typing import List, Dict, Any

class MemoryData:
    def __init__(self) -> None:
        # {peopleName: { name, relationShip, impression, episodicMemory: ["", "", ...] }}
        self.people = dict()
        # {id: { id, plan, acts: ["", "", ...] }}
        self.experience = dict()
        # {buildingName: { name, relationShip, impression, episodicMemory: ["", "", ...] }}
        self.building = dict()
    
    def get_impression_memory(self) -> Dict[str, Any]:
        return {
            "people": {k: {"name": v["name"], "relationShip": v["relationShip"], "impression": v["impression"]} for k, v in self.people.items()},
            "building": {k: {"name": v["name"], "relationShip": v["relationShip"], "impression": v["impression"]} for k, v in self.building.items()},
        }
    
    def get_memory(self) -> Dict[str, Any]:
        return {
            "people": self.people,
            "building": self.building
        }
    
    def get_people_memory(self, name: str) -> Dict[str, Any]:
        return self.people.get(name, dict())
    
    def get_building_memory(self, name: str) -> Dict[str, Any]:
        return self.building.get(name, dict())
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "people": self.people,
            "experience": self.experience,
            "building": self.building,
        }
    
    def from_json(self, obj: Dict[str, Any]):
        self.people = obj.get("people", dict())
        self.experience = obj.get("experience", dict())
        self.building = obj.get("building", dict())

class People:
    def __init__(self, name: str, relationShip: str, impression: str) -> None:
        self.name = name
        self.relationShip = relationShip
        self.impression = impression
        self.episodicMemory = list()
    
    def add_episodic_memory(self, memory: str) -> None:
        self.episodicMemory.append(memory)

class Experience:
    def __init__(self, plan: str, acts: List[str]) -> None:
        self.plan = plan
        self.acts = acts

class Building:
    def __init__(self, name, relationShip, impression) -> None:
        self.name = name
        self.relationShip = relationShip
        self.impression = impression
        self.episodicMemory = list()
    
    def add_episodic_memory(self, memory: str) -> None:
        self.episodicMemory.append(memory)
