# Simplest bot

Let's create the simplest bot possible on Poe. We'll be creating a bot that repeats whatever is sent to it and uppercases it. 


The first step is to create a class that defines a method get_response.

The get_response uses dependency injection and provides these arguments
- `request: fp.QueryRequest`
- `messages: list[fp.ProtocolMessage]`
We'll be accessing the context, all messages sent to and received by the bot, and retrieving the last message with index -1. The `fp.ProtocolMessage` has a bunch of useful attributes, however we'll be using only `content`

```python
import fastapi_poe as fp
from poe_bot_but_better import poe_bot_but_better


@poe_bot_but_better
class EchoBot:
    def get_response(self, messages):
        last_message_text = messages[-1].content
        return last_message_text.upper()
```        


Let's write a test to make sure the bot works. 

```python
import pytest
from echobot import EchoBot
from poe_bot_but_better.test import bot_helper
        
@pytest.mark.asyncio
async def test_echo_bot_simple(bot_helper):
    response = await bot_helper.send_message(EchoBot, "Hello")
    assert response == "HELLO"
```

Or deploy it to production