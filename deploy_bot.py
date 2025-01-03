import os
from typing import Optional
from modal import App, Image, asgi_app, Secret
from prompt_bot import PromptBot
import fastapi_poe as fp

REQUIREMENTS = ["fastapi-poe==0.0.48"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App("poe-bot-poe")

# 1 Deploy the bot - modal server deploy_bot.py (copy the deployment URL - ends with .modal.run)
# 2 Create Poe bot - https://poe.com/create_bot?server=1 (copy access key)
access_key = ""
# 3 Set the name of the bot 
bot_name = ""
# 4 (optional) use Modal's secret https://modal.com/secrets/ and Secret.from_name
@app.function(image=image, secrets=[Secret.from_dict({"POE_BOT_ACCESS_KEY": access_key})])
@asgi_app()
def fastapi_app():
    bot = PromptBot(access_key=access_key, bot_name=bot_name)
    access_key = os.environ.get("POE_BOT_ACCESS_KEY")
    app = fp.make_app(bot, allow_without_key=(not access_key))
    return app
