import json
import os

abs_path = os.path.dirname(os.path.realpath(__file__))

def extract_area_objects(json_data):
    area_objects = []
    for layer in json_data['layers']:
        if layer['type'] == 'objectgroup':
            for obj in layer['objects']:
                if 'type' in obj and (obj["type"] == "Area" or obj["type"] == "area"):
                    area_objects.append(obj)
                            
    return area_objects

def merge_polygon_to_rectangle(area_objects, tile_width, tile_height):
    rectangles = []
    for obj in area_objects:
        if 'polygon' in obj:
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')

            for point in obj['polygon']:
                min_x = min(min_x, point['x'])
                min_y = min(min_y, point['y'])
                max_x = max(max_x, point['x'])
                max_y = max(max_y, point['y'])

            rectangles.append({
                'name': obj['name'],
                'x': round((obj['x'] + min_x) / tile_width),
                'y': round((obj['y'] + min_y) / tile_height),
                'width': round((max_x - min_x) / tile_width),
                'height': round((max_y - min_y) / tile_height)
            })
        else:
            rectangles.append({
                'name': obj['name'],
                'x': round(obj['x']/tile_width),
                'y':  round(obj['y']/tile_height),
                'width': round(obj['width']/tile_width),
                'height': round(obj['height']/tile_height)
            })
    return rectangles

def set_block(bitmap, x1, y1, x2, y2):
    for i in range(y1, y2 + 1):
        for j in range(x1, x2 + 1):
            bitmap[i][j] = 1

def is_block(obj):
    if 'properties' in obj:
        for prop in obj['properties']:
            if (prop['name'] == "Block" or prop['name'] == "block") and prop['type'] == "bool" and prop['value'] is True:
                return True
    return False

