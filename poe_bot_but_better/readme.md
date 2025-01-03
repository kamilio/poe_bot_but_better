# Poe Bot API Suggestions

This document outlines three key proposals to enhance the Poe Bot API, making it more intuitive and flexible while maintaining backward compatibility.

## Dependency Injection Framework

Implement FastAPI-style dependency injection for core bot functions, particularly get_response and get_settings.

Key Dependencies (special cases matched on argument name)
- request
- messages (request.query is so confusing)
- bot_name (useful)
- get_final_response
- stream_request
- post_message_attachment

The dependency injection is a very powerful pattern and provides easy way to build extensions that can be shared across bots. 

## Simplify get_final_response / stream_request

When passing the request along, it's not immediately obvious what is the context of the current messsage. What context is the bot exactly getting. 

### Allow messages (string) instead of request
I propose to make the API flexible and support

- `str` simplest cases for building the prompt as string, converts to user message.
- `messages: List[fp.Message]` just a rename of request.query, but it unlocks simpler interface e.g. `[prompt] + messages`

### Bake-in the auth token
Thanks to dependendency dependency this is easy to do. API users should not not worry about passing the token. 

## Make get_response more flexible - returning value, yield string
Generators are advanced concept and it can be a bit intimidating to start with.

From my experience, the bots I created, are mashups of various LLMs, output is piped from one LLM to another, which makes streaming of responses impossible anyway. Therefore, we could add support where instead of yielding, we return final message. 

Another addition is ability to yield string (or return string).

## Add test helpers
Writing tests is hard, let's make it easier. 