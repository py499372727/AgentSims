from utils import utils


class Config:
    """Main configuration."""

    def __init__(self, path):

        # Load json file.
        obj = utils.load_json_file(path)

        # Read data.
        self.version = obj["version"]
        self.online = obj["online"]
        self.tick_cooldown = utils.get_json_value(
            obj, "tick_cooldown", 3600000)
        self.tick_count_limit = utils.get_json_value(
            obj, "tick_count_limit", 20)
        self.mayor_cooldown = utils.get_json_value(
            obj, "mayor_cooldown", 3600000)
        self.mayor_count_limit = utils.get_json_value(
            obj, "mayor_count_limit", 5)
        self.eval_interval_tick = utils.get_json_value(
            obj, "eval_interval_tick", 1)

        # Database parameters.
        # User count for each game database.
        self.db_user_per_db = utils.get_json_value(
            obj, "db_user_per_db", 500000)

        # Current account table index.
        self.db_account_cur_table = utils.get_json_value(
            obj, "db_account_cur_table", 0)
        # Account max table count.
        self.db_account_max_table = utils.get_json_value(
            obj, "db_account_max_table", 50)
        # Account count for each account table.
        self.db_account_per_table = utils.get_json_value(
            obj, "db_account_per_table", 2000000)

        # MySQL connection pool size.
        self.db_pool_size = utils.get_json_value(obj, "db_pool_size", 4)

        # MySQL database path.
        # Account database.
        self.db_account_host = utils.get_json_value(
            obj, "db_account_host", "127.0.0.1")
        self.db_account_port = utils.get_json_value(
            obj, "db_account_port", 3306)
        self.db_account_user = utils.get_json_value(
            obj, "db_account_user", "root")
        self.db_account_pwd = utils.get_json_value(
            obj, "db_account_pwd", "")
        self.db_account_name = utils.get_json_value(
            obj, "db_account_name", "llm_account")

        # Game database - global tables.
        self.db_game_host = utils.get_json_value(
            obj, "db_game_host", "127.0.0.1")
        self.db_game_port = utils.get_json_value(
            obj, "db_game_port", 3306)
        self.db_game_user = utils.get_json_value(
            obj, "db_game_user", "root")
        self.db_game_pwd = utils.get_json_value(
            obj, "db_game_pwd", "")
        self.db_game_name = utils.get_json_value(
            obj, "db_game_name", "llm_game")

        # Single info database 0001.
        self.db_game0001_host = utils.get_json_value(
            obj, "db_game0001_host", "127.0.0.1")
        self.db_game0001_port = utils.get_json_value(
            obj, "db_game0001_port", 3306)
        self.db_game0001_user = utils.get_json_value(
            obj, "db_game0001_user", "root")
        self.db_game0001_pwd = utils.get_json_value(
            obj, "db_game0001_pwd", "")
        self.db_game0001_name = utils.get_json_value(
            obj, "db_game0001_name", "llm_game0001")

        # Single info database 0002.
        self.db_game0002_host = utils.get_json_value(
            obj, "db_game0002_host", "127.0.0.1")
        self.db_game0002_port = utils.get_json_value(
            obj, "db_game0002_port", 3306)
        self.db_game0002_user = utils.get_json_value(
            obj, "db_game0002_user", "root")
        self.db_game0002_pwd = utils.get_json_value(
            obj, "db_game0002_pwd", "")
        self.db_game0002_name = utils.get_json_value(
            obj, "db_game0002_name", "llm_game0002")

    def get_db_host(self, key):
        return getattr(self, f"db_{key}_host")

    def get_db_port(self, key):
        return getattr(self, f"db_{key}_port")

    def get_db_user(self, key):
        return getattr(self, f"db_{key}_user")

    def get_db_pwd(self, key):
        return getattr(self, f"db_{key}_pwd")

    def get_db_name(self, key):
        return getattr(self, f"db_{key}_name")

class EvalConfig:
    def __init__(self, obj):
        self.id = obj['id']
        self.target_nickname = obj['target_nickname']
        self.query = obj['query']
        self.measurement = obj['measurement']
        self.eval_interval = obj['interval']
    def to_json(self):
        return vars(self)


class BuildingConfig:
    def __init__(self, obj):
        self.id = obj["id"]
        self.type = obj["type"]
        self.price = obj["price"]

        self.width = utils.get_json_value(obj, "width", 1)
        self.height = utils.get_json_value(obj, "height", 1)
        self.assets = utils.get_json_value(obj, "assets", "none")
        self.blocks = utils.get_json_value(obj, "blocks", [[1]])
        self.equipments = utils.get_json_value(obj, "equipments", [[0]])
    
    def to_json(self):
        return { #TODO var() can serve as the to_dict
            "id": self.id,
            "type": self.type,
            "price": self.price,
            "width": self.width,
            "height": self.height,
            "assets": self.assets,
            "blocks": self.blocks,
            "equipments": self.equipments,
        }

class EquipmentConfig:
    def __init__(self, obj):
        self.id = obj["id"]
        self.type = obj["type"]

        self.width = utils.get_json_value(obj, "width", 1)
        self.height = utils.get_json_value(obj, "height", 1)
        self.assets = utils.get_json_value(obj, "assets", "none")
        self.description = utils.get_json_value(obj, "description", "")
        self.functions = utils.get_json_value(obj, "functions", [])
        self.economic = utils.get_json_value(obj, "economic", 0)
        self.price = utils.get_json_value(obj, "price", 0)
        self.hireCapacity = utils.get_json_value(obj, "hireCapacity", 0)
        self.livingCapacity = utils.get_json_value(obj, "livingCapacity", 0)
    
    def to_json(self):
        return {
            "id": self.id,
            "type": self.type,
            "price": self.price,
            "width": self.width,
            "height": self.height,
            "assets": self.assets,
            "functions": self.functions,
            "economic": self.economic,
            "description": self.description,
            "hireCapacity": self.hireCapacity,
            "livingCapacity": self.livingCapacity,
        }

class EconomicConfig:
    def __init__(self, obj):
        self.id = obj["id"]

        self.menu = utils.get_json_value(obj, "menu", dict())
        self.salary = utils.get_json_value(obj, "salary", 0)

    def to_json(self):
        return {
            "id": self.id,
            "menu": self.menu,
            "salary": self.salary,
        }

class NPCConfig:
    def __init__(self, path):
        # Load json file.
        obj = utils.load_json_file(path)

        self.assets = obj["assets"]
        self.models = obj["models"]
        self.memorySystems = obj["memorySystems"]
        self.planSystems = obj["planSystems"]
    
    def to_json(self):
        return {
            "assets": self.assets,
            "models": self.models,
            "memorySystems": self.memorySystems,
            "planSystems": self.planSystems,
        }

class FrameworkConfig:
    def __init__(self, path):
        # Load json file.
        obj = utils.load_json_file(path)

        self.map = obj["map"]
        self.buildings = obj["buildings"]
        self.equipments = obj["equipments"]
    
    def to_json(self):
        return {
            "map": self.map,
            "buildings": self.buildings,
            "equipments": self.equipments,
        }

