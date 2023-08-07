from model.single_model_base import SingleModelBase


class PlayerModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)

        # Player's leader ID, If type=member, follow whom.
        self.name = None
        self.x = None
        self.y = None
        self.rotation = None
        self.revenue = None

        self.reg_time = self.get_nowtime()
        self.login_time = self.reg_time
        self.refresh_time = self.reg_time
        self.timezone = 0
        self.path = None
        self.last_move = None
        self.chats = None
        # Resources.
        # ORM mapping.
        self.orm['name'] = SingleModelBase.STRING
        self.orm['x'] = SingleModelBase.INT
        self.orm['y'] = SingleModelBase.INT
        self.orm['rotation'] = SingleModelBase.INT
        self.orm['revenue'] = SingleModelBase.INT

        self.orm['reg_time'] = SingleModelBase.TIME
        self.orm['login_time'] = SingleModelBase.TIME
        self.orm['refresh_time'] = SingleModelBase.TIME
        self.orm['timezone'] = SingleModelBase.INT
        self.orm['path'] = SingleModelBase.OBJECT
        self.orm['last_move'] = SingleModelBase.TIME
        self.orm['chats'] = SingleModelBase.OBJECT

    def init(self):
        self.name = ''
        self.x = -1
        self.y = -1
        self.rotation = 0
        self.revenue = 1000000

        self.reg_time = self.get_nowtime()
        self.login_time = self.reg_time
        self.refresh_time = self.reg_time
        self.timezone = 0
        self.path = list()
        self.last_move = 0
        self.chats = dict()
        # print("Player Model inited")

    def get_token(self):
        return f"Player-{self.id}"
    
    def change_revenue(self, amount, trigger_uid, is_increase=True):
        if is_increase:
            self.revenue += amount
        else:
            if self.revenue < amount:
                return False
            self.revenue -= amount
        self.app.send(f"Player-{self.id}", {"code": 200, "uri": "changeRevenue", "uid": trigger_uid, "data": {"uid": f"Player-{self.id}", "revenue": self.revenue, "amount": amount, "effect": "increase" if is_increase else "decrease"}})
        return True

    def add_chat(self, uid, content, isSender=True):
        chats = self.chats.get(uid, list())[::-1]
        if chats and self.app.last_game_time - chats[-1]["createTime"] >= 1000 * 60 * 60 * 3:
            chats = list()
        chats.append({"createTime": self.app.last_game_time, "content": content.partition(": ")[2], "isSender": isSender})
        chats = chats[::-1]
        if len(chats) > 10:
            chats = chats[:10]
        self.chats[uid] = chats

    def get_name(self):
        return self.name
