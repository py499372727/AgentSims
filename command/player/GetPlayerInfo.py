from command.command_base import CommandBase

class GetPlayerInfo(CommandBase):
    """get appointed Player info."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False

        player_model = self.get_single_model("Player", create=False)
        if not player_model:
            return self.error("Player not found")

        return {'player': player_model.as_object(False)}
