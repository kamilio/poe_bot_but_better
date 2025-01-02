"""

Sample bot that wraps Claude-3-Haiku but makes responses Haikus

"""

from __future__ import annotations

from typing import AsyncIterable

import fastapi_poe as fp
from modal import App, Image, asgi_app

SYSTEM_PROMPT = """
All your replies are Haikus.
""".strip()

from poe_bot_but_better import poe_bot_but_better, StreamRequestCallable

@poe_bot_but_better
class PromptBot:
    async def get_response(
        self, messages: list[fp.ProtocolMessage], stream_request: StreamRequestCallable
    ) -> AsyncIterable[fp.PartialResponse]:
        messages = [fp.ProtocolMessage(role="system", content=SYSTEM_PROMPT)] + messages
        async for msg in stream_request(messages, "Claude-3-Haiku"):
            yield msg

    def get_settings(self) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"Claude-3-Haiku": 1})


REQUIREMENTS = ["fastapi-poe==0.0.48"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App("prompt-bot-poe")


@app.function(image=image)
@asgi_app()
def fastapi_app():
    bot = PromptBot()
    # see https://creator.poe.com/docs/quick-start#configuring-the-access-credentials
    # app = fp.make_app(bot, access_key=<YOUR_ACCESS_KEY>, bot_name=<YOUR_BOT_NAME>)
    app = fp.make_app(bot, allow_without_key=True)
    return app
