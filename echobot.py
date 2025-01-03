"""

Sample bot that echoes back messages.

This is the simplest possible bot and a great place to start if you want to build your own bot.

"""

import fastapi_poe as fp
from poe_bot_but_better import poe_bot_but_better

@poe_bot_but_better
class EchoBot:
    def get_response(self, messages: list[fp.ProtocolMessage]):
        return messages[-1].content