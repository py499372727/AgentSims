from audioop import add
from random import randbytes
from command.auth.login_base import LoginBase


class Register(LoginBase):
    """register player."""
    def clear_invalid_char(self, sql, max_length=50):
        dirty_stuff = ["\"", "\\", "/", "*", "'", "=", "-", "#", ";", "<", ">", "+", "%", "$", "(", ")", "%","!", "\u200B"]
        for stuff in dirty_stuff:
            sql = sql.replace(stuff, "")
        return sql[:max_length]

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['nickname', 'email', 'cryptoPWD']):
            return False
        # # Get address.
        # # TODO Do more checks about the address.
        nickname, email, cryptoPWD = self.clear_invalid_char(params['data']['nickname'].strip()), self.clear_invalid_char(params['data']['email'].strip()), self.clear_invalid_char(params['data']['cryptoPWD'].strip())

        # Get user's Unique ID.
        account_model = self.get_model('Account')
        id = account_model.find_id(email)
        if id <= 0:
            id = account_model.reg_user(email, cryptoPWD)
            if id <= 0:
                return self.error('register user failed')
        else:
            if cryptoPWD != account_model.get_pwd(id):
                return self.error('user password error')
        self.id = id
        
        uid = self.gen_token("Player", id)

        buildings_info, npcs_info = self.handle_login(nickname, uid)

        # Return nonce and sign message.
        return {'email': email, 'nickname': nickname, 'cryptoPWD': cryptoPWD, 'uid': uid, "buildings": buildings_info, "npcs": npcs_info}

    def is_check_token(self):
        return False
