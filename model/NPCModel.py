from model.single_model_base import SingleModelBase


class NPCModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)

        # NPC's name
        self.name = None
        self.server = None
        self.map = None
        self.cash = None
        self.x = None
        self.y = None
        self.rotation = None
        
        self.asset = None
        self.model = None
        self.memorySystem = None
        self.planSystem = None
        self.bio = None
        self.goal = None
        
        self.home_building = None
        self.work_building = None

        self.reg_time = self.get_nowtime()
        self.login_time = self.reg_time
        self.refresh_time = self.reg_time
        self.timezone = 0
        self.path = None
        self.act = None
        self.plan = None
        self.event = None
        self.last_move = None
        self.act_timeout = None
        self.chats = None
        self.new_chats = list()
        # Resources.
        # ORM mapping.
        self.orm['name'] = SingleModelBase.STRING
        self.orm['server'] = SingleModelBase.STRING
        self.orm['map'] = SingleModelBase.INT

        self.orm['cash'] = SingleModelBase.INT
        self.orm['x'] = SingleModelBase.INT
        self.orm['y'] = SingleModelBase.INT
        self.orm['rotation'] = SingleModelBase.INT
        
        self.orm['asset'] = SingleModelBase.STRING
        self.orm['model'] = SingleModelBase.STRING
        self.orm['planSystem'] = SingleModelBase.STRING
        self.orm['memorySystem'] = SingleModelBase.STRING
        self.orm['bio'] = SingleModelBase.STRING
        self.orm['goal'] = SingleModelBase.STRING
        
        self.orm['home_building'] = SingleModelBase.INT
        self.orm['work_building'] = SingleModelBase.INT

        self.orm['reg_time'] = SingleModelBase.TIME
        self.orm['login_time'] = SingleModelBase.TIME
        self.orm['refresh_time'] = SingleModelBase.TIME
        self.orm['timezone'] = SingleModelBase.INT
        self.orm['path'] = SingleModelBase.OBJECT
        # act plan event: record time & target
        self.orm['act'] = SingleModelBase.OBJECT
        self.orm['plan'] = SingleModelBase.STRING
        self.orm['event'] = SingleModelBase.OBJECT
        self.orm['last_move'] = SingleModelBase.TIME
        self.orm['act_timeout'] = SingleModelBase.TIME
        self.orm['chats'] = SingleModelBase.OBJECT

    def init(self):
        self.name = ''
        self.server = ''
        self.map = -1
        self.cash = 0
        self.x = -1
        self.y = -1
        self.rotation = 0
        
        self.home_building = 0
        self.work_building = 0

        self.reg_time = self.get_nowtime()
        self.login_time = self.reg_time
        self.refresh_time = self.reg_time
        self.timezone = 0
        self.path = []
        self.act = {"action": "planning", "time": self.app.last_game_time}
        self.plan = "planning"
        self.event = list()
        self.last_move = 0
        self.act_timeout = 0
        self.chats = dict()
        # print("Player Model inited")
    
    def change_cash(self, amount, trigger_uid, is_increase=True):
        if not amount:
            return True
        if is_increase:
            self.cash += amount
        else:
            if self.cash < amount:
                return False
            self.cash -= amount
        self.app.send(f"Player-{self.map}", {"code": 200, "uri": "changeCash", "uid": trigger_uid, "data": {"uid": self.get_token(), "cash": self.cash, "amount": amount, "effect": "increase" if is_increase else "decrease"}})
        return True
    
    def get_token(self):
        return f"NPC-{self.id}"
    
    def add_event(self, event):
        if event.get("action", "").startswith("Talking"):
            event["action"] = event["action"].replace("Talking", "Talked")
        events = self.event[::-1]
        event["end_time"] = self.app.last_game_time
        if "earn" in event or "cost" in event:
            earn = event.get("earn", 0)
            cost = event.get("cost", 0)
            # print("earn:", earn, type(earn), "cost:", cost, type(cost))
            self.change_cash(int(earn), self.get_token(), True)
            if not self.change_cash(int(cost), self.get_token(), False):
                # TODO: no cash to pay
                pass
            if int(cost):
                player_model = self.get_single_model("Player", self.map, create=False)
                if player_model:
                    player_model.change_revenue(int(cost), self.get_token(), True)
                    player_model.save()
        # send info: NPC finish action
        self.app.send(f"Player-{self.map}", {"code": 200, "uri": "finishAction", "uid": self.get_token(), "data": {"uid": self.get_token(), "action": event["action"],"startTime": event["time"],"endTime": self.app.last_game_time}})
        events.append(event)
        events = events[::-1]
        if len(events) > 3:
            events = events[:3]
        self.event = events
    
    def get_name(self):
        return self.name
    
    def set_action(self, action):
        push_info = {"uid": self.get_token()}
        for key, value in action.items():
            push_info[key] = value
        self.app.send(f"Player-{self.map}", {"code": 200, "uri": "newAction", "uid": self.get_token(), "data": push_info})
        self.act = action
    
    def add_chat(self, uid, content, isSender=True):
        chats = self.chats.get(uid, list())[::-1]
        if chats and self.app.last_game_time - chats[-1]["createTime"] >= 1000 * 60 * 60 * 3:
            chats = list()
        chats.append({"createTime": self.app.last_game_time, "content": content.partition(": ")[2], "isSender": isSender})
        chats = chats[::-1]
        if len(chats) > 10:
            chats = chats[:10]
        self.chats[uid] = chats
        if not isSender:
            self.new_chats.append({"sender": uid, "createTime": self.app.last_game_time, "content": content.partition(": ")[2]})
