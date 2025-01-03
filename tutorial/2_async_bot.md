# Async bot

In the previous chapter, we've built super simple bot, but in reality you might want to query database, LLM or any other asynchronous action. So let's do that! We'll query other bots on Poe. We'll be building on top of the EchoBot we created previously.

Let's get response from existing image generation bot but modify the original message (prompt) to turn the image black and white.  

Thanks to dependency injection we can access other useful functions such as `get_final_response` that queries any bot on Poe and gets the full response.


```python
from poe_bot_but_better import poe_bot_but_better


@poe_bot_but_better
class ImageGenBot: 
    async def get_response( # switch to async method
        self, 
        messages, 
        get_final_response # function provided by Poe API
    ): 
        last_message_text = messages[-1].content
        prompt = "Output only Black&white image\n" + last_message_text # merge two strings
        image = await get_final_response(prompt, "FLUX-pro-1.1")
        return image
```

Besides that we need to introduce brand new concept of settings and define our dependencies. Our dependency is the Image Generation bot.

```python
    def get_settings(self):
        return {
            "server_bot_dependencies": {
                "FLUX-pro-1.1": 1, 
            }
        }
```