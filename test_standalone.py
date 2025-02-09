import pytest
import fastapi_poe as fp
from poe_bot_but_better import poe_bot_but_better
from poe_bot_but_better.types import PoeBotError


@pytest.mark.asyncio
async def test_blank_bot(bot_helper):
    class DummyBot(fp.PoeBot):
        pass

    response = await bot_helper.send_message(DummyBot, "Hello")
    assert response == ""
    assert len(response.events) == 1 # default event in the Fastapi_Poe codebase

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
            
    with pytest.raises(PoeBotError, 
                      match="get_final_response is disabled in sync get_response. Use async get_response instead."):
        await bot_helper.send_message(SyncBotGetFinalResponse, "Hello")

    # sync generator
    @poe_bot_but_better
    class SyncBotStreamRequest:
        def get_response(self, stream_request):
            for part in stream_request("Hello", "GPT-4"):
                yield part
                return

    with pytest.raises(PoeBotError,
                      match="stream_request is disabled in sync get_response. Use async get_response instead."):
        await bot_helper.send_message(SyncBotStreamRequest, "Hello")

@pytest.mark.asyncio
async def test_none_bot(bot_helper):
    @poe_bot_but_better
    class NoneBot:
        async def get_response(self):
            return None

    response = await bot_helper.send_message(NoneBot, "Hello")
    assert response == ""