from typing import Any, AsyncGenerator, Awaitable, BinaryIO, Callable, Coroutine, List, Optional, Union
import fastapi_poe as fp
import httpx

RequestOrMessage = Union[str, fp.QueryRequest, fp.ProtocolMessage, List[fp.ProtocolMessage]]
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


    if isinstance(request_or_message, str):
        return create_query_request([fp.ProtocolMessage(role="user", content=request_or_message)])
    
    elif isinstance(request_or_message, list):
        if all(isinstance(item, fp.ProtocolMessage) for item in request_or_message):
            return create_query_request(request_or_message)
        raise ValueError("List must contain only ProtocolMessages")
    
    elif isinstance(request_or_message, fp.QueryRequest):
        return request_or_message
    
    elif isinstance(request_or_message, fp.ProtocolMessage):
        return create_query_request([request_or_message])
    
    raise ValueError(f"Request must be a string, list of strings, QueryRequest, or list of ProtocolMessages. Got: {request_or_message}")

def on_error(e, msg):
    print(msg)
    raise e

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
            
            # If it would up to me I would change these defaults
            on_error=on_error, # the errors being swallowed is a confusing
            num_tries=0, # spent a lot of time debugging why my code was executed twice, only to find out it was because of the retries
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
            # If it would up to me I would change these defaults
            on_error=on_error, # the errors being swallowed is a confusing
            num_tries=0, # spent a lot of time debugging why my code was executed twice, only to find out it was because of the retries
        ):
            yield message
            
    return stream_request

def create_post_message_attachment(bot: fp.PoeBot, request: fp.QueryRequest) -> Callable[..., Awaitable[None]]:
    message_id: str = request.message_id
    
    async def post_message_attachment(
        download_url: Optional[str] = None,
        file_data: Optional[Union[bytes, BinaryIO]] = None,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        is_inline: bool = False,
    ) -> None:
        await bot.post_message_attachment(download_url=download_url, file_data=file_data, filename=filename, content_type=content_type, is_inline=is_inline, message_id=message_id)
    
    return post_message_attachment