import sse_starlette
from typing import AsyncIterable, Union, Dict, Any
from inspect import iscoroutinefunction, isgeneratorfunction, isasyncgenfunction
from poe_bot_but_better.client import create_get_final_response, create_stream_request, create_post_message_attachment, disabled_fn
from .dependency_injection import solve_dependencies
import fastapi_poe as fp
from poe_bot_but_better.types import PoeBotError

def normalize_response(response: Union[str, fp.PartialResponse, sse_starlette.sse.ServerSentEvent]) -> Union[fp.PartialResponse, sse_starlette.sse.ServerSentEvent]:
    if isinstance(response, fp.PartialResponse):
        return response
    elif response is None:
        return fp.PartialResponse(text="")
    elif isinstance(response, str):
        return fp.PartialResponse(text=response)
    elif isinstance(response, sse_starlette.sse.ServerSentEvent):
        return response
    else:
        raise PoeBotError("Response must be a string or PartialResponse. Got: {}".format(response))

def poe_bot_but_better(cls):
    if not hasattr(cls, 'get_response'):
        raise PoeBotError(f"Class {cls.__name__} must implement get_response method")
        
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

            "get_final_response": create_get_final_response(request),
            "stream_request": create_stream_request(request),
            "post_message_attachment": create_post_message_attachment(self, request),
        }
        
        if self.dependency_injection_context_override:
            context.update(self.dependency_injection_context_override)
        
        # Call the original method
        if isasyncgenfunction(original_get_response):
            dependencies = await solve_dependencies(original_get_response, context)
            async for item in original_get_response(self, **dependencies):
                yield normalize_response(item)
        elif iscoroutinefunction(original_get_response):
            dependencies = await solve_dependencies(original_get_response, context)
            result = await original_get_response(self, **dependencies)
            yield normalize_response(result)
        elif isgeneratorfunction(original_get_response):
            context.update({
                "get_final_response": disabled_fn("get_final_response", "is disabled in sync get_response. Use async get_response instead."),
                "stream_request": disabled_fn("stream_request", "is disabled in sync get_response. Use async get_response instead."),
                "post_message_attachment": disabled_fn("post_message_attachment", "is disabled in sync get_response. Use async get_response instead."),
            })
            dependencies = await solve_dependencies(original_get_response, context)
            for item in original_get_response(self, **dependencies):
                yield normalize_response(item)
        else:
            context.update({
                "get_final_response": disabled_fn("get_final_response", "is disabled in sync get_response. Use async get_response instead."),
                "stream_request": disabled_fn("stream_request", "is disabled in sync get_response. Use async get_response instead."),
                "post_message_attachment": disabled_fn("post_message_attachment", "is disabled in sync get_response. Use async get_response instead."),
            })
            dependencies = await solve_dependencies(original_get_response, context)
            result = original_get_response(self, **dependencies)
            yield normalize_response(result)        

    async def get_settings_impl(self, request: fp.SettingsRequest) -> fp.SettingsResponse:
        result = fp.SettingsResponse()
        
        if not original_get_settings:
            return result 
            
        context = {
            "request": request,
            "setting": request,
            "bot_name": self.bot_name,

            # hand holding
            "get_final_response": disabled_fn("get_final_response", "is disabled in get_settings"),
            "stream_request": disabled_fn("stream_request", "is disabled in get_settings"),
            "post_message_attachment": disabled_fn("post_message_attachment", "is disabled in get_settings"),
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