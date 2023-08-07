from command.command_base import CommandBase


class GetMapScene(CommandBase):
    """get map infomation."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False
        uid = params['uid']
        entity_model = self.get_single_model(self.type, create=False)
        if not entity_model:
            return self.error("entity not found")
        map_id = self.id
        if self.type == "NPC":
            map_id = entity_model.map
        map_model = self.get_single_model("Map", map_id, create=False)
        if not map_model:
            return self.error("map not found")
        return {'map': map_model.as_object(False)}
