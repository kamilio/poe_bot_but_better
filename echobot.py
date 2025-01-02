"""

Sample bot that echoes back messages.

This is the simplest possible bot and a great place to start if you want to build your own bot.

"""

from __future__ import annotations

from typing import AsyncIterable

import fastapi_poe as fp
from modal import App, Image, asgi_app
from poe_bot_but_better import poe_bot_but_better

@poe_bot_but_better
class EchoBot:
    def get_response(self, messages: list[fp.ProtocolMessage]):
        return messages[-1].content


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
