import pytest
from suggested_replies_bot import SuggestedRepliesBot
        
@pytest.mark.asyncio
async def test_echo_bot_simple(bot_helper):
    
    mock = bot_helper.mock_bot("Claude-3.5-Sonnet", ["Hi, ", "I am a bot"])
    response = await bot_helper.send_message(SuggestedRepliesBot, "Hello")

    assert mock.call_count == 1
    mock.assert_called_with_content("Hello")
    assert len(response.suggested_replies) == 4
    assert response.suggested_replies[0] == "Expand"
    assert response == "Hi, I am a bot"