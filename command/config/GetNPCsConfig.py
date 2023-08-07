from command.command_base import CommandBase


class GetNPCsConfig(CommandBase):
    """get npc configs."""
    def is_check_token(self):
        return False

    def execute(self, params):
        return {"configs": self.app.npc_configs.to_json()}
