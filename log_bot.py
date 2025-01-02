"""

Sample bot that shows the query sent to the bot.

"""

from __future__ import annotations

from typing import AsyncIterable, List

import fastapi_poe as fp
from devtools import PrettyFormat
from modal import App, Image, asgi_app

from poe_bot_but_better.decorator import poe_bot_but_better

pformat = PrettyFormat(width=85)

@poe_bot_but_better
class LogBot:
    async def get_response(
        self, messages: List[fp.ProtocolMessage]
    ) -> AsyncIterable[fp.PartialResponse]:
        yield "```python\n" + pformat(messages) + "\n```"

    def get_settings(self) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            allow_attachments=True, enable_image_comprehension=True
        )


REQUIREMENTS = ["fastapi-poe==0.0.48", "devtools==0.12.2"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App("log-bot-poe")


@app.function(image=image)
@asgi_app()
def fastapi_app():
    bot = LogBot()
    # see https://creator.poe.com/docs/quick-start#configuring-the-access-credentials
    # app = fp.make_app(bot, access_key=<YOUR_ACCESS_KEY>, bot_name=<YOUR_BOT_NAME>)
    app = fp.make_app(bot, allow_without_key=True)
    return app
