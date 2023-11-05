from command.command_base import CommandBase
from typing import List, Dict, Any
import json
import asyncio

class Tick(CommandBase):
    """time tick."""
    def is_check_token(self):
        return False
    
    def next_time(self) -> bool:
        new_real_time = self.get_nowtime()
        new_game_time = self.app.last_game_time + (new_real_time - self.app.last_real_time) * 60
        next_day = False
        if self.app.get_formatter(new_game_time, "%Y-%m-%d") > self.app.get_formatter(self.app.last_game_time, "%Y-%m-%d"):
            next_day = True
        self.app.last_game_time = new_game_time
        self.app.last_real_time = new_real_time
        return next_day
    
    def get_entity_model(self, uid: str):
        entity_type = uid.partition("-")[0]
        entity_id = int(uid.partition("-")[2]) #TODO, why not use split ?
        entity_model = self.get_single_model(entity_type, entity_id, create=False)
        map_id = entity_id
        if entity_type == "NPC" and entity_model:
            map_id = entity_model.map
        map_model = self.get_single_model("Map", map_id, create=False)
        return entity_type, entity_id, entity_model, map_id, map_model
    
    async def move(self, entity_model, map_id, map_model, entity_type, uid) -> int:
        path = entity_model.path
        print("uid:", uid, "path:", path)
        # moves = 1
        # if entity_model.last_move:
        moves = len(path)
        print(moves)
        if moves:
            self.app.send(f"Player-{map_id}", {"code": 200, "uri": "movePath", "uid": uid, "data": {"uid": uid, "path": [{"x": x[0], "y": x[1]} for x in path[:moves]]}})
            for _ in range(moves):
                if path:
                    x, y = path[0]
                    if not map_model.map.get(str(x), dict()).get(str(y), dict()).get("block"):
                        if map_model.moveEntity(entity_model.x, entity_model.y, path[0][0], path[0][1], uid):
                            next_coord = path.pop(0)
                            # self.app.send(f"Player-{map_id}", {"code": 200, "uri": "moveTo", "uid": uid, "data": {"uid": uid, "fromX": entity_model.x, "fromY": entity_model.y, "toX": next_coord[0], "toY": next_coord[1]}})
                            map_model.save()
                            map_model.flush()
                            entity_model.x, entity_model.y = next_coord[0], next_coord[1]
                            entity_model.save()
                else:
                    break
            entity_model.last_move = self.app.last_game_time
            if path:
                entity_model.path = [[x[0], x[1]] for x in path]
                entity_model.save()
                entity_model.flush()
            self.app.movings.add(entity_model.get_token())
            # else:
            #     # arrival
            #     if entity_type == "NPC":
            #         sight = map_model.search_sight(entity_model.x, entity_model.y)
            #         info = {"source": "timetick-finishMoving", "data": {
            #             "people": sight["people"],
            #             "equipments": sight["equipments"],
            #             "cash": entity_model.cash,
            #             "game_time": self.app.last_game_time,
            #         }}
            #         result = await self.app.actors[uid].react(info)
            #         if result["status"] == 500:
            #             pass# self.app.cache.append({"uid": uid, "info": info})
            #         else:
            #             await self.parse_react(result, entity_model, map_id, map_model, uid)
            #     entity_model.path = list()
            #     entity_model.save()
            #     entity_model.flush()
            return 1
        else:
            sight = map_model.search_sight(entity_model.x, entity_model.y)
            info = {"source": "timetick-finishMoving", "data": {
                "people": sight["people"],
                "equipments": sight["equipments"],
                "cash": entity_model.cash,
                "game_time": self.app.last_game_time,
            }}
            result = await self.app.actors[uid].react(info)
            if result["status"] == 500:
                pass# self.app.cache.append({"uid": uid, "info": info})
            else:
                await self.parse_react(result, entity_model, map_id, map_model, uid)
            return 0
    
    async def _execute_chat(self, map_id, map_model, uid, entity_model, tuid, target_model, chats, topic=""):
        source_sight = map_model.search_sight(entity_model.x, entity_model.y)
        target = target_model.name
        cache = {
            "inited": tuid in self.app.inited,
            "using": tuid in self.app.using,
            "chatted": tuid in self.app.chatted,
            "caches": [c for c in self.app.cache if c["uid"] == tuid],
        }
        # stop target's movement
        if cache["inited"]:
            self.app.inited.remove(tuid)
        if cache["using"]:
            self.app.using.remove(tuid)
        if cache["chatted"]:
            self.app.chatted.remove(tuid)
        self.app.cache = [c for c in self.app.cache if c["uid"] != tuid]
        target_sight = map_model.search_sight(target_model.x, target_model.y)
        entity_model.add_event(entity_model.act)
        entity_model.set_action({"action": f"Talking to {target}", "time": self.app.last_game_time, "target": target, "targetID": tuid})
        while len(chats) < 10:
            not_reverse = len(chats) % 2 == 1
            source_model_loop = entity_model if not_reverse else target_model
            source_actor_id = uid if not_reverse else tuid
            target_model_loop = target_model if not_reverse else entity_model
            target_actor_id = tuid if not_reverse else uid
            info = {"source": "chatted", "data": {
                "people": source_sight["people"] if not_reverse else target_sight["people"],
                "equipments": source_sight["equipments"] if not_reverse else target_sight["equipments"],
                "cash": target_model_loop.cash,
                "person": source_model_loop.name,
                "topic": topic,
                "chat_cache": chats,
                "game_time": self.app.last_game_time,
            }}
            result = await self.app.actors[target_actor_id].react(info)
            try:
                content = result["data"]['chat']['content']
            except KeyError:
                if 'content' not in self.app.actors[target_actor_id].agent.state.chat:
                    __import__('remote_pdb').set_trace()
                content = self.app.actors[target_actor_id].agent.state.chat
            target_model_loop.add_chat(source_actor_id, content, False)
            source_model_loop.add_chat(target_actor_id, content)
            chats.append({"speaker": target_model_loop.name, "content": content})
        self.app.send(f"Player-{map_id}", {"code": 200, "uri": "chatWith", "uid": uid, "data": {"chats": [{"content": chat["content"].partition(": ")[2], "speaker": chat["speaker"], "speakerID": tuid if target == chat["speaker"] else uid} for chat in chats]}})
        # continue target's movement
        # stop target's movement
        if cache["inited"]:
            self.app.inited.add(tuid)
        if cache["using"]:
            self.app.using.add(tuid)
        if cache["chatted"]:
            self.app.chatted.add(tuid)
        for c in cache["caches"]:
            pass# self.app.cache.append(c)
        target_model.save()
        target_model.flush()
        entity_model.save()
        entity_model.flush()

    async def parse_react(self, result: Dict[str, Any], entity_model, map_id, map_model, uid):
        print("uid:", uid,"result:", json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        self.app.send(f"Player-{map_id}", {"code": 200, "uri": "NPC-React", "uid": uid, "data": {"uid": uid, "reaction": result}})
        if "newPlan" in result["data"]:
            try:
                entity_model.plan = result["data"]["newPlan"]["purpose"]
            except:
                __import__('remote_pdb').set_trace()
            self.app.send(f"Player-{map_id}", {"code": 200, "uri": "newPlan", "uid": uid, "data": {"uid": uid, "plan": result["data"]["newPlan"]["purpose"]}})
            entity_model.save()
            location = result['prompts']['plan']['building']
            buildings_model = self.get_single_model("Buildings", map_id, create=False)
            curLocation = map_model.map.get(str(entity_model.x), dict()).get(str(entity_model.y), dict()).get("building")
            if curLocation:
                curLocation = buildings_model.get_building(int(curLocation)).get('n', "")
            print("location:", location, "curLocation:", curLocation)
            if location != curLocation:
                # moving
                if buildings_model:
                    building = buildings_model.get_building_by_name(location)
                    if building:
                        # print("location:", location)
                        # print("curLocation:", curLocation)
                        # print("building:", building)
                        targetX, targetY = map_model.get_empty_tile(building['lx'], building['ty'], building['rx'], building['by'])
                        # if targetX != -1 and targetY != -1:
                        path = map_model.navigate(entity_model.x, entity_model.y, targetX, targetY)
                        if path:
                            entity_model.path = path[1:]
                            entity_model.last_move = self.app.last_game_time
                            entity_model.save()
                            entity_model.flush()
                            # # send info: target building id
                            self.app.send(f"Player-{map_id}", {"code": 200, "uri": "planToMove", "uid": uid, "data": {"uid": uid, "targetBuilding": location,"targetBuildingID": building["id"]}})
                            await self.move(entity_model, map_id, map_model, uid.partition("-")[0], uid)
                        # else:
                        #     # finish moving
                        #     entity_model.path = list()
                        #     entity_model.save()
                        #     entity_model.flush()
                    else:
                        # finish moving
                        entity_model.path = list()
                        entity_model.save()
                        entity_model.flush()
            self.app.movings.add(uid)
        elif "chat" in result["data"]:
            person = result['data']['person']
            tuid = map_model.name2uid.get(person)
            if tuid and tuid.partition("-")[0] == "NPC":
                target_type = tuid.partition("-")[0]
                target_id = int(tuid.partition("-")[2])
                target_model = self.get_single_model(target_type, id=target_id, create=False)
                if not target_model:
                    return 0
                chats = [{"speaker": entity_model.name, "content": result["data"]['chat']['content']}]
                topic = result['data']['topic']
                # self.app.send(f"Player-{map_id}", {"code": 200, "uri": "chatWith", "uid": uid, "data": {"sourceID": uid, "targetID": tuid, "content": result["data"]['chat']['content'].partition(": ")[2]}})
                await self._execute_chat(map_id, map_model, uid, entity_model, tuid, target_model, chats, topic)
            self.app.chatted.add(uid)
        elif "use" in result["data"]:
            equipment = result['data']['equipment']
            equipment_id = 0
            equipment_model = None
            equipments_model = self.get_single_model("Equipments", id=map_id, create=False)
            if equipments_model:
                equipment_id, equipment_model = equipments_model.get_equipment_by_name_and_position(equipment, entity_model.x, entity_model.y)
                if equipment_model:
                    lx, ty, rx, by = equipment_model["lx"], equipment_model["ty"], equipment_model["rx"], equipment_model["by"]
                    target_x, target_y = -1, -1
                    found = False
                    points = list()
                    for dx in range(lx, rx+1):
                        points.append([dx, ty-1])
                        points.append([dx, by+1])
                    for dy in range(ty, by+1):
                        points.append([lx-1, dy])
                        points.append([rx+1, dy])
                    for point in points:
                        if map_model.passable(point[0], point[1]):
                            target_x, target_y = point[0], point[1]
                            found = True
                    if found:
                        path = map_model.navigate(entity_model.x, entity_model.y, target_x, target_y)
                        if path:
                            entity_model.path = path[1:]
                            entity_model.last_move = self.app.last_game_time
                            entity_model.save()
                            entity_model.flush()
                            await self.move(entity_model, map_id, map_model, uid.partition("-")[0], uid)
            operation = result['data']['operation']
            continue_time = result['data']['use']['continue_time']
            cost = result['data']['use'].get("cost", 0)
            earn = result['data']['use'].get("earn", 0)
            if (cost or earn) and equipment_model:
                buildings_model = self.get_single_model("Buildings", map_id, create=False)
                if buildings_model:
                    buildings_model.increase_economic_income(equipment_model["b"], cost + earn, uid)
            entity_model.add_event(entity_model.act)
            entity_model.set_action({"action": f"{operation}", "time": self.app.last_game_time, "equipment": equipment_id, "continue_time": continue_time, "cost": cost, "earn": earn})
            # entity_model.plan = result['prompts']['plan']['purpose']
            entity_model.act_timeout = self.app.last_game_time + continue_time * 1000
            entity_model.save()
            if equipment_id:
                self.app.send(f"Player-{map_id}", {"code": 200, "uri": "interact", "uid": uid, "data": {"uid": uid, "equipment": equipment_id, "operation": operation, "continueTime": continue_time, "cost": cost, "earn": earn}})
            self.app.using.add(uid)

    async def finish_using(self, entity_model, map_id, map_model, uid) -> int:
        sight = map_model.search_sight(entity_model.x, entity_model.y)
        info = {"source": "timetick-finishUse", "data": {
            "people": sight["people"],
            "equipments": sight["equipments"],
            "cash": entity_model.cash,
            "game_time": self.app.last_game_time,
        }}
        result = await self.app.actors[uid].react(info)
        if result["status"] == 500:
            pass# self.app.cache.append({"uid": uid, "info": info})
        else:
            if result['data'] is None:
                __import__('remote_pdb').set_trace()
                result['date'] = self.app.actors[uid].agent.state.critic
            await self.parse_react(result, entity_model, map_id, map_model, uid)

        return 1

    async def solve_moving(self, moving):
        counter = 0
        entity_type, entity_id, entity_model, map_id, map_model = self.get_entity_model(moving)
        if not entity_model:
            return counter
        if self.app.last_game_time - entity_model.last_move <= 1000 * 60:
            self.app.movings.add(moving)
        if not map_model:
            return counter
        # if map_model.map.get(str(entity_model.x), dict()).get(str(entity_model.y), dict()).get("uid", "") != moving:
        #     # return self.error("position invalid")
        #     continue
        move_result = await self.move(entity_model, map_id, map_model, entity_type, moving)
        if move_result:
            counter = 1
        return counter
    
    async def solve_use(self, use):
        counter = 0
        entity_type, entity_id, entity_model, map_id, map_model = self.get_entity_model(use)
        if self.app.last_game_time - entity_model.act_timeout < 0:
            self.app.using.add(use)
        if not map_model:
            return counter
        use_result = await self.finish_using(entity_model, map_id, map_model, use)
        if use_result:
            counter += 1
        return counter
    
    async def solve_chat(self, chat):
        # finished chatting
        # chat is uid?
        counter = 0
        entity_type, entity_id, entity_model, map_id, map_model = self.get_entity_model(chat)
        if not entity_model:
            return counter
        if not map_model:
            return counter
        sight = map_model.search_sight(entity_model.x, entity_model.y)
        info = {"source": "timetick-finishChatting", "data": {
            "people": sight["people"],
            "equipments": sight["equipments"],
            "cash": entity_model.cash,
            "game_time": self.app.last_game_time,
        }}
        entity_model.new_chats = list()
        entity_model.save()
        entity_model.flush()
        result = await self.app.actors[chat].react(info)
        if result["status"] == 500:
            pass# self.app.cache.append({"uid": chat, "info": info})
        else:
            await self.parse_react(result, entity_model, map_id, map_model, chat)
            counter += 1
        return counter
    
    async def solve_init(self, init):
        counter = 0
        entity_type, entity_id, entity_model, map_id, map_model = self.get_entity_model(init)
        if not entity_model:
            return counter
        if not map_model:
            return counter
        sight = map_model.search_sight(entity_model.x, entity_model.y)
        info = {"source": "inited", "data": {
            "people": sight["people"],
            "equipments": sight["equipments"],
            "cash": entity_model.cash,
            "game_time": self.app.last_game_time,
        }}
        result = await self.app.actors[init].react(info)
        if result["status"] == 500:
            pass# self.app.cache.append({"uid": init, "info": info})
        else:
            await self.parse_react(result, entity_model, map_id, map_model, init)
            counter += 1
        return counter
    
    async def solve_cache(self, info):
        counter = 0
        entity_type, entity_id, entity_model, map_id, map_model = self.get_entity_model(info['uid'])
        if not map_model:
            return counter
        result = await self.app.actors[info['uid']].react(info['info'])
        if result["status"] == 500:
            pass# self.app.cache.append(info)
        else:
            await self.parse_react(result, entity_model, map_id, map_model, info['uid'])
            counter += 1
        return counter

    async def execute_eval(self):
        current_tick = self.app.tick_state["tick_count"]
        for eval_name, eval_module in self.app.evals.items():
            if  current_tick % eval_module.interval == 0:
                eval_res, response = await eval_module()
                eval_res = await eval_res
                response = await response
                print(f'{eval_name}: {eval_res}')
                with open('logs/eval_results.txt','a+') as f:
                    f.write(f'tick {current_tick}: {eval_name}: {eval_res}\n, response: {response} \n')
                    

    async def execute(self, params):
        # update timetick
        if self.app.tick_state["start"]:
            asyncio.create_task(self.execute_eval())
        if self.app.tick_state["tick_count"] >= self.app.config.tick_count_limit and self.app.tick_state["start"]:
            return self.error("tick counts over limit")
        next_day = self.next_time()

        counter = {'moving': 0, 'chatted': 0, 'using': 0, 'inited': 0, 'cache': 0}

        # using
        using = self.app.using
        print("before solving using:", using)
        uses = list()
        self.app.using = set()
        for use in using:
            use_task = asyncio.create_task(self.solve_use(use))
            uses.append(use_task)

        # chatted
        chatted = self.app.chatted # e.g.{'NPC-10001'}
        print("before solving chatted:", chatted)
        chats = list()
        self.app.chatted = set()
        for chat in chatted:
            chat_task = asyncio.create_task(self.solve_chat(chat))
            chats.append(chat_task)
        
        # if next_day:
        #     for uid, actor in self.app.actors:
        #         info = {"source": "timetick-storeMemory", "data": {
        #             "people": sight["people"],
        #             "equipments": sight["equipments"],
        #             "cash": entity_model.cash
        #         }}
        #         result = await actor.react(info)
        #         if result["status"] == 500:
        pass# #             self.app.cache.append({"uid": uid, "info": info})
        # move
        movings = self.app.movings
        moves = list()
        print("before solving movings:", movings)
        self.app.movings = set()
        for moving in movings:
            move_task = asyncio.create_task(self.solve_moving(moving))
            moves.append(move_task)
        
        # inited
        inited = self.app.inited
        print("before solving inited:", inited)
        inits = list()
        self.app.inited = set()
        for init in inited:
            init_task = asyncio.create_task(self.solve_init(init))
            inits.append(init_task)

        infos = self.app.cache # to solve agent occupied problem
        print("before solving cache:", infos)
        caches = list()
        self.app.cache = list()
        for info in infos:
            cache_task = asyncio.create_task(self.solve_cache(info))
            caches.append(cache_task)

        for move in moves:
            counter["moving"] += await move
        for chat in chats:
            counter["chatted"] += await chat
        for use in uses:
            counter["using"] += await use
        for init in inits:
            counter["inited"] += await init
        for cache in caches:
            counter["cache"] += await cache
        
        if counter["moving"] or counter["chatted"] or counter["using"] or counter["inited"] or counter["cache"]:
            self.app.tick_state["tick_count"] += 1

        print("movings:", self.app.movings)
        print("cache:", self.app.cache)
        print("inited:", self.app.inited)
        print("using:", self.app.using)
        print("chatted:", self.app.chatted)

        return counter
