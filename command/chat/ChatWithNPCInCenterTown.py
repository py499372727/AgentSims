from command.command_base import CommandBase
import asyncio
import random


class ChatWithNPCInCenterTown(CommandBase):
    """chat with NPC in  center town"""

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

        # 如果对话中包换中央小镇的相关信息 todo center town info 参数是否要考虑在内
        cenTerAgentName = self.checkCenterTownAgentName(result)
        if "center town" in result or cenTerAgentName:
            if not cenTerAgentName:
                cenTerAgentName = self.getCenterTownAgentNamnRangdom()
            self.app.send(player_id, {"code": 200, "uri": "chatWith", "uid": NPC_id,
                                      "data": {"sourceID": NPC_id,
                                               "targetID": player_id,
                                               "content": response.partition(": ")[2],
                                               "goToCenterTown": True,
                                               "cenTerAgentName": cenTerAgentName
                                               # todo center town 是否要把人物的坐标输入在内？
                                               }})
        else:
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

    # 检查结果里是否包含小镇里的人物
    def checkCenterTownAgentName(self, result):
        # todo center town 8个agent的人名
        centralTown = list()
        for agentName in centralTown:
            if agentName in result:
                return agentName
        return None

    # 随机获取中央小镇里的一个人物
    def getCenterTownAgentNamnRangdom(self):
        # todo center town 8个agent的人名
        centralTown = list()
        return random.choice(centralTown)