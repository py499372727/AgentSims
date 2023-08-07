import subprocess
from command.command_base import CommandBase

class MayorStarter(CommandBase):
    """start mayor."""

    def execute(self, params):
        # Check params.
        if not self.check_params(params, ['uid']):
            return False
        
        mayor_state = self.app.mayor_state
        if mayor_state["start"]:
            return self.error("already start")
        elif self.app.get_nowtime() - mayor_state["start_time"] < self.app.config.mayor_cooldown:
            return self.error("still cooldown")
        cmd = f"nohup python3.9 -u mayor.py {self.app.config.mayor_count_limit} >> logs/mayor.log 2>&1 &"
        print(subprocess.getstatusoutput(cmd))
        # Return nonce and sign message.
        return {'start': True}
