import pytest
import fastapi_poe as fp
from typing import Any, AsyncGenerator, List, Optional, Union
from dataclasses import dataclass, field
import uuid

import sse_starlette
from poe_bot_but_better import normalize_request, solve_dependencies
from unittest.mock import AsyncMock, MagicMock

class ResponseString(str):
    def __new__(cls, content):
        instance = super().__new__(cls, content)
        return instance
    
    def __init__(self, content):
        super().__init__()
        self.suggested_replies = []
        self.versions = []
        self.events = []
    
    def append_suggested_reply(self, suggested_reply: str):
        self.suggested_replies.append(suggested_reply)

    def append_event(self, event: sse_starlette.sse.ServerSentEvent):
        self.events.append(event)
    
    def replacemenet(self, new_content: str):
        new_string = ResponseString(new_content)
        new_string.versions.append(self)
        new_string.suggested_replies = self.suggested_replies
        return new_string
    
    def append(self, new_content: str):
        new_string = ResponseString(self + new_content)
        new_string.suggested_replies = self.suggested_replies
        new_string.versions = self.versions
        return new_string
        

mock_query_request = fp.QueryRequest(
    query=[],
    version="1.0",
    type="query",
    user_id="test_user",
    conversation_id="test_conv", 
    message_id="test_msg",
    access_key="test_key"
)

class AsyncQueryMock(AsyncMock):
    def __init__(self, bot_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_name = bot_name

    def inspect_calls(self):
        print(f"Mock: {self.bot_name}")
        for i, call in enumerate(self.call_args_list):
            print(f"Call {i}: args={call.args}, kwargs={call.kwargs}")

    def assert_called_with_content(self, content: str):
        call_requests = [normalize_request(mock_query_request, call.args[0]) for call in self.call_args_list]
        for call_args in call_requests:
            print("yo", call_args.query)
            for message in call_args.query:
                if message.content == content:
                    return
        output = [call_args.query[0].content for call_args in call_requests]
        new_line = "\n"
        raise AssertionError(f"Expected call with content '{content}' not found. Found: {new_line.join(output)}")

        

class BotTestHelper:
    def __init__(self):
        self.mocked_bots = {}
        self.responses = {}

    def mock_bot(self, bot_name: str, responses: Union[str, List[str]]):
        if isinstance(responses, str):
            responses = [responses]

        self.responses[bot_name] = responses
        mock = AsyncQueryMock(bot_name=bot_name)

        self.mocked_bots[bot_name] = mock
        return mock

    def _create_response_generator(self, responses: List[str]) -> AsyncGenerator[fp.PartialResponse, None]:
        async def generator():
            for response in responses:
                yield fp.PartialResponse(text=response)
        return generator()

    async def _get_final_response(self, request_or_message, bot_name: str, **kwargs) -> str:
        if bot_name not in self.responses:
            raise ValueError(f"Bot {bot_name} not mocked. Use bot_helper.mock_bot(\"{bot_name}\", \"response\")")
        self.mocked_bots[bot_name](request_or_message)
        return "".join(self.responses[bot_name])

    async def _stream_request(self, request_or_message, bot_name: str, **kwargs) -> AsyncGenerator[fp.PartialResponse, None]:
        if bot_name not in self.responses:
            raise ValueError(f"Bot {bot_name} not mocked. Use bot_helper.mock_bot(\"{bot_name}\", \"response\")")
        self.mocked_bots[bot_name](request_or_message)
        async for response in self._create_response_generator(self.responses[bot_name]):
            yield response

    async def send_message(self, bot_class, messages: List[Any]) -> str:
        bot_name = "TestBot"
        bot = bot_class(bot_name=bot_name)
        
        request = normalize_request(mock_query_request, messages)

        bot.dependency_injection_context_override = {
            "get_final_response": self._get_final_response,
            "stream_request": self._stream_request,
        }

        response = ResponseString("")
        async for part in bot.get_response(request):
            if isinstance(part, fp.PartialResponse):
                if part.is_replace_response:
                    response = response.replacemenet(part.text)
                elif part.is_suggested_reply:
                    response.append_suggested_reply(part.text)
                else:
                    response = response.append(part.text)
            # Not sure how is this used
            elif isinstance(part, sse_starlette.sse.ServerSentEvent):
                response.append_event(part)
            else:
                raise ValueError(f"Unexpected response type: {part}")
            
        return response
    
    async def get_settings(self, bot_class) -> fp.SettingsResponse:
        bot_name = "TestBot"
        bot = bot_class(bot_name=bot_name)
        request = fp.SettingsRequest(version="1", type="settings")
        return await bot.get_settings(request)

@pytest.fixture
def bot_helper():
    return BotTestHelper()

def bot_helper_wrong_usage(*args, **kwargs):
    raise ValueError("Use bot_helper fixture in your test: async def test_something(bot_helper): ...")

bot_helper.mock_bot = bot_helper_wrong_usage
bot_helper.send_message = bot_helper_wrong_usage
