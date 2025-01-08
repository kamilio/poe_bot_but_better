# Simplest bot

Let's create the simplest bot possible on Poe. We'll be creating a bot that repeats whatever is sent to it and uppercases it. 


The first step is to create a class that defines a method get_response.

The get_response uses dependency injection and provides some special arguments such as
- `request: fp.QueryRequest`
- `messages: list[fp.ProtocolMessage]`
- ... and more later

The beauty of it is that you you can define the arguments that you need and they will be provided automatically.

We'll be accessing the context, all messages sent to and received by the bot, and retrieving the last message with index -1. The class `fp.ProtocolMessage` has a bunch of useful attributes, however we'll be using only `content`

```python
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
        
@pytest.mark.asyncio
async def test_echo_bot_simple(bot_helper): # fixture provided by pytest
    response = await bot_helper.send_message(EchoBot, "Hello")
    assert response == "HELLO"
```

Or deploy it to production by setting up the modal deploy script. We can re-use this script for our next iterations. 

deploy_bot.py
```python
from modal import App, Image, asgi_app
from poe_bot_but_better import poe_bot_but_better


REQUIREMENTS = ["fastapi-poe==0.0.48"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App("echobot-poe")


@app.function(image=image)
@asgi_app()
def fastapi_app():
    bot = EchoBot()
    # see https://creator.poe.com/docs/quick-start#configuring-the-access-credentials
    # app = fp.make_app(bot, access_key=<YOUR_ACCESS_KEY>, bot_name=<YOUR_BOT_NAME>)
    app = fp.make_app(bot, allow_without_key=True)
    return app
```