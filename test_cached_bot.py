from unittest.mock import AsyncMock
import pytest
from cached_bot import CachedBot, create_cached_get_final_response

@pytest.mark.asyncio
async def test_get_final_response_cached():
    cache = {}
    get_final_response = AsyncMock(side_effect=lambda prompt, bot_name: f"{prompt}-{bot_name}")
    
    get_final_response_cached = create_cached_get_final_response(get_final_response, cache)

    # miss
    response = await get_final_response_cached("Hello", "GPT-4")
    assert response == "Hello-GPT-4"
    get_final_response.assert_called_once_with("Hello", "GPT-4")
    
    # hit
    response = await get_final_response_cached("Hello", "GPT-4")
    assert response == "Hello-GPT-4"
    get_final_response.assert_called_once_with("Hello", "GPT-4")

    # miss
    response = await get_final_response_cached("Goodbye", "GPT-4")
    assert response == "Goodbye-GPT-4"
    assert get_final_response.call_count == 2

    # hit
    response = await get_final_response_cached("Hello", "GPT-4")
    assert response == "Hello-GPT-4"
    assert get_final_response.call_count == 2
    

@pytest.mark.asyncio
async def test_cached_bot_simple(bot_helper):
    mock = bot_helper.mock_bot("FLUX-pro-1.1", "image.jpg")
    response = await bot_helper.send_message(CachedBot, "Hello")

    assert response == "image.jpg"
    assert mock.call_count == 1
    

    # repeat the same message
    response = await bot_helper.send_message(CachedBot, "Hello")
    assert response == "image.jpg"
    assert mock.call_count == 1
    