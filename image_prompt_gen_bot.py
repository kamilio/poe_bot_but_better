"""

Text bot creates a detailed art prompt and generates an image based on the prompt.

"""

from __future__ import annotations

from typing import AsyncIterable

import fastapi_poe as fp
from modal import App, Image, asgi_app
from poe_bot_but_better import poe_bot_but_better

IMAGE_PROMPT_GEN_PROMPT = "Create a detailed art prompt in this format: [subject], [artistic style], [lighting], [composition], [mood], [color palette], [additional details]. Focus on creating a cohesive visual scene that combines these elements while maintaining internal consistency. Make it specific enough to generate a clear image but leave room for artistic interpretation. Avoid conflicting elements or physically impossible combinations."

@poe_bot_but_better
class ImagePromptGenBot:
    async def get_response(
        self, messages: list[fp.ProtocolMessage], get_final_response,
    ):
        image_prompt = await get_final_response([fp.ProtocolMessage(role="system", content=IMAGE_PROMPT_GEN_PROMPT)] + messages, "Claude-3.5-Haiku")
        image = await get_final_response(image_prompt, "FLUX-pro-1.1")
        return image
    
    def get_settings(self) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"Claude-3.5-Haiku": 1, "FLUX-pro-1.1": 1})


REQUIREMENTS = ["fastapi-poe==0.0.48"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App("image-prompt-gen-bot-poe")


@app.function(image=image)
@asgi_app()
def fastapi_app():
    bot = ImagePromptGenBot()
    # see https://creator.poe.com/docs/quick-start#configuring-the-access-credentials
    # app = fp.make_app(bot, access_key=<YOUR_ACCESS_KEY>, bot_name=<YOUR_BOT_NAME>)
    app = fp.make_app(bot, allow_without_key=True)
    return app
