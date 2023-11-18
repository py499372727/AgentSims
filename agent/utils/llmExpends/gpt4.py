from typing import List, Dict, Any
import os
import json
import openai_async as openai
from agent.utils.llmExpends.BasicCaller import BasicCaller

abs_path = os.path.dirname(os.path.realpath(__file__))

class GPT4Caller(BasicCaller):
    def __init__(self) -> None:
        self.model = "gpt-4"
        self.api_key = ""
        with open(os.path.join(abs_path, "..", "..", "..", "config", "api_key.json"), "r", encoding="utf-8") as api_file:
            api_keys = json.loads(api_file.read())
            self.api_key = api_keys["gpt-4"]
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
                    "temperature": 0
                }
                response = await openai.chat_complete(self.api_key, 50, request_body)
                print(response.text)
                result = response.json()["choices"][0]["message"]["content"]
                break
            except Exception as e:
                print(e)
                counter += 1
        return result
