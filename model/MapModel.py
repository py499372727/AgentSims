from model.single_model_base import SingleModelBase


class MapModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)

        self.seed = None
        self.centerX = None
        self.centerY = None
        self.width = None
        self.height = None
        
        self.map = None
        self.name2uid = None
        # ORM mapping.
        self.orm['seed'] = SingleModelBase.INT
        self.orm['centerX'] = SingleModelBase.INT
        self.orm['centerY'] = SingleModelBase.INT
        self.orm['width'] = SingleModelBase.INT
        self.orm['height'] = SingleModelBase.INT
        self.orm['map'] = SingleModelBase.OBJECT
        self.orm['name2uid'] = SingleModelBase.OBJECT

    def init(self):
        self.seed = 0
        self.centerX = 0
        self.centerY = 0
        self.width = 143
        self.height = 81
        self.map = dict()
        self.name2uid = dict()

    def init_map(self):
        # setTownCenter
        self.map = self.app.get_framework_config().map
        # self.setValues(-1, -1, 1, 1, "building", 1)
        # self.setValues(-1, -1, 1, 1, "block", 1)
        # self.setValue(0, 1, "equipment", 1)
    
    def get_empty_tile(self, x1, y1, x2, y2):
        centerX = (x1 + x2) // 2
        centerY = (y1 + y2) // 2
        # bottom-right
        for x in range(centerX, x2+1):
            for y in range(centerY, y2+1):
                info = self.map.get(str(x), dict()).get(str(y), dict())
                # self.setValue(x, y, key, value)
                if not info.get("block") and not info.get("uid") and not info.get("equipment"):
                    return x, y
        # bottom-left
        for x in range(centerX-1, x1-1, -1):
            for y in range(centerY, y2+1):
                info = self.map.get(str(x), dict()).get(str(y), dict())
                # self.setValue(x, y, key, value)
                if not info.get("block") and not info.get("uid") and not info.get("equipment"):
                    return x, y
        # top-right
        for x in range(centerX, x2+1):
            for y in range(centerY-1, y1-1, -1):
                info = self.map.get(str(x), dict()).get(str(y), dict())
                # self.setValue(x, y, key, value)
                if not info.get("block") and not info.get("uid") and not info.get("equipment"):
                    return x, y
        # top-left
        for x in range(centerX-1, x1-1, -1):
            for y in range(centerY-1, y1-1, -1):
                info = self.map.get(str(x), dict()).get(str(y), dict())
                # self.setValue(x, y, key, value)
                if not info.get("block") and not info.get("uid") and not info.get("equipment"):
                    return x, y
        return -1, -1

    def setValues(self, x1, y1, x2, y2, key, value):
        """
        Args:
            x1 (int): less then x2
            y1 (int): less then y2
            x2 (int): 
            y2 (int): 
            key (str): 
            value (int): 
        """
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                self.setValue(x, y, key, value)

    def setValue(self, x, y, key, value):
        if str(x) not in self.map:
            self.map[str(x)] = dict()
        if str(y) not in self.map[str(x)]:
            self.map[str(x)][str(y)] = dict()
        print(f"map setting: ({x},{y}).{key} = {value}")
        self.map[str(x)][str(y)][key] = value
    
    def hasEntityInRange(self, x1, y1, x2, y2):
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                if self.hasEntity(x, y):
                    return True
        return False
    
    def hasEntity(self, x, y):
        return self.map.get(str(x), dict()).get(str(y), dict())

    def add_uid(self, x, y, uid, name):
        self.setValue(x, y, "uid", uid)
        self.name2uid[name] = uid

    def removeValue(self, x, y, key):
        if x not in self.map:
            self.map[x] = dict()
        if y not in self.map[x]:
            self.map[x][y] = dict()
        del self.map[x][y][key]

    def moveEntity(self, x1, y1, x2, y2, entity=None):
        if not entity:
            entity = self.map.get(str(x1), dict()).get(str(y1), dict()).get("uid")
            if not entity:
                return False
        target = self.map.get(str(x2), dict()).get(str(y2), dict()).get("uid")
        if not target:
            if str(x1) in self.map and str(y1) in self.map[str(x1)] and "uid" in self.map[str(x1)][str(y1)]:
                del self.map[str(x1)][str(y1)]["uid"]
            if str(x2) not in self.map:
                self.map[str(x2)] = dict()
            if str(y2) not in self.map[str(x2)]:
                self.map[str(x2)][str(y2)] = dict()
            self.map[str(x2)][str(y2)]["uid"] = entity
            return True
        return False
    
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, x, y):
        target = self.map.get(str(x), dict()).get(str(y), dict())
        if not target:
            return True
        if target.get("block"):
            return False
        return True
        # return not self.hasEntity(x, y)
    
    def neighbors(self, x, y):
        results = []
        # 上
        if self.in_bounds(x - 1, y) and self.passable(x - 1, y):
            results.append((x - 1, y))
        # 下
        if self.in_bounds(x + 1, y) and self.passable(x + 1, y):
            results.append((x + 1, y))
        # 左
        if self.in_bounds(x, y - 1) and self.passable(x, y - 1):
            results.append((x, y - 1))
        # 右  
        if self.in_bounds(x, y + 1) and self.passable(x, y + 1):
            results.append((x, y + 1))
        return results

    def _navigate(self, start, end):
        queue = [start]
        path = {start: None}
        while queue:
            row, col = queue.pop(0)
            if (row, col) == end:
                break
            for neighbor in self.neighbors(row, col):
                if neighbor not in path:
                    queue.append(neighbor)
                    path[neighbor] = (row, col)
        route = [end]
        while end != start:
            row, col = path.get(end, (None, None))
            if row is None:
                break
            route.append((row, col))
            end = (row, col)
        route.reverse()
        return route

    def navigate(self, x1, y1, x2, y2):
        return self._navigate((x1, y1), (x2, y2))
    
    def search_sight(self, x, y):
        people = list()
        equipment = list()
        equipment_names = set()
        equipments_model = self.get_single_model("Equipments", id=self.id, create=True)
        buildings_model = self.get_single_model("Buildings", id=self.id, create=True)
        building_id = self.map.get(str(x), dict()).get(str(y), dict()).get("building", 0)
        # print("building_id:", building_id)
        if building_id:
            building = buildings_model.get_building(building_id)
            # 44, 65, 45, 59
            lx, rx, ty, by = building["lx"], building["rx"], building["ty"], building["by"]
            for x1 in range(lx, rx+1):
                for y1 in range(ty, by+1):
                    if x1 == x and y1 == y:
                        continue
                    # print(f"x: {x1}, y: {y1}, building_id: {building_id}, info: {self.map.get(str(x1), dict()).get(str(y1), dict())}")
                    if self.hasEntity(x1, y1):
                        uid = self.map[str(x1)][str(y1)].get("uid", "")
                        if uid and uid.partition("-")[0] == "NPC":
                            entity_type = uid.partition("-")[0]
                            entity_id = int(uid.partition("-")[2])
                            model = self.get_single_model(entity_type, entity_id, create=False)
                            self.name2uid[model.name] = uid
                            if model:
                                people.append(model.name)
                        equipment_id = self.map[str(x1)][str(y1)].get("equipment", "")
                        if equipment_id:
                            e = equipments_model.get_equipment(equipment_id)
                            if e and e['n'] not in equipment_names:
                                equipment.append({"id": e["id"], "building_id": e["b"], "name": e['n'], "description": e['d'], "menu": e['m']})
                                equipment_names.add(e['n'])
        else:
            for x1 in range(x-10, x+10):
                for y1 in range(y-10, y+10):
                    if x1 == x and y1 == y:
                        continue
                    if self.hasEntity(x1, y1):
                        uid = self.map[str(x1)][str(y1)].get("uid", "")
                        if uid and uid.partition("-")[0] == "NPC":
                            entity_type = uid.partition("-")[0]
                            entity_id = int(uid.partition("-")[2])
                            model = self.get_single_model(entity_type, entity_id, create=False)
                            self.name2uid[model.name] = uid
                            if model:
                                people.append(model.name)
                        equipment_id = self.map[str(x1)][str(y1)].get("equipment", "")
                        if equipment_id:
                            e = equipments_model.get_equipment(equipment_id)
                            if e and e['n'] not in equipment_names:
                                equipment.append({"id": e["id"], "building_id": e["b"], "name": e['n'], "description": e['d'], "menu": e['m']})
                                equipment_names.add(e['n'])
        print({"people": people, "equipments": equipment})
        return {"people": people, "equipments": equipment}
