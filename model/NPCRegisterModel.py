from mysql.connector import errorcode
from utils.mysql import Mysql
from model.model_base import ModelBase


class NPCRegisterModel(ModelBase):

    # Get a npc's unique ID by npcname.
    def find_id(self, npc):
        db = self.get_db()
        hashid = self.gen_hashid(npc)

        # Find npc=id map from reversed finding table.
        query = f"""
            SELECT
                  
            FROM 
                `find_npc_id` 
            WHERE 
                `hashid`={hashid}
        """
        row = db.fetchone(query, True)
        if not row:
            return 0 #TODO: add erro info

        npcpair = row['npcpair'].split(';')
        id = 0
        for pair in npcpair:
            if pair == '':
                continue

            nameid = pair.split('=')
            # Found.
            if nameid[0] == npc:
                id = nameid[1]
                break

        return int(id)

    # Get a npc's npcname by id.
    def get_npc(self, id):
        db = self.get_db()

        table_name = self.get_account_table_name(id)
        query = f"""
            SELECT
                `npc`
            FROM
                `{table_name}`
            WHERE
                `id`={id}
        """
        row = db.fetchone(query)
        if not row:
            return False

        return row['npc']

    # Get a npc's password by id.
    def get_pwd(self, id):
        db = self.get_db()

        table_name = self.get_account_table_name(id)
        query = f"""
            SELECT
                `pwd`
            FROM
                `{table_name}`
            WHERE
                `id`={id}
        """
        row = db.fetchone(query)
        if not row:
            return False

        return row['pwd']

    # Register a new npc.
    def reg_npc(self, npc, pwd=''):
        db = self.get_db()

        table_name = ''
        idx = 0
        # Get current table name.
        for i in range(self.config.db_account_cur_table, self.config.db_account_max_table):
            idx = i
            table_name = f"npc{i+1:03}"
            query = f"""
                SELECT
                    max(`id`) as maxid
                FROM
                    `{table_name}`
            """
            row = db.fetchone(query)
            if not row or not row['maxid']:
                break
            count = int(row['maxid']) - i * self.config.db_account_per_table
            if count < self.config.db_account_per_table:
                break

        # Insert a new account item.
        query = f"""
            INSERT INTO `{table_name}`
                (`npc`,`pwd`,`time`)
            VALUES
                ('{npc}','{pwd}',{self.get_nowtime()})
        """
        if not db.execute(query, True, True):
            # Insert failed.
            if db.last_errno != errorcode.ER_NO_SUCH_TABLE:
                return 0

            # Calculate auto_increment value.
            auto_increment = 10001
            if idx > 0:
                auto_increment = idx * self.config.db_account_per_table + 1

            # Create a new table.
            if not self.create_account_table(table_name, auto_increment):
                return 0
            if not db.execute(query, need_rowid=True):
                return 0

        id = db.last_rowid

        # Generate reversed finding info.
        hashid = self.gen_hashid(npc)

        # Find npc=id map from reversed finding table.
        query = f"""
            SELECT
                `npcpair`
            FROM
                `find_npc_id`
            WHERE
                `hashid`={hashid}
        """
        row = db.fetchone(query, True)
        if row == False:
            if db.last_errno != errorcode.ER_NO_SUCH_TABLE:
                return 0
            # Try to create a new table.
            if not self.create_findnpcid_table():
                return 0
            row = None

        if row is None:  # hashid does not exist.
            npcpair = f"{npc}={id};"
            query = f"""
                INSERT INTO `find_npc_id`
                    (`hashid`,`npcpair`)
                VALUES
                    ({hashid},'{npcpair}')
            """
            if not db.execute(query):
                return 0
        else:  # hashid exists.
            npcpair = f"{row['npcpair']}{npc}={id};"
            query = f"""
                UPDATE
                    `find_npc_id`
                SET
                    `npcpair`='{npcpair}'
                WHERE
                    `hashid`={hashid}
            """
            if not db.execute(query):
                return 0

        return int(id)

    # Create the 'accountXXX' table.
    def create_account_table(self, table_name, auto_increment=10001):
        db = self.get_db()
        query = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}`(
                `id` INT NOT NULL AUTO_INCREMENT,
                `npc` VARCHAR(255) NOT NULL,
                `pwd` VARCHAR(255) NOT NULL,
                `time` BIGINT NOT NULL,
                PRIMARY KEY(`id`),
                UNIQUE KEY(`npc`)) AUTO_INCREMENT={auto_increment}
        """
        return db.execute(query)

    # Create the 'find_npc_id' table.
    def create_findnpcid_table(self):
        db = self.get_db()
        query = f"""
            CREATE TABLE IF NOT EXISTS `find_npc_id`(
                `hashid` INT NOT NULL,
                `npcpair` TEXT NOT NULL,
                PRIMARY KEY(`hashid`))
        """
        return db.execute(query)

    def get_account_table_name(self, id):
        # Hash to different table according to id.
        hashid = int(id / self.config.db_account_per_table + 1)
        return f"npc{hashid:03}"

    def get_db(self):
        if 'account' not in self.cmd.db_cache:
            self.cmd.db_cache['account'] = Mysql(
                self.app,
                self.config.get_db_host('account'),
                self.config.get_db_port('account'),
                self.config.get_db_user('account'),
                self.config.get_db_pwd('account'),
                self.config.get_db_name('account'),
            )
        return self.cmd.db_cache['account']
