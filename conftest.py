import pytest
from poe_bot_but_better.test import BotTestHelper

@pytest.fixture(scope="function") # runs each test
def bot_helper() -> BotTestHelper:
    return BotTestHelper()
