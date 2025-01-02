# Poe Bot API Suggestions

Following three concepts could make the API more concise and easier to understand, while maintaining backward compatibility. 

## Dependency injection for get_response and get_settings

Provide standard dependency injection similar fastapi `solve_dependencies` with special dependencies:
- request
- messages (request.query is so confusing)
- bot_name (useful)

The dependency injection is a very powerful pattern and provides easy way to build extensions that can be shared across bots. 

## get_final_response / stream_request changes

When passing the request along, it's no immediately obvious what is the context of the current messsage. What is the bot getting. 

### Allow messages (string) instead of request
I propose to make the API flexible and support

- `str` simplest cases for building the prompt as string, converts to user message
- `List[str]` similar to above, just array, nicer than concetanting strings
- `messages: List[fp.Message]` just a rename of request.query, but it unlocks simpler interface e.g. `[prompt] + messages`

### Bake-in the auth token
Thanks to dependendency this is easy to do. API users should not not worry about passing the token. 

## get_response can return string or yield multiple
Generators are advanced concept and it can be a bit intimidating to start with.

From my experience, the bots are created are mashups of various LLMs, output is piped from one LLM to another, which makes streaming of responses impossible. 




