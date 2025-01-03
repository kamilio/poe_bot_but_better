"""

Sample bot that shows the query sent to the bot.

"""

from typing import List

import fastapi_poe as fp
from pprint import pformat


from poe_bot_but_better.decorator import poe_bot_but_better

@poe_bot_but_better
class LogBot:
    def get_response(self, messages: List[fp.ProtocolMessage]):
        return "```python\n" + pformat(messages) + "\n```"

    def get_settings(self) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            allow_attachments=True, 
            enable_image_comprehension=True
        )