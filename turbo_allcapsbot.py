"""

Sample bot that wraps GPT-3.5-Turbo but makes responses use all-caps.

"""

from __future__ import annotations

from typing import AsyncIterable

import fastapi_poe as fp
from modal import App, Image, asgi_app
from poe_bot_but_better import poe_bot_but_better

@poe_bot_but_better
class GPT35TurboAllCapsBot:
    async def get_response(
        self, stream_request, messages,
    ) -> AsyncIterable[fp.PartialResponse]:
        async for msg in stream_request(
            messages, "GPT-3.5-Turbo"
        ):
            yield msg.text.upper()

    async def get_settings(self) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"GPT-3.5-Turbo": 1})