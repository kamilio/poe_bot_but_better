# Streaming bot

The LLMs are often slow to get the full response, therefore we can stream the response as we receive it and do some tiny modifications. We'll uppercase the response from bot.

Again, re-using the already familiar concepts from previous lessons. 

The main concept here is python generators. The main difference from previous examples returning a value is that here we can return value multiple times. As the bot keeps sending message parts, we keep yielding (returning) them. 

```python
@poe_bot_but_better
class GPT35TurboAllCapsBot:
    async def get_response(
        self, stream_request, messages,
    ):
        async for msg in stream_request(
            messages, "GPT-3.5-Turbo" # we pass the whole context to the bot
        ):
            yield msg.text.upper()

    def get_settings(self):
        return {
            "server_bot_dependencies": {
                "GPT-3.5-Turbo": 1 # change dependency to text bot
            }
        }
```