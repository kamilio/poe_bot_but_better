import asyncio
from dataclasses import dataclass, field
from typing import Annotated, Any
from poe_bot_but_better import poe_bot_but_better
from poe_bot_but_better.dependency_injection import Depends
import json

@dataclass
class Config:
    decision_bot: str = "Claude-3-Haiku"
    bots: list[str] = field(default_factory=lambda: ["Claude-3-Haiku", "GPT-3.5-Turbo"])

def create_get_final_response_tuple(get_final_response):
    async def get_final_response_tuple(request, bot_name) -> tuple[str, str]:
        try:
            response = await get_final_response(request, bot_name)
            return bot_name, response
        except Exception as e:
            print(f"Error with bot {bot_name}: {e}")
            return bot_name, ""

    return get_final_response_tuple


@poe_bot_but_better
class BestResponseBot:
    async def get_response(
            self, 
            request, 
            get_final_response, 
            get_final_response_tuple: Annotated[Any, Depends(create_get_final_response_tuple)],
            config: Config
        ):
        responses = dict(await asyncio.gather(*(get_final_response_tuple(request, bot_name) for bot_name in config.bots)))
        prompt = "Which response is best? Output only the key from the json. Nothing else is permitted. \n\n"
        best_key = await get_final_response(prompt+json.dumps(responses, indent=4), config.decision_bot)
        print("Best key:", best_key)
        try:
            return responses[best_key]
        except KeyError:
            print("Key not found, returning first response. Key:", best_key)
            return responses[config.bots[0]]
    
    def get_settings(self, config: Annotated[Config, Depends()]):
        def count_strings(string_list):
            return {item: string_list.count(item) for item in set(string_list)}
        
        return {
            "server_bot_dependencies": count_strings(config.bots+[config.decision_bot])
        }