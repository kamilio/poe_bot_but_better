import pytest
import fastapi_poe as fp
from typing import AsyncIterable
from .decorator import poe_bot_but_better  # adjust import path as needed

# Mock messages for testing
mock_message = fp.ProtocolMessage(role="user", content="Hello, world!")
mock_messages = [mock_message]

# Test Bots
@poe_bot_but_better
class TestEchoBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        last_message = request.query[-1].content
        yield fp.PartialResponse(text=last_message)

    async def get_settings(self, request: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            allow_attachments=True,
            enable_image_comprehension=True
        )

@poe_bot_but_better
class TestSyncBot(fp.PoeBot):
    def get_response(self, request: fp.QueryRequest):
        last_message = request.query[-1].content
        return fp.PartialResponse(text=last_message)

    async def get_settings(self, request: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            allow_attachments=False,
            enable_image_comprehension=False
        )

# Tests
@pytest.mark.asyncio
async def test_echo_bot_response():
    bot = TestEchoBot()
    request = fp.QueryRequest(query=mock_messages, version="1", type="query", user_id="123", conversation_id="456", message_id="789")
    
    responses = []
    async for response in bot.get_response(request):
        responses.append(response)
    
    assert len(responses) == 1
    assert responses[0].text == "Hello, world!"

@pytest.mark.asyncio
async def test_echo_bot_settings():
    bot = TestEchoBot()
    request = fp.SettingsRequest(version="1", type="settings")
    
    response = await bot.get_settings(request)
    
    assert response.allow_attachments is True
    assert response.enable_image_comprehension is True

@pytest.mark.asyncio
async def test_sync_bot_response():
    bot = TestSyncBot()
    request = fp.QueryRequest(query=mock_messages, version="1", type="query", user_id="123", conversation_id="456", message_id="789")
    
    responses = []
    async for response in bot.get_response(request):
        responses.append(response)
    
    assert len(responses) == 1
    assert responses[0].text == "Hello, world!"

@pytest.mark.asyncio
async def test_sync_bot_settings():
    bot = TestSyncBot()
    request = fp.SettingsRequest(version="1", type="settings")
    
    response = await bot.get_settings(request)
    
    assert response.allow_attachments is False
    assert response.enable_image_comprehension is False

@pytest.mark.asyncio
async def test_dict_bot_settings():
    @poe_bot_but_better
    class TestDictBot(fp.PoeBot):
        async def get_response(self):
            pass

        async def get_settings(self):
            return {"allow_attachments": True, "enable_image_comprehension": True}
    
    bot = TestDictBot()
    request = fp.SettingsRequest(version="1", type="settings")
    
    response = await bot.get_settings(request)
    
    assert response.allow_attachments is True
    assert response.enable_image_comprehension is True

# Test for error handling
@poe_bot_but_better
class TestErrorBot(fp.PoeBot):
    async def get_response(self):
        raise ValueError("Test error")

    async def get_settings(self):
        raise ValueError("Test error")

@pytest.mark.asyncio
async def test_error_handling():
    bot = TestErrorBot()
    request = fp.QueryRequest(query=mock_messages, version="1", type="query", user_id="123", conversation_id="456", message_id="789")
    
    with pytest.raises(ValueError):
        async for _ in bot.get_response(request):
            pass