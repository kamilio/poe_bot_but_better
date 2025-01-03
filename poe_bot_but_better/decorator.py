import asyncio
import sse_starlette
from functools import wraps
from typing import AsyncIterable, Callable, Union, Optional, Dict, Any
from inspect import iscoroutinefunction, isgeneratorfunction, isasyncgenfunction
from poe_bot_but_better.client import create_get_final_response, create_stream_request, create_post_message_attachment
from .dependency_injection import solve_dependencies
import fastapi_poe as fp

def normalize_response(response: Union[str, fp.PartialResponse, sse_starlette.sse.ServerSentEvent]) -> Union[fp.PartialResponse, sse_starlette.sse.ServerSentEvent]:
    if isinstance(response, fp.PartialResponse):
        return response
    elif isinstance(response, str):
        return fp.PartialResponse(text=response)
    elif isinstance(response, sse_starlette.sse.ServerSentEvent):
        return response
    else:
        raise ValueError("Response must be a string or PartialResponse. Got: {}".format(response))

def poe_bot_but_better(cls):
    if not hasattr(cls, 'get_response'):
        raise ValueError(f"Class {cls.__name__} must implement get_response method")
        
    if not issubclass(cls, fp.PoeBot):
        class EnhancedBot(cls, fp.PoeBot):
            pass
        cls = EnhancedBot
    
    original_get_response = getattr(cls, 'get_response')
    original_get_settings = getattr(cls, 'get_settings', None)
    
    # Add class attribute for context override
    cls.dependency_injection_context_override = None
    
    async def get_response_impl(self, request: fp.QueryRequest) -> AsyncIterable[Union[fp.PartialResponse, sse_starlette.sse.ServerSentEvent]]:
        context = {
            "request": request,
            "messages": request.query,
            "bot_name": self.bot_name,
            
            # maybe remove these
            "get_final_response": create_get_final_response(request),
            "stream_request": create_stream_request(request),
            "post_message_attachment": create_post_message_attachment(self, request),
        }
        
        if self.dependency_injection_context_override:
            context.update(self.dependency_injection_context_override)

        dependencies = await solve_dependencies(original_get_response, context)
        
        # Call the original method
        if isasyncgenfunction(original_get_response):
            async for item in original_get_response(self, **dependencies):
                yield normalize_response(item)
        elif iscoroutinefunction(original_get_response):
            result = await original_get_response(self, **dependencies)
            yield normalize_response(result)
        elif isgeneratorfunction(original_get_response):
            for item in original_get_response(self, **dependencies):
                yield normalize_response(item)
        else:
            result = original_get_response(self, **dependencies)
            yield normalize_response(result)        

    async def get_settings_impl(self, request: fp.SettingsRequest) -> fp.SettingsResponse:
        result = fp.SettingsResponse()
        
        if not original_get_settings:
            return result 
            
        context = {
            "request": request,
            "setting": request,
            "bot_name": self.bot_name
        }
        
        if self.dependency_injection_context_override:
            context.update(self.dependency_injection_context_override)
        
        dependencies = await solve_dependencies(original_get_settings, context)
        
        if iscoroutinefunction(original_get_settings):
            result = await original_get_settings(self, **dependencies)
        else:
            result = original_get_settings(self, **dependencies)

        if isinstance(result, dict):
            result = fp.SettingsResponse(**result)

        return result

    cls.get_response = get_response_impl
    if original_get_settings:
        cls.get_settings = get_settings_impl

    # Todo: 
    #  - add `on_feedback`
    #  - merge the get_response_with_context and add to dependency injection context
    
    return cls