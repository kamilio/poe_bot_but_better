import asyncio
from functools import wraps
from typing import AsyncIterable, Callable, Union
from inspect import iscoroutinefunction, isgeneratorfunction, isasyncgenfunction

from poe_bot_but_better.client import create_get_final_response, create_stream_request
from .dependency_injection import solve_dependencies
import fastapi_poe as fp

def normalize_response(response: Union[str, fp.PartialResponse]) -> fp.PartialResponse:
    if isinstance(response, fp.PartialResponse):
        return response
    elif isinstance(response, str):
        return fp.PartialResponse(text=response)
    else:
        raise ValueError("Response must be a string or PartialResponse. Got: {}".format(response))

def poe_bot_but_better(cls):
    # Check if PoeBot is already in the class's bases
    if not issubclass(cls, fp.PoeBot):
        # Create new class with PoeBot as parent if not already inherited
        class EnhancedBot(fp.PoeBot, cls):
            pass
        cls = EnhancedBot
    
    original_get_response = cls.get_response
    original_get_settings = cls.get_settings
    
    def get_response_wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def wrapped_to_async_generator(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
            context = {
                "self": self,
                "request": request,
                "messages": request.query,
                "bot_name": self.bot_name,
                
                # client methods (maybe remove and use Depends instead)
                "get_final_response": create_get_final_response(request),
                "stream_request": create_stream_request(request),
            }

            dependencies = await solve_dependencies(func, context)

            # Handle different types of functions
            if isasyncgenfunction(func):
                # Async generator
                async for item in func(**dependencies):
                    yield normalize_response(item)
                    
            elif iscoroutinefunction(func):
                # Async function
                result = await func(**dependencies)
                yield normalize_response(result)
                
            elif isgeneratorfunction(func):
                # Sync generator
                for item in func(**dependencies):
                    yield normalize_response(item)
                    
            else:
                # Sync function
                result = func(**dependencies)
                yield normalize_response(result)
                
        return wrapped_to_async_generator
    
    def get_settings_wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def wrapped_settings(self, request: fp.SettingsRequest) -> fp.SettingsResponse:
            context = {
                "self": self,
                "request": request,
                "bot_name": self.bot_name
            }
            
            dependencies = await solve_dependencies(func, context)
            
            # Since get_settings is an async function
            result = await func(**dependencies)
            return result
            
        return wrapped_settings

    cls.get_response = get_response_wrapper(original_get_response)
    cls.get_settings = get_settings_wrapper(original_get_settings)
    
    return cls