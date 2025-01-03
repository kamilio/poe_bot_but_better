from __future__ import annotations

import os
from typing import AsyncIterable

import fastapi_poe as fp
from modal import App, Image, Mount, asgi_app

from poe_bot_but_better import poe_bot_but_better

@poe_bot_but_better
class VideoBot:
    async def get_response(
        self, request: fp.QueryRequest, post_message_attachment
    ):
        with open("/root/assets/tiger.mp4", "rb") as file:
            file_data = file.read()

        await post_message_attachment(file_data=file_data, filename="tiger.mp4")
        
        return "Attached a video."


REQUIREMENTS = ["fastapi-poe==0.0.48"]
image = (
    Image.debian_slim()
    .pip_install(*REQUIREMENTS)
    .env({"POE_ACCESS_KEY": os.environ["POE_ACCESS_KEY"]})
)
app = App(
    name="video-bot",
    image=image,
    mounts=[Mount.from_local_dir("./assets", remote_path="/root/assets")],
)


@app.function(
    image=image, mounts=[Mount.from_local_dir("./assets", remote_path="/root/assets")]
)
@asgi_app()
def fastapi_app():
    bot = VideoBot()
    POE_ACCESS_KEY = os.environ["POE_ACCESS_KEY"]
    # see https://creator.poe.com/docs/quick-start#configuring-the-access-credentials
    # app = fp.make_app(bot, access_key=POE_ACCESS_KEY, bot_name=<YOUR_BOT_NAME>)
    app = fp.make_app(bot, access_key=POE_ACCESS_KEY)
    return app
