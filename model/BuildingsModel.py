from model.single_model_base import SingleModelBase


class BuildingsModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)
        
        """
        buildings: [{
            id: building ID,
            n: building name,
            o: owner,
            t: building type,
            lx: leftX,
            ty: topY,
            rx: rightX,
            by: bottomY,
            r: rotation,
            x: blockX,
            y: blockY,

            eI: economic Income
            eE: economic Expenditure
            eT: economic Taxes
            hL: hire list
            hC: hire capacity

            lL: living list
            lC: living capacity
            rI: rent Income
            rT: rent Taxes
        } ...]
        """

        # Player's leader ID, If type=member, follow whom.
        self.buildings = None
        # ORM mapping.
        self.orm['buildings'] = SingleModelBase.OBJECT

    def init(self):
        self.buildings = []

    def total(self):
        return len(self.buildings)
    
    def xToBlockX(self, lx, rx):
        blocks = [
            {"lx": 0, "rx": 36, "x": 1},
            {"lx": 37, "rx": 71, "x": 2},
            {"lx": 72, "rx": 106, "x": 3},
            {"lx": 107, "rx": 143, "x": 4},
        ]
        for block in blocks:
            if lx >= block["lx"] and rx <= block["rx"]:
                return block["x"]
        return 1
    
    def yToBlockY(self, ty, by):
        blocks = [
            {"ty": 0, "by": 20, "y": 1},
            {"ty": 21, "by": 40, "y": 2},
            {"ty": 41, "by": 60, "y": 3},
            {"ty": 61, "by": 81, "y": 4},
        ]
        for block in blocks:
            if ty >= block["ty"] and by <= block["by"]:
                return block["y"]
        return 1
    
    def init_buildings(self):
        basic_buildings = self.app.get_framework_config().buildings
        building_mapping = dict()
        basic_equipments = self.app.get_framework_config().equipments
        for equipment in basic_equipments:
            if equipment["b"] not in building_mapping:
                building_mapping[equipment["b"]] = {"hireCapacity": 0, "livingCapacity": 0}
            equipment_config = self.app.get_equipment_config(equipment["t"])
            building_mapping[equipment["b"]]["hireCapacity"] += equipment_config.hireCapacity
            building_mapping[equipment["b"]]["livingCapacity"] += equipment_config.livingCapacity
        for building in basic_buildings:
            self.buildings.append({
                'id': building["id"],
                'n': building["n"],
                'o': f"Player-{self.id}",
                't': building["t"],
                'lx': building["lx"],
                'ty': building["ty"],
                'rx': building["rx"],
                'by': building["by"],
                'r': building["r"],
                "x": self.xToBlockX(building["lx"], building["rx"]),
                "y": self.yToBlockY(building["ty"], building["by"]),
                'eI': 0,
                'eE': 0,
                'eT': 0,
                'hL': list(),
                'hC': building_mapping.get(building["id"], dict()).get("hireCapacity", 0),
                'lL': list(),
                'lC': building_mapping.get(building["id"], dict()).get("livingCapacity", 0),
                'rI': 0,
                'rT': 0,
            })
    
    def add_building(self, name, owner, type, leftX, topY, rightX, bottomY, rotation, hireCapacity, livingCapacity):
        id = self.get_idle_id(self.buildings, min=1, max=200)
        self.buildings.append({
            'id': id,
            'n': name,
            'o': owner,
            't': type,
            'lx': leftX,
            'ty': topY,
            'rx': rightX,
            'by': bottomY,
            'r': rotation,
            "x": self.xToBlockX(leftX, rightX),
            "y": self.yToBlockY(topY, bottomY),
            'eI': 0,
            'eE': 0,
            'eT': 0,
            'hL': list(),
            'hC': hireCapacity,
            'lL': list(),
            'lC': livingCapacity,
            'rI': 0,
            'rT': 0,
        })
        return id
    
    def is_empty(self, x, y):
        for b in self.buildings:
            if b["x"] == x and b["y"] == y:
                return False
        return True

    def get_names(self):
        return [x['n'] for x in self.buildings]

    def add_tenent(self, building_id, uid):
        for b in self.buildings:
            if b["id"] == building_id:
                b["lL"].append(uid)
                return True
        return False

    def add_employee(self, building_id, uid):
        for b in self.buildings:
            if b["id"] == building_id:
                b["lL"].append(uid)
                return True
        return False

    def get_building(self, bid):
        for b in self.buildings:
            if b["id"] == bid:
                return b
    
    def get_building_by_name(self, name):
        for b in self.buildings:
            if b["n"] == name:
                return b
    
    def increase_economic_income(self, building_id, amount, uid):
        for b in self.buildings:
            if b["id"] == building_id:
                b["eI"] += amount
                self.app.send(f"Player-{self.id}", {"code": 200, "uri": "increaseBuildingIncome", "uid": uid, "data": {"uid": f"Player-{self.id}", "building_id": building_id, "income": b["eI"], "amount": amount}})
                return True
        return False
