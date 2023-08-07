from model.single_model_base import SingleModelBase


class TownModel(SingleModelBase):
    def __init__(self, app, cmd, id):
        super().__init__(app, cmd, id)

        self.taxes = None
        self.taxRate = None
        self.records = None
        
        self.last_real_time = None
        self.last_game_time = None

        # ORM mapping.
        self.orm['taxes'] = SingleModelBase.INT
        self.orm['taxRate'] = SingleModelBase.INT
        self.orm['records'] = SingleModelBase.OBJECT
        self.orm['last_real_time'] = SingleModelBase.TIME
        self.orm['last_game_time'] = SingleModelBase.TIME

    def init(self):
        self.taxes = 1000000
        self.taxRate = 10
        self.records = list()
        
        self.last_real_time = self.get_nowtime()
        self.last_game_time = self.get_nowtime()
