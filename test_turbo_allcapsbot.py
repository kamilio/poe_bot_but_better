import pytest
from turbo_allcapsbot import GPT35TurboAllCapsBot
from poe_bot_but_better.test import bot_helper
        

@pytest.mark.asyncio
async def test_turbo_allcaps_bot(bot_helper):
    # Mock responses
    turbo_mock = bot_helper.mock_bot("GPT-3.5-Turbo", [
        "I tried yoga.\n"
        "Mat slipped.\n"
        "Now I'm pretzel.\n"
    ])
    
    response = await bot_helper.send_message(GPT35TurboAllCapsBot, "Tell me a joke")
    
    # Verify Claude was called
    turbo_mock.assert_called_once()
    turbo_mock.assert_called_with_content("Tell me a joke")

    # Verify we got Claude's last response
    assert response ==  """I TRIED YOGA.
MAT SLIPPED.
NOW I'M PRETZEL.
"""
    