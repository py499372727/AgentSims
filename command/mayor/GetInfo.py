from command.command_base import CommandBase


class GetInfo(CommandBase):
    """get infos for mayor agent."""

    def execute(self, params):
        # Check params.
        ret_data = {
            "last_game_time": self.app.last_game_time,
            "start_time": self.app.start_time,
            "revenue": self.get_single_model("Player").revenue,
            "buildings": [],
            "npcs": list(),
            "building_types": [config.to_json() for config in self.app.building_configs.values()],
        }

        npcs_model = self.get_single_model("NPCs")
        for npc in npcs_model.npcs:
            n_id = npc["id"]
            npc_model = self.get_single_model("NPC", id=n_id, create=False)
            if not npc_model:
                continue
            ret_data["npcs"].append(
                {"id": npc_model.get_token(), "name": npc_model.name, "bio": npc_model.bio, "goal": npc_model.goal,
                 "cash": npc_model.cash})

        buildings_model = self.get_single_model("Buildings", create=False)
        if buildings_model:
            for building in buildings_model.buildings:
                print("mayor check building:",
                      {"name": building["n"], "x": building["x"], "y": building["y"], "income": building["eI"],
                       "beds": building["lC"], "livings": building["lL"], "id": building["id"]})
                ret_data["buildings"].append(
                    {"name": building["n"], "x": building["x"], "y": building["y"], "income": building["eI"],
                     "beds": building["lC"], "livings": building["lL"], "id": building["id"]})

        return ret_data