import pytest
import fastapi_poe as fp
from poe_bot_but_better.test import bot_helper
from poe_bot_but_better import poe_bot_but_better


@pytest.mark.asyncio
async def test_blank_bot(bot_helper):
    class DummyBot(fp.PoeBot):
        pass

    response = await bot_helper.send_message(DummyBot, "Hello")
    assert response == ""
    assert len(response.events) == 1

@pytest.mark.asyncio
async def test_error_response_bot(bot_helper):
    @poe_bot_but_better
    class DummyBot:
        async def get_response(self):
            yield "Working"
            yield fp.ErrorResponse(text="Sad face", allow_retry=False)

    response = await bot_helper.send_message(DummyBot, "Hello")
    assert response == "Sad face"
    assert response.is_error is True
    assert response.versions[-1] == "Working" # previous version
    