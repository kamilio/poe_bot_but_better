"""

Sample bot that wraps Claude-3-Haiku but makes responses Haikus

"""

from typing import AsyncIterable

import fastapi_poe as fp

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


