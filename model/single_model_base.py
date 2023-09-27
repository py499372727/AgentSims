import json
from mysql.connector import errorcode
from utils.mysql import Mysql
from model.model_base import ModelBase


class SingleModelBase(ModelBase):

    # DB data type definition.
    BOOL = 'bool'       # TINYINT
    INT = 'int'         # INT
    TIME = 'time'       # BIGINT
    STRING = 'string'   # VARCHAR(255)
    OBJECT = 'object'   # MEDIUMTEXT json-encoded

    def __init__(self, app, cmd, id):
        super().__init__(app, cmd)

        # Is a new created data object.
        self.is_created = False

        # User's unique ID.
        self.id = id

        # ORM mapping.
        self.orm = {'id': SingleModelBase.INT}

    # Initialize default data here.
    def init(self):
        pass

    # Get user's unique ID.
    def get_id(self):
        return self.id

    # Convert orm data to k,v object.
    def as_object(self, include_id=False):
        result = {}
        for key in self.orm.keys():
            if key != 'id' or include_id:
                result[key] = getattr(self, key)
        return result

    # Get a idle id from an array.
    def get_idle_id(self, array, key='id', min=1, max=10000):
        for i in range(min, max+1):
            found = False
            for item in array:
                if key in item and item[key] == i:
                    found = True
                    break
            if not found:
                break
        return i

    def flush(self):
        if self.is_created:
            return self.create()
        if self.is_modified:
            return self.update()
        return True

    def create(self):
        db = self.get_db()
        table_name = self.get_table_name()

        # Insert a data item.
        query = f"INSERT INTO `{table_name}`("
        for key in self.orm:
            query += f"`{key}`,"
        query = query.rstrip(',')
        query += ") VALUES("
        for key, type in self.orm.items():
            value = getattr(self, key)
            if type == SingleModelBase.BOOL:
                query += f"{1 if value else 0},"
            elif type == SingleModelBase.INT or type == SingleModelBase.TIME:
                query += f"{value},"
            elif type == SingleModelBase.STRING:
                object_value = value[:255].replace("'", "`") if value else None
                query += f"'{object_value}',"
            elif type == SingleModelBase.OBJECT:
                object_value = json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace("'", "`")
                query += f"'{object_value}',"
            else:
                self.logger.warn(f"unknown value type: {type}")
                return False
        query = query.rstrip(',')
        query += ")"
        # print(query)

        if not db.execute(query, True):
            # Insert failed.
            if db.last_errno != errorcode.ER_NO_SUCH_TABLE:
                return False

            # Create a new table.
            query_create = f"CREATE TABLE IF NOT EXISTS `{table_name}`("
            for key, type in self.orm.items():
                if type == SingleModelBase.BOOL:
                    query_create += f"`{key}` TINYINT NOT NULL,"
                elif type == SingleModelBase.INT:
                    query_create += f"`{key}` INT NOT NULL,"
                elif type == SingleModelBase.TIME:
                    query_create += f"`{key}` BIGINT NOT NULL,"
                elif type == SingleModelBase.STRING:
                    query_create += f"`{key}` VARCHAR(255) NOT NULL,"
                elif type == SingleModelBase.OBJECT:
                    query_create += f"`{key}` MEDIUMTEXT NOT NULL,"
                else:
                    self.logger.warn(f"unknown value type: {type}")
            query_create += "PRIMARY KEY(`id`))"

            if not db.execute(query_create):
                return False
            if not db.execute(query):
                return False

        return True

    def retrieve(self):
        # Only retrieve once.
        if self.is_retrieved: # TODO: have retrieved the value no need to retrieve again ?
            return True

        db = self.get_db()
        table_name = self.get_table_name()

        query = "SELECT "
        for key in self.orm:
            query += f"`{key}`,"
        query = query.rstrip(',')
        query += f" FROM `{table_name}` WHERE `id`={self.id}"
        row = db.fetchone(query, True)
        if not row:
            return False

        for key, type in self.orm.items():
            if type == SingleModelBase.BOOL:
                setattr(self, key, True if row[key] else False)
            elif type == SingleModelBase.INT or type == SingleModelBase.TIME:
                setattr(self, key, int(row[key]))
            elif type == SingleModelBase.STRING:
                setattr(self, key, str(row[key])[:255].replace("`", "'") if row[key] else None)
            elif type == SingleModelBase.OBJECT:
                setattr(self, key, json.loads(row[key].replace("`", "'")))
            else:
                self.logger.warn(f"unknown value type: {type}")

        self.is_retrieved = True
        return True

    def update(self):
        db = self.get_db()
        table_name = self.get_table_name()

        query = f"UPDATE `{table_name}` SET "
        for key, type in self.orm.items():
            if key == 'id':
                continue

            value = getattr(self, key)
            if type == SingleModelBase.BOOL:
                query += f"`{key}`={1 if value else 0},"
            elif type == SingleModelBase.INT or type == SingleModelBase.TIME:
                query += f"`{key}`={value},"
            elif type == SingleModelBase.STRING:
                object_value = value[:255].replace("'", "`") if value else None
                query += f"`{key}`='{object_value}',"
            elif type == SingleModelBase.OBJECT:
                object_value = json.dumps(value).replace("'", "`")
                query += f"`{key}`='{object_value}',"
            else:
                self.logger.warn(f"unknown value type: {type}")
        query = query.rstrip(',')
        query += f" WHERE `id`={self.id}"
        if not db.execute(query):
            return False

        return True

    def delete(self):
        db = self.get_db()
        table_name = self.get_table_name()

        query = f"DELETE FROM `{table_name}` WHERE `id`={self.id}"
        if not db.execute(query):
            return False

        return True

    def get_db(self):
        # Hash to different database according to id.
        hashid = int(self.id / self.config.db_user_per_db) + 1
        key = f"game{hashid:04}"
        if key not in self.cmd.db_cache:
            self.cmd.db_cache[key] = Mysql(
                self.app,
                self.config.get_db_host(key),
                self.config.get_db_port(key),
                self.config.get_db_user(key),
                self.config.get_db_pwd(key),
                self.config.get_db_name(key),
            )
        return self.cmd.db_cache[key]
