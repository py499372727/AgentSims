import importlib


class Base:
    """Base class for commands and models. """

    def __init__(self, app, cmd):
        self.app = app
        self.cmd = cmd  # Running command.
        self.config = self.app.config
        # self.logger = self.app.logger

    # Get a single user model object.
    # create: Create a new object or not when data doesn't exist.
    def get_single_model(self, name, id=None, create=True, *args, **kwargs):
        # name: NPC, Map, Building
        # id: 4 digit number
        if id is None:
            id = self.get_id()
        if id is None or ( type(id) is int and  id <= 0):
            return None


        cache_key = f"{name}_{id}"
        if cache_key not in self.cmd.model_cache:
            # Import module.
            # TODO: too vulnerable
            module = importlib.import_module(f"model.{name}Model")
            # Get class.
            cls = getattr(module, f"{name.split('.')[-1]}Model")
            # Create model.
            model = cls(self.app, self.cmd, id, *args, **kwargs)

            if not model.retrieve():
                if create:
                    model.init()
                    model.is_created = True
                else:
                    return None
            self.cmd.model_cache[cache_key] = model

        return self.cmd.model_cache[cache_key]

    # Get a config model object.
    def get_config_model(self, name):
        return self.get_model(f"config.{name}")

    # Get a game model object.
    def get_game_model(self, name):
        return self.get_model(f"{name}Game")

    # Get a model object.
    def get_model(self, name):
        if name not in self.cmd.model_cache:
            # Import module.
            module = importlib.import_module(f"model.{name}Model")
            # Get class.
            cls = getattr(module, f"{name.split('.')[-1]}Model")
            # Create model.
            self.cmd.model_cache[name] = cls(self.app, self.cmd)
        return self.cmd.model_cache[name]

    def get_id(self):
        return None

    # Get current time as timestamp - milliseconds.
    def get_nowtime(self):
        return self.app.get_nowtime()

    # Get current time as timestamp - seconds.
    def get_nowtime_seconds(self):
        return self.app.get_nowtime_seconds()

    # Generate a hash id, using time33 hash algorithm.
    def gen_hashid(self, str):
        hash = 0
        for i in range(len(str)):
            cc = ord(str[i])
            hash += (hash << 5) + cc
            hash &= 0x7FFFFFFF
        hash %= 5000000
        return hash

    # def get_web3_config(self):
    #     return self.app.get_web3_config()

    # def get_npc_config(self, id):
    #     return self.app.get_npc_config(id)
