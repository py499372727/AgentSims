import time
import json
import asyncio
import websockets

commands = {
    "command.auth.Register": {"nickname": str, "email": str, "cryptoPWD": str},
    "command.building.Create": {"building_type": int, "name": str, "x": int, "y": int, "rotation": int},
    "command.building.GetBuildingInfo": {"buildingID": int},
    "command.building.GetBuildings": {},
    "command.chat.ChatToNPC": {"NPCID": int, "content": str},
    "command.config.GetBuildingsConfig": {},
    "command.config.GetEquipmentsConfig": {},
    "command.config.GetNPCsConfig": {},
    "command.map.GetMapScene": {},
    "command.map.GetMapTown": {},
    "command.map.Navigate": {"x": int, "y": int},
    "command.npc.Create": {"asset": str, "model": str, "memorySystem": str, "planSystem": str, "nickname": str,
                           "bio": str, "goal": str, "cash": int},
    "command.npc.GetNPCInfo": {"NPCID": int},
    "command.npc.GetNPCs": {},
    "command.player.GetPlayerInfo": {},
    "command.timetick.Tick": {},
}


async def listen_server(websocket):
    while True:
        msg = await websocket.recv()
        print(f"Received: {msg}")


async def send_input(websocket):
    # info = json.dumps({"uri": "command.auth.Register", "method": "POST", "data": {"nickname": "fisher", "email": "abc@def.com", "cryptoPWD": "WWW"}}, ensure_ascii=False, separators=(",", ":"))
    # await websocket.send(info)
    uid = "Player-10001"
    while True:
        data = dict()
        command_list = ",".join([x for x in commands.keys()])
        command = input(f"Enter command to send from: {command_list}")
        if command not in commands:
            print("command not in commands list")
            continue
        for key, func in commands[command].items():
            param = func(input(f"Enter param {key}: "))
            data[key] = param
        request = json.dumps({"uid": uid, "uri": command, "data": data, "method": "POST"}, ensure_ascii=False,
                             separators=(",", ":"))
        print(f"Send: {request}")
        await websocket.send(request)


async def ping(websocket):
    # info = json.dumps({"uri": "command.auth.Register", "method": "POST", "data": {"nickname": "fisher", "email": "abc@def.com", "cryptoPWD": "WWW"}}, ensure_ascii=False, separators=(",", ":"))
    # await websocket.send(info)
    uid = "Player-10001"
    while True:
        info = json.dumps({"uid": uid, "uri": "ping", "method": "GET", "data": {}}, ensure_ascii=False,
                          separators=(",", ":"))
        print(f"Send: {info}")
        await websocket.send(info)
        await asyncio.sleep(10)


