from model.single_model_base import SingleModelBase


class EquipmentsModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)
        
        """
        equipments: [{
            id: equipment ID,
            n: equipment name,
            d: description,
            o: owner,
            t: equipment type,
            lx: leftX,
            ty: topY,
            rx: rightX,
            by: bottomY,
            r: rotation,
            
            b: building belong,
            fs: functions [{ cost: , earn: , action:  }]
            m: economics.menu,
            s: economics.salary
        } ...]
        """

        # Player's leader ID, If type=member, follow whom.
        self.equipments = None
        # ORM mapping.
        self.orm['equipments'] = SingleModelBase.OBJECT

    def init(self):
        self.equipments = list()

    def total(self):
        return len(self.equipments)
    
    def init_equipments(self):
        basic_equipments = self.app.get_framework_config().equipments
        for equipment in basic_equipments:
            equipment_config = self.app.get_equipment_config(equipment["t"])
            economic = dict()
            if equipment_config.economic:
                economic = self.app.get_economic_config(equipment_config.economic).to_json()
            self.equipments.append({
                'id': equipment["id"],
                'n': equipment["n"],
                'd': equipment_config.description,
                'o': f"Player-{self.id}",
                't': equipment["t"],
                'lx': equipment["lx"],
                'ty': equipment["ty"],
                'rx': equipment["rx"],
                'by': equipment["by"],
                'r': equipment["r"],
                'b': equipment["b"],
                'fs': equipment_config.functions,
                "m": economic.get("menu", dict()),
                "s": economic.get("salary", 0),
            })

    def add_equipment(self, name, owner, type, leftX, topY, rightX, bottomY, rotation, buildingBelong, functions):
        id = self.get_idle_id(self.equipments, min=1, max=200)
        equipment_config = self.app.get_equipment_config(type)
        economic = dict()
        if equipment_config.economic:
            economic = self.app.get_economic_config(equipment_config.economic).to_json()
        self.equipments.append({
            'id': id,
            'n': name,
            'd': equipment_config.description,
            'o': owner,
            't': type,
            'lx': leftX,
            'ty': topY,
            'rx': rightX,
            'by': bottomY,
            'r': rotation,
            'b': buildingBelong,
            'fs': functions,
            "m": economic.get("menu", dict()),
            "s": economic.get("salary", 0),
        })
        return id
    
    def get_equipment(self, eid):
        for e in self.equipments:
            if e['id'] == eid:
                return e
    
    def get_equipment_by_name_and_position(self, name, x, y):
        nearest = -1
        eid = 0
        e_model = None
        for e in self.equipments:
            if e['n'] == name:
                diff = min(abs(e['lx']-x), abs(e['rx']-x)) + min(abs(e['ty']-y), abs(e['by']-y))
                if nearest == -1 or diff < nearest:
                    nearest = diff
                    eid = e["id"]
                    e_model = e
        return eid, e_model
