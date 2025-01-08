import pytest
from best_response_bot import BestResponseBot, Config
from conftest import BotTestHelper

@pytest.fixture
def config():
    return Config(bots=["Assistant", "GPT-3.5-Turbo", "Claude-3-Haiku"], decision_bot="Claude-3-Haiku")

@pytest.mark.asyncio
async def test_best_response_bot(bot_helper: BotTestHelper, config: Config):
    bot_helper.mock_bot("GPT-3.5-Turbo", "Hi!")
    bot_helper.mock_bot("Assistant", "Yo!")
    bot_helper.mock_bot("Claude-3-Haiku", "GPT-3.5-Turbo")
    response = await bot_helper.send_message(BestResponseBot, "Hello", dependency_injection_context_override={"config": config})
    assert response == "Hi!"

@pytest.mark.asyncio
async def test_best_response_wrong_decision(bot_helper: BotTestHelper, config: Config):
    bot_helper.mock_bot("GPT-3.5-Turbo", "Hi!")
    bot_helper.mock_bot("Assistant", "Yo!")
    bot_helper.mock_bot("Claude-3-Haiku", "NOT_EXISTENT_BOT")
    response = await bot_helper.send_message(BestResponseBot, "Hello", dependency_injection_context_override={"config": config})
    assert response == "Yo!"

# some bot errors out
@pytest.mark.asyncio
async def test_best_response_bot_error(bot_helper: BotTestHelper, config: Config):
    bot_helper.mock_bot("GPT-3.5-Turbo", "Hi!")
    bot_helper.mock_bot("Assistant", lambda *args, **kwargs: 1/0)
    bot_helper.mock_bot("Claude-3-Haiku", "GPT-3.5-Turbo")
    response = await bot_helper.send_message(BestResponseBot, "Hello", dependency_injection_context_override={"config": config})
    assert response == "Hi!"
    

@pytest.mark.asyncio
async def test_settings(bot_helper: BotTestHelper, config: Config):
    settings = await bot_helper.get_settings(BestResponseBot, dependency_injection_context_override={"config": config})
    assert settings.server_bot_dependencies == {"Assistant": 1, "GPT-3.5-Turbo": 1, "Claude-3-Haiku": 2}