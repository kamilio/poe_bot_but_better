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
    def get_response(self, messages: List[fp.ProtocolMessage]):
        return "```python\n" + pformat(messages) + "\n```"

    def get_settings(self) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            allow_attachments=True, 
            enable_image_comprehension=True
        )