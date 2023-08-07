from command.command_base import CommandBase

class GetNPCs(CommandBase):
    """get all building infos."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False

        npcs_model = self.get_single_model("NPCs", create=False)
        if not npcs_model:
            return self.error("player's npcs not found")
        npcs = [self.get_single_model("NPC", id=x["id"], create=True).as_object(True) for x in npcs_model.npcs]

        # Return nonce and sign message.
        return {'npcs': npcs}