async def debug(websocket):
    # register
    info = json.dumps({"uri": "command.auth.Register", "method": "POST",
                       "data": {"nickname": "Lixing", "email": "Lixing@163.com", "cryptoPWD": "123456"}},
                      ensure_ascii=False, separators=(",", ":"))
    print(f"Send: {info}")
    await websocket.send(info)
    msg = await websocket.recv()
    print(f"Received: {msg}")
    uid = "Player-10001"
    # GetPlayerInfo
    # time.sleep(3)
    # get_player_info = json.dumps({"uid": uid, "uri": "command.player.GetPlayerInfo", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_player_info}")
    # await websocket.send(get_player_info)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetBuildings
    # # time.sleep(3)
    # get_buildings = json.dumps({"uid": uid, "uri": "command.building.GetBuildings", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_buildings}")
    # await websocket.send(get_buildings)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetBuildingInfo
    # # time.sleep(3)
    # building_id = 1
    # get_building_info = json.dumps({"uid": uid, "uri": "command.building.GetBuildingInfo", "method": "POST", "data": {"buildingID": building_id}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_building_info}")
    # await websocket.send(get_building_info)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetBuildingsConfig
    # # time.sleep(3)
    # get_buildings_config = json.dumps({"uid": uid, "uri": "command.config.GetBuildingsConfig", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_buildings_config}")
    # await websocket.send(get_buildings_config)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetEquipmentsConfig
    # # time.sleep(3)
    # get_equipments_config = json.dumps({"uid": uid, "uri": "command.config.GetEquipmentsConfig", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_equipments_config}")
    # await websocket.send(get_equipments_config)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetNPCsConfig
    # # time.sleep(3)
    # get_npcs_config = json.dumps({"uid": uid, "uri": "command.config.GetNPCsConfig", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_npcs_config}")
    # await websocket.send(get_npcs_config)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetMapScene
    # # time.sleep(3)
    # # GetMapTown
    # # time.sleep(3)
    # get_map_town = json.dumps({"uid": uid, "uri": "command.map.GetMapTown", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_map_town}")
    # await websocket.send(get_map_town)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # GetNPCs
    # time.sleep(3)
    # get_npcs = json.dumps({"uid": uid, "uri": "command.npc.GetNPCs", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_npcs}")
    # await websocket.send(get_npcs)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # GetNPCInfo
    # # time.sleep(3)
    # npc_id = 10001
    # get_npc_info = json.dumps({"uid": uid, "uri": "command.npc.GetNPCInfo", "method": "POST", "data": {"NPCID": npc_id}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_npc_info}")
    # await websocket.send(get_npc_info)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # testName = "changeCash"
    # fake_sendings = json.dumps({"uid": uid, "uri": "command.gm.FakeSendings", "method": "POST", "data": {"testName": testName}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {fake_sendings}")
    # await websocket.send(fake_sendings)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # start_mayor = json.dumps({"uid": uid, "uri": "command.starter.MayorStarter", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {start_mayor}")
    # await websocket.send(start_mayor)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # await asyncio.sleep(10)
    # start_ticks = json.dumps({"uid": uid, "uri": "command.starter.TickStarter", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {start_ticks}")
    # await websocket.send(start_ticks)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # building.Create
    # time.sleep(3)
    # building_type = 3
    # building_name = "dessert shop"
    # building_x = 3
    # building_y = 1
    # building_rotation = 0
    # create_building = json.dumps({"uid": uid, "uri": "command.building.Create", "method": "POST", "data": {"building_type": building_type, "name": building_name, "x": building_x, "y": building_y, "rotation": building_rotation}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_building}")
    # await websocket.send(create_building)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # building_type = 4
    # building_name = "gym"
    # building_x = 3
    # building_y = 2
    # building_rotation = 0
    # create_building = json.dumps({"uid": uid, "uri": "command.building.Create", "method": "POST", "data": {"building_type": building_type, "name": building_name, "x": building_x, "y": building_y, "rotation": building_rotation}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_building}")
    # await websocket.send(create_building)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # building_type = 5
    # building_name = "houseZ"
    # building_x = 3
    # building_y = 4
    # building_rotation = 0
    # create_building = json.dumps({"uid": uid, "uri": "command.building.Create", "method": "POST", "data": {"building_type": building_type, "name": building_name, "x": building_x, "y": building_y, "rotation": building_rotation}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_building}")
    # await websocket.send(create_building)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # building_type = 6
    # building_name = "park"
    # building_x = 4
    # building_y = 2
    # building_rotation = 0
    # create_building = json.dumps({"uid": uid, "uri": "command.building.Create", "method": "POST", "data": {"building_type": building_type, "name": building_name, "x": building_x, "y": building_y, "rotation": building_rotation}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_building}")
    # await websocket.send(create_building)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # building_type = 10
    # building_name = "houseA"
    # building_x = 2
    # building_y = 3
    # building_rotation = 0
    # create_building = json.dumps({"uid": uid, "uri": "command.building.Create", "method": "POST", "data": {"building_type": building_type, "name": building_name, "x": building_x, "y": building_y, "rotation": building_rotation}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_building}")
    # await websocket.send(create_building)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # get_map_scene = json.dumps({"uid": uid, "uri": "command.map.GetMapScene", "method": "POST", "data": {}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {get_map_scene}")
    # await websocket.send(get_map_scene)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # npc.Create
    # time.sleep(3)
    # npc_asset = "premade_01"
    # npc_model = "gpt-3.5"
    # npc_memory = "LongShortTermMemories"
    # npc_plan = "QAFramework"
    # npc_home = 3
    # npc_work = 5
    # npc_nickname = "Alan"
    # npc_bio = "Alan is a genius with outstanding talents and the inventor of computers. Allen has an introverted personality and is only interested in the research he focuses on."
    # npc_goal = "Allen is committed to conducting more work and research."
    # npc_cash = 10000
    # create_npc = json.dumps({"uid": uid, "uri": "command.npc.Create", "method": "POST", "data": {"asset": npc_asset, "model": npc_model, "memorySystem": npc_memory, "planSystem": npc_plan, "homeBuilding": npc_home, "workBuilding": npc_work, "nickname": npc_nickname, "bio": npc_bio, "goal": npc_goal, "cash": npc_cash}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_npc}")
    # await websocket.send(create_npc)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # npc_asset = "premade_04"
    # npc_model = "gpt-3.5"
    # npc_memory = "LongShortTermMemories"
    # npc_plan = "QAFramework"
    # npc_home = 3
    # npc_work = 5
    # npc_nickname = "Fei"
    # npc_bio = "Fei is a talented researcher with a research focus on artificial intelligence. As a university professor, she has a passion for open research in the field of artificial intelligence."
    # npc_goal = "Share with others the progress in the field of artificial intelligence, as well as helping others and answering their questions."
    # npc_cash = 10000
    # create_npc = json.dumps({"uid": uid, "uri": "command.npc.Create", "method": "POST", "data": {"asset": npc_asset, "model": npc_model, "memorySystem": npc_memory, "planSystem": npc_plan, "homeBuilding": npc_home, "workBuilding": npc_work, "nickname": npc_nickname, "bio": npc_bio, "goal": npc_goal, "cash": npc_cash}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {create_npc}")
    # await websocket.send(create_npc)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # Navigate
    # time.sleep(3)
    # content = "Hi, how do you feel abount the town?"
    # target_x = 91
    # target_y = 70
    # navigate = json.dumps({"uid": uid, "uri": "command.map.Navigate", "method": "POST", "data": {"x": target_x, "y": target_y}}, ensure_ascii=False, separators=(",", ":"))
    # print(f"Send: {navigate}")
    # await websocket.send(navigate)
    # msg = await websocket.recv()
    # print(f"Received: {msg}")
    # # ChatToNPC
    # # time.sleep(3)
    npc_id = 10001
    content = "Hi, how do you feel abount the town?"
    chat = json.dumps({"uid": uid, "uri": "command.chat.ChatWithNPC", "method": "POST",
                       "data": {"NPCID": f"NPC-{npc_id}", "content": content}}, ensure_ascii=False,
                      separators=(",", ":"))
    print(f"Send: {chat}")
    await websocket.send(chat)
    msg = await websocket.recv()
    print(f"Received: {msg}")
    server_task = asyncio.create_task(listen_server(websocket))
    await server_task


async def main():
    async with websockets.connect("ws://localhost:8000/ws", ping_interval=None) as websocket:
        msg = await websocket.recv()
        print(f"Received: {msg}")
        # server_task = asyncio.create_task(listen_server(websocket))
        debug_task = asyncio.create_task(debug(websocket))
        # input_task = asyncio.create_task(send_input(websocket))
        ping_task = asyncio.create_task(ping(websocket))

        # await server_task
        await debug_task
        # await input_task
        await ping_task


asyncio.run(main())