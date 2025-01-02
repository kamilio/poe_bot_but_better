from typing import Any, AsyncGenerator, Callable, List, Optional, Union
import fastapi_poe as fp
import httpx

RequestOrMessage = Union[str, List[str], fp.QueryRequest, fp.ProtocolMessage, List[fp.ProtocolMessage]]

def normalize_request(original_request: fp.QueryRequest, request_or_message: RequestOrMessage):
    if isinstance(request_or_message, str):
        return fp.QueryRequest(
            query=[fp.ProtocolMessage(role="user", content=request_or_message)],
            version=original_request.version,
            type=original_request.type,
            user_id=original_request.user_id,
            conversation_id=original_request.conversation_id,
            message_id=original_request.message_id,
            access_key=original_request.access_key
        )
    elif isinstance(request_or_message, list):
        if all(isinstance(item, str) for item in request_or_message):
            return fp.QueryRequest(
                query=[fp.ProtocolMessage(role="user", content=str(item)) for item in request_or_message],
                version=original_request.version,
                type=original_request.type,
                user_id=original_request.user_id,
                conversation_id=original_request.conversation_id,
                message_id=original_request.message_id,
                access_key=original_request.access_key
            )
        elif all(isinstance(item, fp.ProtocolMessage) for item in request_or_message):
            return fp.QueryRequest(
                query=[fp.ProtocolMessage(role="user", content=str(item)) if isinstance(item, str) else item for item in request_or_message],
                version=original_request.version,
                type=original_request.type,
                user_id=original_request.user_id,
                conversation_id=original_request.conversation_id,
                message_id=original_request.message_id,
                access_key=original_request.access_key
            )
        else:
            raise ValueError("List must contain only strings or ProtocolMessages")
    elif isinstance(request_or_message, fp.QueryRequest):
        return request_or_message
    elif isinstance(request_or_message, fp.ProtocolMessage):
        return fp.QueryRequest(
            query=[request_or_message],
            version=original_request.version,
            type=original_request.type,
            user_id=original_request.user_id,
            conversation_id=original_request.conversation_id,
            message_id=original_request.message_id,
            access_key=original_request.access_key
        )
    else:
        raise ValueError("Request must be a string, list of strings, QueryRequest, or list of ProtocolMessages. Got: {}".format(request_or_message))

def create_get_final_response(request: fp.QueryRequest):
    api_key: str = request.access_key
    async def get_final_response(
        request_or_message: fp.QueryRequest,
        bot_name: str,
        *,
        session: Optional[httpx.AsyncClient] = None,
        on_error: Any = None,
        num_tries: int = 2,
        retry_sleep_time: float = 0.5,
        base_url: str = "https://api.poe.com/bot/",
    ) -> str:
        # Apply any request modifications
        modified_request = normalize_request(request, request_or_message)
        
        # Call original function with pre-configured access key
        return await fp.get_final_response(
            request=modified_request,
            bot_name=bot_name,
            api_key=api_key,
            session=session,
            on_error=on_error,
            num_tries=num_tries,
            retry_sleep_time=retry_sleep_time,
            base_url=base_url
        )
    
    return get_final_response


def create_stream_request(request: fp.QueryRequest):
    api_key: str = request.access_key
    
    async def stream_request(
        request_or_message: RequestOrMessage,
        bot_name: str,
        *,
        tools: Optional[List[fp.ToolDefinition]] = None,
        tool_executables: Optional[List[Callable]] = None,
        session: Optional[httpx.AsyncClient] = None,
        on_error: Any = None,
        num_tries: int = 2,
        retry_sleep_time: float = 0.5,
        base_url: str = "https://api.poe.com/bot/",
    ) -> AsyncGenerator[fp.PartialResponse, None]:
        # Apply any request modifications
        modified_request = normalize_request(request, request_or_message)
        
        # Call original function with pre-configured access key
        async for message in fp.stream_request(
            request=modified_request,
            bot_name=bot_name,
            api_key=api_key,
            tools=tools,
            tool_executables=tool_executables,
            session=session,
            on_error=on_error,
            num_tries=num_tries,
            retry_sleep_time=retry_sleep_time,
            base_url=base_url
        ):
            yield message
            
    return stream_request