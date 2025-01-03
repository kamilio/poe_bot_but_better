import pytest
import fastapi_poe as fp
from typing import Any, AsyncGenerator, List, Optional
from dataclasses import dataclass, field
import uuid
from poe_bot_but_better import normalize_request, solve_dependencies
from unittest.mock import AsyncMock, MagicMock

mock_query_request = fp.QueryRequest(
    query=[],
    version="1.0",
    type="query",
    user_id="test_user",
    conversation_id="test_conv", 
    message_id="test_msg",
    access_key="test_key"
)

class BotTestHelper:
    def __init__(self):
        self.mocked_bots = {}
        self.responses = {}

    def mock_bot(self, bot_name: str, responses: List[str]):
        self.responses[bot_name] = responses
        mock = AsyncMock()
        self.mocked_bots[bot_name] = mock
        return mock

    def _create_response_generator(self, responses: List[str]) -> AsyncGenerator[fp.PartialResponse, None]:
        async def generator():
            for response in responses:
                yield fp.PartialResponse(text=response)
        return generator()

    async def _get_final_response(self, request_or_message, bot_name: str, **kwargs) -> str:
        if bot_name not in self.responses:
            raise ValueError(f"Bot {bot_name} not mocked")
        self.mocked_bots[bot_name](request_or_message)
        return "".join(self.responses[bot_name])

    async def _stream_request(self, request_or_message, bot_name: str, **kwargs) -> AsyncGenerator[fp.PartialResponse, None]:
        if bot_name not in self.responses:
            raise ValueError(f"Bot {bot_name} not mocked")
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

        response_parts = []
        async for part in bot.get_response(request):
            if isinstance(part, fp.PartialResponse):
                print(part.text)
                response_parts.append(part.text)
        return "".join(response_parts)
    
    async def get_settings(self, bot_class) -> fp.SettingsResponse:
        bot_name = "TestBot"
        bot = bot_class(bot_name=bot_name)
        request = fp.SettingsRequest(version="1", type="settings")
        return await bot.get_settings(request)

@pytest.fixture
def bot_helper():
    return BotTestHelper()
