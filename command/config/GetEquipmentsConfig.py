from command.command_base import CommandBase


class GetEquipmentsConfig(CommandBase):
    """get equipment configs."""
    def is_check_token(self):
        return False

    def execute(self, params):
        return {"configs": sorted([v.to_json() for v in self.app.equipment_configs.values()], key=lambda x: x["id"], reverse=False)}
