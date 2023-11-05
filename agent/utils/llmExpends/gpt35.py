from typing import List, Dict, Any
import os
import json
import traceback
import openai_async as openai
from agent.utils.llmExpends.BasicCaller import BasicCaller

abs_path = os.path.dirname(os.path.realpath(__file__))

class GPT35Caller(BasicCaller):
    def __init__(self) -> None:
        self.model = "gpt-3.5-turbo"
        self.api_key = ""
        with open(os.path.join(abs_path, "..", "..", "..", "config", "api_key.json"), "r", encoding="utf-8") as api_file:
            api_keys = json.loads(api_file.read())
            self.api_key = api_keys["gpt-3.5"]
        if not self.api_key:
            raise ValueError("Api key not found")
    
    async def ask(self, prompt: str) -> str:
        counter = 0
        result = "{}"
        while counter < 3:
            try:
                request_body = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    'temperature' : 0
                }
                response = await openai.chat_complete(self.api_key, 50, request_body)
                result = response.json()["choices"][0]["message"]["content"]
                return result
            except Exception as e:
                print(e)
                counter += 1

        try:
            traceback.print_exc()
            print(response.json())
        except:
            pass
        __import__('remote_pdb').set_trace()

