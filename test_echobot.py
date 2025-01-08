import pytest
from echobot import EchoBot
        
@pytest.mark.asyncio
async def test_echo_bot_simple(bot_helper):
    response = await bot_helper.send_message(EchoBot, "Hello")
    assert response == "HELLO"

@pytest.mark.asyncio
async def test_default_bot_settings(bot_helper):
    settings = await bot_helper.get_settings(EchoBot)
    assert settings.allow_attachments is None