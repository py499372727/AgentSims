from command.command_base import CommandBase

class GetNPCInfo(CommandBase):
    """get appointed NPC info."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', "NPCID", "promptType", "promptText"]):
            return False
        
        NPC_id, promptType, promptText = params['data']['NPCID'], params['data']['promptType'], params['data']['promptText']

        # npc_model = self.get_single_model("NPC", id=NPC_id, create=False)
        # if not npc_model:
        #     return self.error("NPC not found")
        uid = f"NPC-{NPC_id}"
        self.app.actors[uid].agent.cover_prompt(promptType, promptText)

        # Return nonce and sign message.
        return {'result': True}
