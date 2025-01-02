"""

Demo bot: catbot.

This bot uses all options provided by the Poe protocol. You can use it to get examples
of all the protocol has to offer.

"""

from __future__ import annotations

import asyncio
from typing import AsyncIterable, Literal

import fastapi_poe as fp
from modal import App, Image, asgi_app
from poe_bot_but_better import poe_bot_but_better

@poe_bot_but_better
class CatBot:
    async def get_response(
        self, messages: list[fp.ProtocolMessage]
    ):
        """Return an async iterator of events to send to the user."""
        last_message = messages[-1].content.lower()
        response_content_type: Literal["text/plain", "text/markdown"] = (
            "text/plain" if "plain" in last_message else "text/markdown"
        )
        yield fp.MetaResponse(
            text="",
            content_type=response_content_type,
            linkify=True,
            refetch_settings=False,
            suggested_replies="dog" not in last_message,
        )
        if "markdown" in last_message:
            yield "# Heading 1\n\n"
            yield "*Bold text* "
            yield "**More bold text**\n"
            yield "\n"
            yield "A list:\n"
            yield "- Item 1\n"
            yield "- Item 2\n"
            yield "- An item with [a link](https://poe.com)\n"
            yield "\n"
            yield "A table:\n\n"
            yield "| animal | cuteness |\n"
            yield "|--------|----------|\n"
            yield "| cat    | 10       |\n"
            yield "| dog    | 1        |\n"
            yield "\n"
        if "cardboard" in last_message:
            yield "crunch "
            yield "crunch"
        elif (
            "kitchen" in last_message
            or "meal" in last_message
            or "food" in last_message
        ):
            yield "meow "
            yield "meow"
            yield fp.PartialResponse(text="feed the cat", is_suggested_reply=True)
        elif "stranger" in last_message:
            for _ in range(10):
                yield fp.PartialResponse(text="peek ")
                await asyncio.sleep(1)
        elif "square" in last_message:
            yield fp.ErrorResponse(text="Square snacks are not tasty.")
        elif "cube" in last_message:
            yield fp.ErrorResponse(
                text="Cube snacks are even less tasty.", allow_retry=False
            )
        elif "count" in last_message:
            for i in range(1, 11):
                yield fp.PartialResponse(text=str(i), is_replace_response=True)
                if "quickly" not in last_message:
                    await asyncio.sleep(1)
        else:
            yield "zzz"

    async def on_feedback(self, feedback_request: fp.ReportFeedbackRequest) -> None:
        """Called when we receive user feedback such as likes."""
        print(
            f"User {feedback_request.user_id} gave feedback on {feedback_request.conversation_id}"
            f"message {feedback_request.message_id}: {feedback_request.feedback_type}"
        )

    async def get_settings(self) -> fp.SettingsResponse:
        """Return the settings for this bot."""
        return fp.SettingsResponse(
            allow_user_context_clear=True, allow_attachments=True
        )


REQUIREMENTS = ["fastapi-poe==0.0.48"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
app = App("catbot-poe")


@app.function(image=image)
@asgi_app()
def fastapi_app():
    bot = CatBot()
    # see https://creator.poe.com/docs/quick-start#configuring-the-access-credentials
    # app = fp.make_app(bot, access_key=<YOUR_ACCESS_KEY>, bot_name=<YOUR_BOT_NAME>)
    app = fp.make_app(bot, allow_without_key=True)
    return app
