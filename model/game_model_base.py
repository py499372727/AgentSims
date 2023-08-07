from utils.mysql import Mysql
from model.model_base import ModelBase


class GameModelBase(ModelBase):

    def get_db(self):
        if 'game' not in self.cmd.db_cache:
            self.cmd.db_cache['game'] = Mysql(
                self.app,
                self.config.get_db_host('game'),
                self.config.get_db_port('game'),
                self.config.get_db_user('game'),
                self.config.get_db_pwd('game'),
                self.config.get_db_name('game'),
            )
        return self.cmd.db_cache['game']

    # Get the table name.
    # The default is the class name removed right 'GameModel'.
    def get_table_name(self):
        if self.table_name is None:
            self.table_name = self.__class__.__name__.removesuffix(
                'GameModel').lower()
        return self.table_name

    # Get the model name.
    # The default is the class name removed right 'GameModel'.
    def get_model_name(self):
        if self.model_name is None:
            self.model_name = self.__class__.__name__.removesuffix('GameModel')
        return self.model_name
