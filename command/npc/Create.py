from command.command_base import CommandBase
from agent.actor import Actor

class Create(CommandBase):
    """Player create npc."""
    
    def flush_str(self, string):
        if isinstance(string, str):
            string = string.strip().strip("\u200B")
        return string

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', 'asset', 'model', 'memorySystem', 'planSystem', 'homeBuilding', 'workBuilding', 'nickname', 'bio', 'goal', 'cash']):
            return False

        player_uid, asset, model, memorySystem, planSystem, home_building_id, work_building_id, nickname, bio, goal, cash = params['uid'], params['data']['asset'], params['data']['model'], params['data']['memorySystem'], params['data']['planSystem'], params['data']['homeBuilding'], params['data']['workBuilding'], params['data']['nickname'], params['data']['bio'], params['data']['goal'], params['data']['cash']
        asset = self.flush_str(asset)
        model = self.flush_str(model)
        memorySystem = self.flush_str(memorySystem)
        planSystem = self.flush_str(planSystem)
        nickname = self.flush_str(nickname)
        bio = self.flush_str(bio)
        goal = self.flush_str(goal)
        if not asset:
            return self.error("asset is blank")
        if not model:
            return self.error("model is blank")
        if not memorySystem:
            return self.error("memorySystem is blank")
        if not planSystem:
            return self.error("planSystem is blank")
        if not nickname:
            return self.error("nickname is blank")
        if not bio:
            return self.error("bio is blank")
        if not goal:
            return self.error("goal is blank")

        # check valid
        npc_configs = self.app.get_npc_config()
        if asset not in npc_configs.assets:
            try:
                asset = npc_configs.assets[int(asset)]
            except Exception:
                return self.error('invalid asset')
        if asset not in npc_configs.assets or model not in npc_configs.models or memorySystem not in npc_configs.memorySystems or planSystem not in npc_configs.planSystems:
            return self.error('invalid params')
        # for controller in controllers:
        #     if controller not in npc_configs.controllers:
        #         return self.error('invalid params')

        # Get npc's Unique ID.
        account_model = self.get_model('NPCRegister')
        id = account_model.find_id(f'{player_uid}-{nickname}')
        registered = False
        if id <= 0:
            id = account_model.reg_npc(f'{player_uid}-{nickname}')
            if id <= 0:
                return self.error('register npc failed')
        else:
            registered = True
        uid = self.gen_token("NPC", id)

        npcs_model = self.get_single_model("NPCs", create=False)
        if not npcs_model:
            return self.error("player's npcs not found")
        # if not registered:
        npcs_model.add_npc({"id": id, "name": nickname})
        npcs_model.save()
        
        player_model = self.get_single_model("Player", create=False)
        if not player_model:
            return self.error("player's info not found")
        if not player_model.change_revenue(cash + 2000, player_uid, False):
            return self.error("lack of revenue to invite")
        player_model.save()

        buildings_model = self.get_single_model("Buildings", create=False)
        if not buildings_model:
            return self.error("map's buildings not found")
        home_building = buildings_model.get_building(home_building_id)
        if not home_building:
            return self.error("home building not found")
        if len(home_building.get("lL", list())) >= home_building.get("lC", 0):
            return self.error("over home capacity limit")
        lx, ty, rx, by = home_building["lx"], home_building["ty"], home_building["rx"], home_building["by"]
        work_building = buildings_model.get_building(work_building_id)
        if not work_building:
            work_building_id = 0
        # if not work_building:
        #     return self.error("work building not found")
        # if len(work_building.get("hL", list())) >= work_building.get("hC", 0):
        #     return self.error("over work capacity limit")
        # building_id = 0
        # hire_building_id = 0
        # for building in buildings_model.buildings:
        #     if len(building["lL"]) < building["lC"]:
        #         lx, ty, rx, by = building["lx"], building["ty"], building["rx"], building["by"]
        #         building_id = building["id"]
        #     if len(building["hL"]) < building["hC"]:
        #         hire_building_id = building["id"]
        #     if building_id > 0 and hire_building_id > 0:
        #         break
        # else:
        #     return self.error("over capacity limit")

        map_model = self.get_single_model("Map", create=False)
        if not map_model:
            return self.error("map not found")
        x, y = map_model.get_empty_tile(lx, ty, rx, by)
        
        buildings_model.add_tenent(home_building_id, uid)
        if work_building_id:
            buildings_model.add_employee(work_building_id, uid)
        buildings_model.save()
        
        npc_model = self.get_single_model("NPC", id=id, create=True)
        npc_model.name = nickname
        npc_model.map = self.id
        # TODO: If agent use websocket connect with server
        # Then don't set server and use this field to search npcs not linked
        npc_model.server = uid
        npc_model.cash = cash
        npc_model.x = x
        npc_model.y = y
        npc_model.home_building = home_building_id
        npc_model.work_building_ = work_building_id
        npc_model.model = model
        npc_model.planSystem = planSystem
        npc_model.memorySystem = memorySystem
        npc_model.bio = bio
        npc_model.goal = goal
        npc_model.rotation = 0
        npc_model.asset = asset
        npc_model.save()
        
        map_model.add_uid(x, y, uid, nickname)
        map_model.save()
        
        buildings = buildings_model.get_names()
        # bound Actor to app
        self.app.actors[uid] = Actor(nickname, bio, goal, model, memorySystem, planSystem, buildings, cash, self.app.last_game_time)
        if uid in self.app.movings:
            self.app.movings.remove(uid)
        if uid in self.app.chatted:
            self.app.chatted.remove(uid)
        if uid in self.app.using:
            self.app.using.remove(uid)
        self.app.cache = [c for c in self.app.cache if c["uid"] != uid]
        self.app.inited.add(uid)

        # Return nonce and sign message.
        return {'uid': uid, 'homeBuilding': home_building_id, 'asset': npc_configs.assets.index(asset), "assetName": asset, 'model': model, 'memorySystem': memorySystem, 'planSystem': planSystem, 'workBuilding': work_building_id, 'nickname': nickname, 'bio': bio, 'goal': goal, 'cash': cash, "x": x, "y": y}
