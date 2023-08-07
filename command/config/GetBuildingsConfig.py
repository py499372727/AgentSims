from command.command_base import CommandBase


class GetBuildingsConfig(CommandBase):
    """get building configs."""
    def is_check_token(self):
        return False

    def execute(self, params):
        return {"configs": sorted([v.to_json() for v in self.app.building_configs.values()], key=lambda x: x["id"], reverse=False)}
