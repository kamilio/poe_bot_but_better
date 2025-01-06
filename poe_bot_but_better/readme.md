# Poe Bot API Suggestions

This document outlines proposals to improve the Poe Bot API, making it more intuitive and flexible while maintaining backward compatibility.

## Dependency Injection Framework

Implement FastAPI-style dependency injection for core bot functions, mainly for get_response and get_settings.

Key Dependencies (special cases matched on argument name)
- request
- messages (request.query is so confusing)
- bot_name (useful)
- get_final_response
- stream_request
- post_message_attachment

The dependency injection is a very powerful pattern and provides easy way to build extensions that can be shared across bots. 

Bonus: We could remove the functions get_response_with_context, that are not interesting for most of the users but cause mental overhead.

## Simplify bot calling - get_final_response / stream_request

Currently, when passing the request as argument, it's not immediately obvious what is the context of the current messsage. What context is the bot exactly getting. 

### Allow messages (string) instead of request
I propose to make the API flexible and support

- `str` simplest cases for building the prompt as string, converts to user message.
- `messages: List[fp.Message]` using `request.query` as an argument. It unlocks simpler interface e.g. `[prompt] + messages`

### Bake-in the auth token
Thanks to dependendency dependency this is easy to do. API users should not not worry about passing the token around. It's verbose and incraseas the cognitive load.

## Make get_response more flexible
Generators are advanced concept and it can be a bit intimidating to start with.

From my experience, the bots I created, are mashups of various LLMs, output is piped from one LLM to another, which makes streaming of responses impossible anyway. Therefore, add support for returning the final response instead of yielding would be useful.

Using PartialResponse is verbose and error prone (the error message is not helpful when mismatched), it would be beneficial to support `str`. 

## Add test helpers
Writing tests is hard, let's make it easier. 