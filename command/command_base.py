import json
import asyncio
from random import randbytes
# from flask import request
from base import Base


class CommandBase(Base):
    def __init__(self, app):
        super().__init__(app, self)

        # Cached models.
        self.model_cache = {}
        # Cached dbs.
        self.db_cache = {}

        self.id = 0
        self.type = ""
        self.last_error = None

        # Cached command name.
        self.command_name = None

    async def _execute(self, params=None):

        # Get token from params.
        token = None
        if self.is_check_token() and 'uid' in params:
            token = params['uid']
            try:
                self.type = token.split('-')[0]
                self.id = int(token.split('-')[1])
            except ValueError:
                pass

        # Check token and execute command.
        data = False
        if not self.is_check_token() or self.check_token(token):
            if asyncio.iscoroutinefunction(self.execute):
                data = await self.execute(params)
            else:
                data = self.execute(params)

        # Generate return data.
        # False from Command = system level fail - unexpected error.
        # {'errno': } from Command = command level fail - simply not flush.
        ret = {}
        if not data:
            if self.last_error is None:
                ret['error'] = 'unknown error'
                self.log_error()
            else:
                ret['error'] = self.last_error['error']
                ret['doRefresh'] = self.last_error['doRefresh']
        else:
            # Flush database modifications.
            # TODO Deal with failed flush.
            if type(data) is not dict or 'errno' not in data:
                for model in self.cmd.model_cache.values():
                    model.flush()
            ret['data'] = data

        return ret

    # Check token.
    def check_token(self, token):
        if token is None:
            return self.error('invalid params', is_log=True)
        type = token.split('-')[0]
        if type not in ['Player', 'NPC']:
            return self.error('invalid token', is_log=True)
        checking_model = self.get_single_model(type, create=False)
        if checking_model is None:
            return self.error('invalid token', is_log=True)
        return True

    # Check params.
    def check_params(self, params, keys):
        for key in keys:
            if key not in params and key not in params.get("data", dict()):
                return self.error('invalid params')
        return True

    # Generate a token - ID:time:random
    def gen_token(self, type, id):
        return f"{type}-{id}"

    # Simply return an error.
    # context: error context.
    # is_log: whether save the log.
    def error(self, error, context=None, is_log=True, refresh=True):
        params = {
            'error': error,
            'context': context,
            'doRefresh': refresh
        }
        if not is_log:
            self.last_error = params
            return False
        return self.log_error(params)

    # Generate and save error log.
    def log_error(self, params=None):
        if params is None:
            params = {}

        if 'uid' not in params:
            params['uid'] = self.get_id()
        if 'user' not in params:
            params['user'] = self.get_user()
        if 'command' not in params:
            params['command'] = self.get_command_name()
        # if 'request' not in params:
        #     params['request'] = request.data.decode('utf-8')
        if 'error' not in params:
            params['error'] = 'unknown error'
        if 'time' not in params:
            params['time'] = self.get_nowtime()
        if 'context' not in params or params['context'] is None:
            params['context'] = {}
        if params['doRefresh'] not in params:
            params["doRefresh"] = True

        # TODO Add more context.

        # Json encode the context data.
        params['context'] = json.dumps(params['context'])

        # Save to database.
        # errlog_model = self.get_model('statistics.Errlog')
        # errlog_model.add_log(params)
        self.app.log(json.dumps(params, ensure_ascii=False, separators=(",", ":")))

        self.last_error = params
        return False

    # Get current user's ID.
    def get_id(self):
        return self.id

    # Get user name.
    def get_user(self):
        session_model = self.get_single_model(self.type, create=False)
        if session_model is None:
            return ''
        return session_model.get_name()

    # Get token.
    def get_token(self):
        session_model = self.get_single_model(self.type, create=False)
        if session_model is None:
            return ''
        return session_model.get_token()

    # Get command name - equal to the class name.
    def get_command_name(self):
        if self.command_name is None:
            self.command_name = self.__module__.removeprefix('command.')
        return self.command_name

    # Whether to check token for this api call.
    def is_check_token(self):
        return True
