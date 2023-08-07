from command.command_base import CommandBase

class GetBuildingInfo(CommandBase):
    """get appointed building info."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', "buildingID"]):
            return False
        
        building_id = params['data']['buildingID']

        buildings_model = self.get_single_model("Buildings", create=False)
        if not buildings_model:
            return self.error("player's buildings not found")

        # Return nonce and sign message.
        return {'building': buildings_model.get_building(building_id)}
