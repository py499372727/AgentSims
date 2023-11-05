from mysql.connector import errorcode
from utils.mysql import Mysql
from model.model_base import ModelBase
from model.single_model_base import SingleModelBase
from model.NPCRegisterModel import NPCRegisterModel
from agent.utils.llm import LLMCaller


class EvalModel(ModelBase):
    def __init__(self, app, cmd, id, eval_cfg):
        super().__init__(app, cmd)
        self.player_id = id # TODO:
        self.eval_cfg = eval_cfg
        self.target_nickname = eval_cfg.target_nickname
        self.query = eval_cfg.query
        self.measure = eval_cfg.measurement
        self.interval = eval_cfg.eval_interval # unit: tick 
        assert 'response' in self.measure # for easy eval
        self.created = True

    def retrieve(self):
        return True # placeholder, to fit the process in Tick.get_single_model
    async def ask (self, *args, **kwargs):
    #  ask questions to a specific npc
        for npc_id, actor in self.app.actors.items():
            if actor.agent.name == self.target_nickname:
                target_npc_id = npc_id
                # target_npc = self.app.actors[target_npc_id]
                response = await actor.agent.caller.ask(self.query)
                return response
        
        return f"eval target {self.target_nickname} not found"


    async def eval(self, response):
        try:
            eval_fct = eval(f'lambda response: {self.measure}')
            eval_result = eval_fct(response)
            return eval_result
        except Exception as e:
            print(f"Error: {e} \n occurred when using the custom eval function\n: {self.measure} \n to response {response}")
            return e

    async def __call__(self, *args, **kwargs):
        response = await self.ask()
        response = response['response']
        assert type(response) is str, f'response should be a string, current response is {response}'
        return self.eval(response), response

    def __repr__(self):
        return f'''
            EvalModel(\n
            app={self.app}, \n
            cmd={self.cmd}, \n
            id={self.id}, \n
            eval_cfg={self.eval_cfg}\n
            )
        '''