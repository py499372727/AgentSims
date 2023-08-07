from command.command_base import CommandBase

class GetNPCInfo(CommandBase):
    """get appointed NPC info."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', "NPCID"]):
            return False
        
        NPC_id = params['data']['NPCID']

        npc_model = self.get_single_model("NPC", id=NPC_id, create=False)
        if not npc_model:
            return self.error("NPC not found")

        # Return nonce and sign message.
        return {'npc': npc_model.as_object(False)}
