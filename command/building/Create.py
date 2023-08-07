from command.command_base import CommandBase

class Create(CommandBase):
    """Player create building."""
    
    def block_xy_to_tile_xy(self, bx, by):
        # {by: {bx: {tx, ty}}}
        mapping = {
            1: {
                1: (10, 5),
                2: (45, 5),
                3: (79, 5),
                4: (115, 5),
            },
            2: {
                1: (10, 24),
                2: (45, 24),
                3: (79, 24),
                4: (115, 24),
            },
            3: {
                1: (10, 44),
                2: (45, 44),
                3: (79, 44),
                4: (115, 44),
            },
            4: {
                1: (10, 64),
                2: (45, 64),
                3: (79, 64),
                4: (115, 64),
            },
        }
        if by not in mapping or bx not in mapping[by]:
            return 0, 0
        tx, ty = mapping[by][bx]
        return tx, ty
    
    def flush_str(self, string):
        if isinstance(string, str):
            string = string.strip().strip("\u200B")
        return string

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid', 'building_type', 'name', 'x', 'y', 'rotation']):
            return False

        player_uid, building_type, name, bx, by, rotation = params['uid'], params['data']['building_type'], params['data']['name'], params['data']['x'], params['data']['y'], params['data']['rotation']
        name = self.flush_str(name)
        bx, by = int(bx), int(by)

        # if not name:
        #     return self.error("name is blank")
        
        x, y = self.block_xy_to_tile_xy(bx, by)
        if x == 0 and y == 0:
            return self.error("cannot parse x & y")

        # check valid
        building_config = self.app.get_building_config(building_type)
        width = building_config.width
        height = building_config.height
        dx, dy = 1, 1
        if rotation == 90:
            dy = -1
        elif rotation == 180:
            dx, dy = -1, -1
        elif rotation == 270:
            dx = -1
        
        leftX, topY = min(x, x+dx*width), min(y, y+dy*height)
        rightX, bottomY = max(x, x+dx*width), max(y, y+dy*height)
        
        map_model = self.get_single_model("Map", create=False)
        if not map_model:
            return self.error("map not found")
        if map_model.hasEntityInRange(leftX, topY, rightX, bottomY):
            return self.error("block already used")
        buildings_model = self.get_single_model("Buildings", create=False)
        if not buildings_model:
            return self.error("player's buildings not found")
        if not buildings_model.is_empty(bx, by):
            return self.error("block already used")
        equipments_model = self.get_single_model("Equipments", create=False)
        if not equipments_model:
            return self.error("player's equipments not found")
        player_model = self.get_single_model("Player", create=False)
        if not player_model:
            return self.error("player info not found")
        if not player_model.change_revenue(building_config.price, player_uid, False):
            return self.error("lack of revenue to invite")
        player_model.save()
        hireCapacity = 0
        livingCapacity = 0
        names = buildings_model.get_names()
        if not name:
            name = building_config.type
        if name in names:
            for i in range(1, 50):
                if f"{name}-{i}" not in names:
                    name = f"{name}-{i}"
                    break

        for ry in range(height):
            for rx in range(width):
                equipment_type = building_config.equipments[ry][rx]
                if equipment_type:
                    equipment_config = self.app.get_equipment_config(equipment_type)
                    hireCapacity += equipment_config.hireCapacity
                    livingCapacity += equipment_config.livingCapacity

        building_id = buildings_model.add_building(name, player_uid, building_type, leftX, topY, rightX, bottomY, rotation, hireCapacity, livingCapacity)
        buildings_model.save()
        buildings_model.flush()

        map_model.setValues(leftX, topY, rightX, bottomY, "building", building_id)
        for ry in range(height):
            for rx in range(width):
                block = building_config.blocks[ry][rx]
                if block:
                    map_model.setValue(x+dx*rx, y+dy*ry, "block", 1)
                equipment_type = building_config.equipments[ry][rx]
                if equipment_type:
                    equipment_config = self.app.get_equipment_config(equipment_type)
                    equipment_width = equipment_config.width
                    equipment_height = equipment_config.height
                    eleftX, etopY = min(x, x+dx*equipment_width), min(y, y+dy*equipment_height)
                    erightX, ebottomY = max(x, x+dx*equipment_width), max(y, y+dy*equipment_height)
                    equipment_id = equipments_model.add_equipment(f'{equipment_config.type} in {name}', player_uid, equipment_type, eleftX, etopY, erightX, ebottomY, rotation, building_id, equipment_config.functions)
                    map_model.setValues(eleftX, etopY, erightX, ebottomY, "equipment", equipment_id)

        map_model.save()
        equipments_model.save()

        npcs_model = self.get_single_model("NPCs", create=False)
        if not npcs_model:
            return self.error("map's npcs not found")
        npcs = npcs_model.get_uids()
        for npc_id in npcs:
            uid = f"NPC-{npc_id}"
            self.app.actors[uid].agent.state.buildings.append(name)

        # Return nonce and sign message.
        return {'building_id': building_id, "x": bx, "y": by, "building_type": building_type, "name": name}
