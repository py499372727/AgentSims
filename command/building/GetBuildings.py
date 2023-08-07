from command.command_base import CommandBase

class GetBuildings(CommandBase):
    """get all building infos."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False

        buildings_model = self.get_single_model("Buildings", create=False)
        if not buildings_model:
            return self.error("player's buildings not found")

        # Return nonce and sign message.
        return {'buildings': buildings_model.buildings}
