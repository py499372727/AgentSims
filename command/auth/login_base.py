from command.command_base import CommandBase
from agent.actor import Actor


class LoginBase(CommandBase):

    def reg_npc(self, uid, nickname, x, y, asset, bio, goal):
        account_model = self.get_model('NPCRegister')
        # print(f'!!! when register npc uid: {uid}-{nickname}')
        # print(f'!!! when register database: {account_model.get_db()}')
        id = account_model.find_id(f'{uid}-{nickname}')
        if id <= 0:
            id = account_model.reg_npc(f'{uid}-{nickname}')
            if id <= 0:
                return self.error('register npc failed')
        npc_uid = self.gen_token("NPC", id)
        npc_model = self.get_single_model("NPC", id=id, create=True)
        npc_model.name = nickname
        npc_model.map = self.id
        # TODO: If agent use websocket connect with server
        # Then don't set server and use this field to search npcs not linked
        npc_model.server = npc_uid
        npc_model.cash = 10000
        npc_model.x = x
        npc_model.y = y
        npc_model.rotation = 0
        npc_model.asset = asset
        npc_model.save()
        
        # buildings_model = self.get_single_model("Buildings", create=False)
        buildings = ["dessert shop", "gym", "houseZ", "park"]
        model = "gpt-3.5"
        memorySystem = "LongShortTermMemories"
        planSystem = "QAFramework"
        npc_model.model = model
        npc_model.memorySystem = memorySystem
        npc_model.planSystem = planSystem
        npc_model.bio = bio
        npc_model.goal = goal
        npc_model.home_building = 3
        npc_model.work_building = 0
        # if buildings_model:
        #     buildings = buildings_model.get_names()
        self.app.actors[npc_uid] = Actor(nickname, bio, goal, model, memorySystem, planSystem, buildings, 10000, self.app.last_game_time)
        self.app.inited.add(npc_uid)
        return id, npc_model

    def reg_eval(self, uid):
        for eval_des, eval_cfg in self.app.eval_configs.items():
            eval_model = self.get_single_model('Eval', id=uid, create=True, eval_cfg=eval_cfg)
            self.app.evals[eval_des] = eval_model
        return eval_model


    # Common login logic.
    def handle_login(self, nickname, uid):
        buildings_info = []
        npcs_info = []
        player_model = self.get_single_model('Player', create=False)
        npc_configs = self.app.get_npc_config()
        # First time login, create all data to avoid creating them in scene server.
        # Otherwise, to update login time.
        if player_model is None:
            print(uid, "first login")
            alan, alan_model = self.reg_npc(uid, "Alan", 50, 71, "premade_01", "Alan is a genius with outstanding talents and is the inventor of computer. Alan has an introverted personality and is only interested in the research he foucues on.", "Promoting the Process of Computer Research")
            fei, fei_model = self.reg_npc(uid, "pH", 52, 73, "premade_04", "pH is a positive, cheerful, optimistic but somewhat crazy girl who dares to try and explore. She loves food, loves life, and hopes to bring happiness to everyone.", "Taste all the delicious food and become a gourmet or chef.")
            models = [
                'Player',
                'Map',
                'Town',
                'Buildings',
                'Equipments',
                'NPCs',
            ]
            for model_name in models:
                model = self.get_single_model(model_name)
                # if model_name == "NPCs":
                    # last_npcs = model.npcs
                    # for nid in last_npcs:
                    #     nuid = self.gen_token("NPC", nid)
                    #     if nuid in self.app.movings:
                    #         self.app.movings.remove(nuid)
                    #     if nuid in self.app.chatted:
                    #         self.app.chatted.remove(nuid)
                    #     if nuid in self.app.using:
                    #         self.app.using.remove(nuid)
                    #     if nuid in self.app.inited:
                    #         self.app.inited.remove(nuid)
                    #     self.app.cache = [c for c in self.app.cache if c["uid"] != nuid]
                    #     if nuid in self.app.actors:
                    #         del self.app.actors[nuid]
                model.init()
                if model_name == "Player":
                    model.name = nickname
                    model.x = 71
                    model.y = 41
                if model_name == "Map":
                    model.init_map()
                    model.add_uid(71, 41, uid, nickname)
                    model.add_uid(50, 71, f"NPC-{alan}", "Alan")
                    model.add_uid(52, 73, f"NPC-{fei}", "Fei")
                if model_name == "Buildings":
                    model.init_buildings()
                    for building in model.buildings:
                        if building["lC"] > 0:
                            model.add_tenent(building["id"], alan)
                            model.add_tenent(building["id"], fei)
                        buildings_info.append({"building_id": building["id"], "building_type": building["t"], "name": building["n"], "x": building["x"], "y": building["y"]})
                if model_name == "Equipments":
                    model.init_equipments()
                if model_name == "NPCs":
                    model.npcs = [{"id": alan, "name": "Alan"}, {"id": fei, "name": "Fei"}]
                    # for npc in model.npcs:
                    #     npc_model = self.get_single_model("NPC", npc["id"], create=False)
                    #     if not npc_model:
                    #         continue
                    #     home_building = self.get_single_model("Buildings", create=True).get_building(npc_model.home_building)
                    #     if not home_building:
                    #         continue
                    npcs_info.append({"uid": f"NPC-{alan}", "homeBuilding": alan_model.home_building, 'asset': npc_configs.assets.index(alan_model.asset), "assetName": alan_model.asset, 'model': alan_model.model, 'memorySystem': alan_model.memorySystem, 'planSystem': alan_model.planSystem, 'workBuilding': alan_model.work_building, 'nickname': alan_model.name, 'bio': alan_model.bio, 'goal': alan_model.goal, 'cash': alan_model.cash, "x": alan_model.x, "y": alan_model.y})
                    npcs_info.append({"uid": f"NPC-{fei}", "homeBuilding": fei_model.home_building, 'asset': npc_configs.assets.index(fei_model.asset), "assetName": fei_model.asset, 'model': fei_model.model, 'memorySystem': fei_model.memorySystem, 'planSystem': fei_model.planSystem, 'workBuilding': fei_model.work_building, 'nickname': fei_model.name, 'bio': fei_model.bio, 'goal': fei_model.goal, 'cash': fei_model.cash, "x": fei_model.x, "y": fei_model.y})
                model.save()
        else:
            print(uid, "login")
            player_model.login_time = self.get_nowtime()
            player_model.save()
            
            buildings_model = self.get_single_model("Buildings", create=False)
            if buildings_model:
                for building in buildings_model.buildings:
                    buildings_info.append({"building_id": building["id"], "building_type": building["t"], "name": building["n"], "x": building["x"], "y": building["y"]})
                    
            npcs_model = self.get_single_model("NPCs", create=False)
            if npcs_model:
                for npc in npcs_model.npcs:
                    npc_model = self.get_single_model("NPC", npc["id"], create=False)
                    if not npc_model:
                        continue
                    npcs_info.append({"uid": f'NPC-{npc["id"]}', "homeBuilding": npc_model.home_building, 'asset': npc_configs.assets.index(npc_model.asset), "assetName": npc_model.asset, 'model': npc_model.model, 'memorySystem': npc_model.memorySystem, 'planSystem': npc_model.planSystem, 'workBuilding': npc_model.work_building, 'nickname': npc_model.name, 'bio': npc_model.bio, 'goal': npc_model.goal, 'cash': npc_model.cash, "x": npc_model.x, "y": npc_model.y})

        self.reg_eval(uid)
        return buildings_info, npcs_info

    def is_check_token(self):
        return False
