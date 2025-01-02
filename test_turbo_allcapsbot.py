import pytest
from typing import AsyncGenerator, List
import fastapi_poe as fp
from turbo_allcapsbot import GPT35TurboAllCapsBot
from poe_bot_but_better.test import bot_helper
        

@pytest.mark.asyncio
async def test_example_bot_with_mock(bot_helper):
    # Mock responses
    turbo_mock = bot_helper.mock_bot("GPT-3.5-Turbo", [
        "Why did the scarecrow win an award?"
    ])
    
    response = await bot_helper.send_message(GPT35TurboAllCapsBot, "Tell me a joke")
    
    # Verify Claude was called
    turbo_mock.assert_called_once()

    # Verify we got Claude's last response
    assert response ==  "WHY DID THE SCARECROW WIN AN AWARD?"
    