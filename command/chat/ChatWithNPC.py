from command.command_base import CommandBase
import asyncio


class ChatWithNPC(CommandBase):
    """chat with NPC."""

    async def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', "NPCID", "content"]):
            return False

        player_id, NPC_id, content = params['uid'], params['data']['NPCID'], params['data']['content']

        npc_model = self.get_single_model("NPC", id=int(NPC_id.partition("-")[2]), create=False)
        if not npc_model:
            return self.error("NPC not found")
        npc_model.add_chat(player_id, content, False)
        player_model = self.get_single_model("Player", create=False)
        if not player_model:
            return self.error("Player not found")
        player_model.add_chat(NPC_id, content)
        self.app.send(player_id, {"code": 200, "uri": "chatWith", "uid": player_id,
                                  "data": {"sourceID": player_id, "targetID": NPC_id, "content": content}})
        last_chats = [{"speaker": player_model.name if x["isSender"] else npc_model.name, "content": x["content"]} for x
                      in player_model.chats.get(NPC_id, list())[::-1]]
        last_chats.append({"speaker": player_model.name, "content": content})

        map_model = self.get_single_model("Map", create=False)
        if not map_model:
            return self.error("map not found")
        sight = map_model.search_sight(npc_model.x, npc_model.y)
        info = {"source": "chatted", "data": {
            "people": sight["people"],
            "equipments": sight["equipments"],
            "cash": npc_model.cash,
            "person": player_model.name,
            "topic": "",
            "chat_cache": last_chats,
            "game_time": self.app.last_game_time,
        }}
        result = await self.app.actors[NPC_id].react(info)
        response = result["data"]['chat']['content']
        player_model.add_chat(NPC_id, response, False)
        npc_model.add_chat(player_id, response)
        self.app.send(player_id, {"code": 200, "uri": "chatWith", "uid": NPC_id,
                                  "data": {"sourceID": NPC_id, "targetID": player_id,
                                           "content": response.partition(": ")[2]}})
        # self.app.chatted.add(NPC_id)
        # if NPC_id in self.app.inited:
        #     self.app.inited.remove(NPC_id)
        # if NPC_id in self.app.movings:
        #     self.app.movings.remove(NPC_id)
        # if NPC_id in self.app.using:
        #     self.app.using.remove(NPC_id)
        # if NPC_id in self.app.cache:
        #     self.app.cache.remove(NPC_id)
        npc_model.save()
        player_model.save()

        # Return nonce and sign message.
        return {'npc': npc_model.as_object(False), 'player': player_model.as_object(False)}