import pytest
from typing import AsyncGenerator, List
import fastapi_poe as fp
from image_prompt_gen_bot import ImagePromptGenBot
from poe_bot_but_better.test import bot_helper
        

@pytest.mark.asyncio
async def test_image_prompt_gen_bot(bot_helper):
    prompt_gen_mock = bot_helper.mock_bot("Claude-3.5-Haiku", [
        "A meadow on a bright summer day.",
    ])

    image_gen_mock = bot_helper.mock_bot("FLUX-pro-1.1", [
        "image_placeholder",
    ])
    
    response = await bot_helper.send_message(ImagePromptGenBot, "Sunny day in June")
    
    prompt_gen_mock.assert_called_once()
    
    image_gen_mock.assert_called_once()
    image_gen_mock.assert_called_with_content("A meadow on a bright summer day.")
    
    assert response ==  "image_placeholder"
    