def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def set_polygon_blocks(bitmap, obj, tile_width, tile_height):
    poly = [(obj['x'] + point['x'], obj['y'] + point['y']) for point in obj['polygon']]

    min_x, min_y = round(min(x for x, _ in poly) // tile_width), round(min(y for _, y in poly) // tile_height)
    max_x, max_y = round(max(x for x, _ in poly) // tile_width), round(max(y for _, y in poly) // tile_height)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if point_inside_polygon(x * tile_width + tile_width/2, y * tile_height + tile_height/2, poly):
                bitmap[y][x] = 1

def is_interactive(obj):
    if 'properties' in obj:
        for prop in obj['properties']:
            if (prop['name'] == "Interactive" or prop['name'] == "interactive") and prop['type'] == "bool" and prop['value'] is True:
                return True
    return False

def extract_interactive_objects(tmj_data):
    interactive_objects = []
    for layer in tmj_data['layers']:
        if layer['type'] == 'objectgroup':
            for obj in layer['objects']:
                if ('type' in obj and (obj["type"] == "Object" or obj["type"] == "object")) or is_interactive(obj):
                    interactive_objects.append(obj)
                        

    return interactive_objects

def calculate_width_height(polygon):
    min_x = min([coord['x'] for coord in polygon])
    max_x = max([coord['x'] for coord in polygon])
    min_y = min([coord['y'] for coord in polygon])
    max_y = max([coord['y'] for coord in polygon])

    return max_x - min_x, max_y - min_y


params = {
    "type": str,
    "width": int,
    "height": int,
    "assets": str,
    "blocks": list,
    "equipments": list,
    "price": 0
}

# { name: {} }
equipmentMap = dict()

def generate_list(tmj_data):
    map_width = tmj_data['width']
    map_height = tmj_data['height']
    tile_width = tmj_data['tilewidth']
    tile_height = tmj_data['tileheight']
    blocks = [[0 for _ in range(map_width)] for _ in range(map_height)]
    equipments = [[0 for _ in range(map_width)] for _ in range(map_height)]
    width, height = map_width, map_height
    for layer in tmj_data['layers']:
        if layer['type'] == "objectgroup":
            for obj in layer['objects']:
                if is_block(obj):
                    x, y = obj['x'] // tile_width, obj['y'] // tile_height
                    if 'polygon' not in obj:
                        w, h = obj['width'] // tile_width, obj['height'] // tile_height
                        set_block(blocks, x, y, x + w - 1, y + h - 1)
                    else:
                        set_polygon_blocks(blocks, obj, tile_width, tile_height)
                if ('type' in obj and (obj["type"] == "Object" or obj["type"] == "object")) or is_interactive(obj):
                    # interactive_objects.append(obj)
                    x, y = obj['x'] // tile_width, obj['y'] // tile_height
                    if 'polygon' not in obj:
                        w, h = int(obj['width'] // tile_width), int(obj['height'] // tile_height)
                    else:
                        w, h = calculate_width_height(obj['polygon'])
                        w, h = w // tile_width, h // tile_height
                    if equipmentMap.get(f"{obj['name']}-{w}-{h}"):
                        equipment = equipmentMap[f"{obj['name']}-{w}-{h}"]
                    else:
                        equipment = {
                            "id": len(equipmentMap) + 1,
                            "type": obj['name'],
                            "width": 1,
                            "height": 1,
                            "assets": f"{obj['name']}-{w}-{h}",
                            "description": "",
                            "functions": [],
                            "hireCapacity": 0,
                            "livingCapacity": 0
                        }
                        if 'polygon' not in obj:
                            equipment["width"] = w
                            equipment["height"] = h
                        else:
                            equipment["width"] = int(w)
                            equipment["height"] = int(h)
                        equipmentMap[f"{obj['name']}-{w}-{h}"] = equipment
                    # print(y, x)
                    equipments[int(y)][int(x)] = equipment["id"]
    return width, height, blocks, equipments

def set_framework(area, blocks, equipments):
    building_infos = list()
    equipment_infos = list()
    map_info = dict()
    for bid, building in enumerate(area):
        bid += 1
        leftX, topY, rightX, bottomY, width, height = building["x"], building["y"], building["x"] + building["width"] - 1, building["y"] + building["height"] - 1, building["width"], building["height"]
        subBlocks = [[0 for w in range(width)] for h in range(height)]
        subEquipments = [[0 for w in range(width)] for h in range(height)]
        for iy, y in enumerate(range(topY, bottomY+1)):
            for ix, x in enumerate(range(leftX, rightX+1)):
                if x not in map_info:
                    map_info[x] = dict()
                if y not in map_info[x]:
                    map_info[x][y] = dict()
                map_info[x][y]["building"] = bid
                block = blocks[y][x]
                if block > 0:
                    subBlocks[iy][ix] = block
                    map_info[x][y]["block"] = 1
                equipment = equipments[y][x]
                if equipment > 0:
                    subEquipments[iy][ix] = equipment
                    equipment_info = dict()
                    equipment_config = dict()
                    for equipment_config in equipmentMap.values():
                        if equipment_config["id"] == equipment:
                            break
                    # no o(owner) & fs(functions)
                    eid = len(equipment_infos) + 1
                    equipment_info["id"] = eid
                    equipment_info["n"] = equipment_config["type"]
                    equipment_info["t"] = equipment
                    equipment_info["lx"] = x
                    equipment_info["ty"] = y
                    equipment_info["rx"] = x + equipment_config["width"] - 1
                    equipment_info["by"] = y + equipment_config["height"] - 1
                    equipment_info["r"] = 0
                    equipment_info["b"] = bid
                    equipment_infos.append(equipment_info)
                    for ey in range(y, y+equipment_config["height"]):
                        for ex in range(x, x+equipment_config["width"]):
                            if ex not in map_info:
                                map_info[ex] = dict()
                            if ey not in map_info[ex]:
                                map_info[ex][ey] = dict()
                            map_info[ex][ey]["equipment"] = eid
        if building["name"] not in appearenced_building:
            appearenced_building.add(building['name'])
            buildings.append({
                "id": len(buildings) + 1,
                "price": 0,
                "assets": building["name"],
                "type": building["name"],
                "width": width,
                "height": height,
                "blocks": subBlocks,
                "equipments": subEquipments,
            })
        building_info = dict()
        # no o(owner) e(economic) h(hire) l(living) r(rent)
        building_info["id"] = bid
        building_info["n"] = building["name"]
        building_info["t"] = building["name"]
        building_info["lx"] = leftX
        building_info["ty"] = topY
        building_info["rx"] = rightX
        building_info["by"] = bottomY
        building_info["r"] = 0
        building_infos.append(building_info)
    framework["map"] = map_info
    framework["buildings"] = building_infos
    framework["equipments"] = equipment_infos

dir_path = os.path.join(abs_path, "tiled")

buildings = list()
appearenced_building = set()
framework = dict()
for name in os.listdir(dir_path):
    if name.endswith(".tmj"):
        assets = name.rpartition(".")[0]
        typeName = name.rpartition(".")[0].partition("_")[0]
        building = dict()
        building["assets"] = assets
        building["type"] = typeName
        with open(os.path.join(dir_path, name), "r", encoding="utf-8") as tile_file:
            json_data = json.loads(tile_file.read())
            tile_width = json_data['tilewidth']
            tile_height = json_data['tileheight']
            width, height, blocks, equipments = generate_list(json_data)
            building["width"] = width
            building["height"] = height
            building["blocks"] = blocks
            building["equipments"] = equipments
            if name.startswith("framework"):
                area_objects = extract_area_objects(json_data)
                set_framework(merge_polygon_to_rectangle(area_objects, tile_width, tile_height), building["blocks"], building["equipments"])
            elif building['type'] not in appearenced_building:
                appearenced_building.add(building['type'])
                building["id"] = len(buildings) + 1
                building["price"] = 0
                buildings.append(building)
print(buildings)
print(equipmentMap)
print(framework)

output_path = os.path.join(abs_path, "output")
with open(os.path.join(output_path, "buildings.json"), "w", encoding="utf-8") as building_output:
    building_output.write(json.dumps(buildings, ensure_ascii=False))
with open(os.path.join(output_path, "equipments.json"), "w", encoding="utf-8") as equipment_output:
    equipment_output.write(json.dumps([x for x in equipmentMap.values()], ensure_ascii=False))
with open(os.path.join(output_path, "framework.json"), "w", encoding="utf-8") as framework_output:
    framework_output.write(json.dumps(framework, ensure_ascii=False))
