from poe_bot_but_better import poe_bot_but_better, StreamRequestCallable
import fastapi_poe as fp

ACTIONS = ["Expand", "Condense", "Polish", "Simplify"]

@poe_bot_but_better
class SuggestedRepliesBot:
    async def get_response(self, request: fp.QueryRequest, stream_request: StreamRequestCallable):
        async for msg in stream_request(request, "Claude-3.5-Sonnet"):
            yield msg
        
        for action in ACTIONS:
            yield fp.PartialResponse(text=action, is_suggested_reply=True)

    def get_settings(self):
        return fp.SettingsResponse(server_bot_dependencies={"Claude-3.5-Sonnet": 1})