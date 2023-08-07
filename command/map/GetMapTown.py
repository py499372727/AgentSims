from command.command_base import CommandBase


class GetMapTown(CommandBase):
    """get town infomation."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False
        # uid = params['uid']
        # entity_model = self.get_single_model(self.type, create=False)
        # if not entity_model:
        #     return self.error("entity not found")
        # map_id = self.id
        # if self.type == "NPC":
        #     map_id = entity_model.map
        town_model = self.get_single_model("Town", create=False)
        if not town_model:
            return self.error("town not found")
        return {'town': town_model.as_object(False)}
