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
    
@pytest.mark.asyncio
async def test_sync_bot(bot_helper):
    # sync function
    @poe_bot_but_better
    class SyncBotGetFinalResponse:
        def get_response(self, get_final_response, stream_request):
            response = get_final_response("Hello", "GPT-4")
            return response
    bot_helper.mock_bot("GPT-4", "Working")
    response = await bot_helper.send_message(SyncBotGetFinalResponse, "Hello")
    assert response == "Working"

    # sync generator
    @poe_bot_but_better
    class SyncBotStreamRequest:
        def get_response(self, stream_request):
            for part in stream_request("Hello", "GPT-4"):
                yield part

    response = await bot_helper.send_message(SyncBotStreamRequest, "Hello")
    assert response == "Working"