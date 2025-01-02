from typing import Any, AsyncGenerator, Callable, Coroutine, List, Optional, Union
import fastapi_poe as fp
import httpx

RequestOrMessage = Union[str, List[str], fp.QueryRequest, fp.ProtocolMessage, List[fp.ProtocolMessage]]
StreamRequestCallable = Callable[
    [RequestOrMessage, str],
    AsyncGenerator[fp.PartialResponse, None]
]

GetFinalResponseCallable = Callable[
    [RequestOrMessage, str], 
    Coroutine[Any, Any, str]
]

def normalize_request(original_request: fp.QueryRequest, request_or_message: RequestOrMessage):
    def create_query_request(query):
        return fp.QueryRequest(
            query=query,
            version=original_request.version,
            type=original_request.type,
            user_id=original_request.user_id,
            conversation_id=original_request.conversation_id,
            message_id=original_request.message_id,
            access_key=original_request.access_key
        )

    def create_protocol_message(content):
        return fp.ProtocolMessage(role="user", content=content)

    if isinstance(request_or_message, str):
        return create_query_request([create_protocol_message(request_or_message)])
    
    elif isinstance(request_or_message, list):
        if all(isinstance(item, str) for item in request_or_message):
            return create_query_request([create_protocol_message(item) for item in request_or_message])
        elif all(isinstance(item, fp.ProtocolMessage) for item in request_or_message):
            query = [create_protocol_message(item) if isinstance(item, str) else item for item in request_or_message]
            return create_query_request(query)
        raise ValueError("List must contain only strings or ProtocolMessages")
    
    elif isinstance(request_or_message, fp.QueryRequest):
        return request_or_message
    
    elif isinstance(request_or_message, fp.ProtocolMessage):
        return create_query_request([request_or_message])
    
    raise ValueError(f"Request must be a string, list of strings, QueryRequest, or list of ProtocolMessages. Got: {request_or_message}")

def create_get_final_response(request: fp.QueryRequest) -> GetFinalResponseCallable:
    api_key: str = request.access_key
    async def get_final_response(
        request_or_message: RequestOrMessage,
        bot_name: str,
    ) -> str:
        # Apply any request modifications
        modified_request = normalize_request(request, request_or_message)
        
        # Call original function with pre-configured access key
        return await fp.get_final_response(
            request=modified_request,
            bot_name=bot_name,
            api_key=api_key,
        )
    
    return get_final_response


def create_stream_request(request: fp.QueryRequest) -> StreamRequestCallable:
    api_key: str = request.access_key
    
    async def stream_request(
        request_or_message: RequestOrMessage,
        bot_name: str,
    ) -> AsyncGenerator[fp.PartialResponse, None]:
        # Apply any request modifications
        modified_request = normalize_request(request, request_or_message)
        
        # Call original function with pre-configured access key
        async for message in fp.stream_request(
            request=modified_request,
            bot_name=bot_name,
            api_key=api_key,
        ):
            yield message
            
    return stream_request