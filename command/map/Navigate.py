from command.command_base import CommandBase


class Navigate(CommandBase):
    """navigate on player's scene map."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', 'x', 'y']):
            return False
        uid, x, y = params['uid'], params['data']['x'], params['data']['y']
        entity_model = self.get_single_model(self.type, create=False)
        if not entity_model:
            return self.error("entity not found")
        map_id = self.id
        if self.type == "NPC":
            map_id = entity_model.map
        map_model = self.get_single_model("Map", map_id, create=False)
        if not map_model:
            return self.error("map not found")
        # if map_model.map.get(str(entity_model.x), dict()).get(str(entity_model.y), dict()).get("uid", "") != uid:
        #     return self.error("position invalid")
        if map_model.map.get(str(x), dict()).get(str(y), dict()).get("block"):
            return self.error("target invalid")
        # TODO: search for a new space
        path = map_model.navigate(entity_model.x, entity_model.y, x, y)
        # print(path)
        if path:
            # remove start
            if path[0] == (entity_model.x, entity_model.y):
                path.pop(0)
            if path and map_model.moveEntity(entity_model.x, entity_model.y, path[0][0], path[0][1], uid):
                next_coord = path.pop(0)
                self.app.send(f"Player-{map_id}", {"code": 200, "uri": "moveTo", "uid": uid, "data": {"uid": uid, "fromX": entity_model.x, "fromY": entity_model.y, "toX": next_coord[0], "toY": next_coord[1]}})
                map_model.save()
                entity_model.x, entity_model.y = next_coord[0], next_coord[1]
                entity_model.save()
            if path:
                entity_model.path = [[x[0], x[1]] for x in path]
                entity_model.save()
                self.app.movings.add(entity_model.get_token())
            else:
                entity_model.path = list()
                entity_model.save()
        return {'nowPositionX': entity_model.x, 'nowPositionY': entity_model.y, "remainPath": entity_model.path}
