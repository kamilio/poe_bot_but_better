from poe_bot_but_better import poe_bot_but_better, Depends
from typing import Annotated, Awaitable, Callable
import hashlib


dummy_cache: dict = {}
def create_cache():
    return dummy_cache

GetFinalResponseCachedCallable = Callable[[str, str], Awaitable[str]]                                          
def create_cached_get_final_response(
        get_final_response, 
        cache: Annotated[dict, Depends(create_cache)]
    ) -> GetFinalResponseCachedCallable:
    async def get_final_response_cached(prompt, model):
        key = hashlib.md5((model+prompt).encode()).hexdigest()
        if key not in cache:
            cache[key] = await get_final_response(prompt, model)
        return cache[key]
    return get_final_response_cached

@poe_bot_but_better
class CachedBot: 
    async def get_response( # switch to async method
        self, 
        messages, 
        get_final_response_cached: Annotated[GetFinalResponseCachedCallable, Depends(create_cached_get_final_response)] 
    ): 
        last_message_text = messages[-1].content
        prompt = "Output only Black&white image\n" + last_message_text
        image = await get_final_response_cached(prompt, "FLUX-pro-1.1")
        return image

    def get_settings(self):
        return {
            "server_bot_dependencies": {
                "FLUX-pro-1.1": 1, 
            }
        }