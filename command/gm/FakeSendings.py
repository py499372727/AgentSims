import random

from command.command_base import CommandBase

class FakeSendings(CommandBase):
    """get appointed NPC info."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', "testName"]):
            return False
        
        uid, test_name = params['uid'], params["data"]["testName"]

        if test_name == "movePath":
            NPC_id = 10001
            npc_model = self.get_single_model("NPC", NPC_id, create=False)
            map_model = self.get_single_model("Map", create=False)
            target_x = random.randint(68, 72)
            target_y = random.randint(38, 42)
            path = map_model.navigate(npc_model.x, npc_model.y,target_x, target_y)
            npc_model.x = target_x
            npc_model.y = target_y
            npc_model.save()
            self.app.send(uid, {"code": 200, "uri": "movePath", "uid": uid, "data": {"uid": npc_model.get_token(), "path": [{"x": x[0], "y": x[1]} for x in path]}})
        elif test_name == "changeRevenue":
            player_model = self.get_single_model("Player", create=False)
            amount = random.randint(100, 1000)
            is_increase = random.choice([True, False])
            player_model.change_revenue(amount, uid, is_increase)
            player_model.save()
            # self.app.send(uid, {"code": 200, "uri": "changeRevenue", "uid": uid, "data": {"uid": uid, "revenue": player_model.revenue + amount if is_increase else player_model.revenue, "amount": amount, "effect": "increase" if is_increase else "decrease"}})
        elif test_name == "changeCash":
            NPC_id = 10001
            npc_model = self.get_single_model("NPC", NPC_id, create=False)
            amount = random.randint(100, 1000)
            is_increase = random.choice([True, False])
            npc_model.change_cash(amount, uid, is_increase)
            npc_model.save()
            # self.app.send(uid, {"code": 200, "uri": "changeCash", "uid": "NPC-10001", "data": {"uid": "NPC-10001", "cash": npc_model.cash + amount if is_increase else npc_model.cash - amount, "amount": amount, "effect": "increase" if is_increase else "decrease"}})
        elif test_name == "increaseBuildingIncome":
            buildings_model = self.get_single_model("Buildings", create=False)
            amount = random.randint(100, 1000)
            buildings_model.increase_economic_income(1, amount, uid)
            buildings_model.save()
        else:
            return False

        # npc_model = self.get_single_model("NPC", id=NPC_id, create=False)
        # if not npc_model:
        #     return self.error("NPC not found")

        # Return nonce and sign message.
        return {'result': True}
