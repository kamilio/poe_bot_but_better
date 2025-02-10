# Poe Bot API Problems

This document outlines problems and proposals to improve the Poe Bot API, making it more intuitive and flexible while maintaining backward compatibility.

Note: User defined function `PoeBot.get_response()` should not to be confused with Poe API `fp.get_final_response()`. 

## 1. Async generators are a difficult concept to understand

Ask engineers to explain the concept of async generators. I bet 50% will not be able to explain it. The concept of generators is difficult enough, async just makes it harder. Seeing the keyword `yield` in code makes intimidating and less inviting to use the API.

### Solution
- Adjust the PoeBot.get_response() to allow for a simpler interface and optionally hide the complexity of async generators.

### How

To determine the type of the function, we can use `inspect.iscoroutinefunction(fn)`, `inspect.isgeneratorfunction(fn)` and `inspect.isasyncgenfunction(fn)`.

```python
# async generator
if isasyncgenfunction(fn):
    async for item in fn(*args, **kwargs):
        yield item
        
# async coroutine
elif iscoroutinefunction(fn):
    result = await fn(*args, **kwargs)
    yield result

# generator
elif isgeneratorfunction(fn):
    for item in fn(*args, **kwargs):
        yield item

# regular sync function        
else:  
    yield fn(*args, **kwargs)

```

Same logic can be applied to `get_settings()`.

As a bonus, we could remove the typing from `get_response()` and `get_settings()` as it has flexibility to support both sync and async. Anything returned should work. 

From my experience, the bots I created, are mashups of various LLMs, output is piped from one LLM to another, which makes streaming of responses impossible. Therefore, add support for returning the final response instead of yielding would be useful.

## 2. Yielding fp.FinalResponse(text=image) is verbose and error prone. 

When reading the code, the `yield fp.FinalResponse()` is oftentimes more prominent than the actual logic of the bot, `image` variable in this case or what is being streamed.

Note: When writing the code using LLMs, I frequently encountered LLM assuming that strings can be yielded. 

### Solution

Check for types and allow strings as well.

```python
if isinstance(item, str):
    yield fp.PartialResponse(text=item)
elif isinstance(item, fp.PartialResponse):
    yield item
else: # Improve on this error message
    raise ValueError(f"Unexpected item type: {type(item)}")
```

Bonus: Currently, the error message is not helpful when mismatched. It shows something like `Type doesn't have attribute 'text'`.

In conjunction with the previous solution, the API allows for much simpler and less intimidating interface.

```python
def get_response(self, request: fp.QueryRequest):
    return "Hello, world!"
```

## 3. When making a LLM request, it's not immediately obvious what is the context of the current query. Where is the prompt, where are the messages?

This is an example of the current interface. Try to read the code and try to figure out what is the context of the current query. 

```python
async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
    async for msg in fp.stream_request(request, "GPT-3.5-Turbo", request.access_key):
```

- Without reading the docs, code or types, it's not immediately obvious that `request` contains the messages. The naming `query` is even more unfortunate, as it contains the messages, `fp.ProtocolMessage`. 
- We can't expect API users to read the code or docs. Ideally, we would want API to be self-explanatory and understandable from examples.
- The duplication of the request object in the argument adds even more cognitive load and makes the code harder to read. 

### Solution

- Add argument `messages` to `get_response()`. Needs dependency injection to work well, see own section.
- Adjust `stream_request()` and `get_final_response()` to support `messages` argument as a shortcut for `QueryRequest(query=messages)` and ideally also string, for building the prompt as string.

```python
async for msg in fp.stream_request(messages, "GPT-3.5-Turbo"):
    ...

async for msg in fp.stream_request("Tell me a joke", "GPT-3.5-Turbo"):
    ...
```


## 4. Passing the access_key/api_key is verbose and increases the cognitive load

```python
async for msg in fp.stream_request(request, "GPT-3.5-Turbo", request.access_key):
```

### Solution

- Use dependency injection to provide stream_request, get_final_response and other API functions with the access_key baked in either via closure or partial application. 


```python
# factory function to create API with access_key baked in
def create_poe_functions(request):
  ...
  # closure
  def stream_request(context, bot_name):
    return fp.stream_request(context, bot_name, request.access_key)
  ...

  # alternatively, use partial application
  stream_request = partial(fp.stream_request, access_key=request.access_key)

  return {
    "stream_request": stream_request,
    ...
  }
```

Client usage:

```python
def get_response(self, messages: list[fp.ProtocolMessage], stream_request: Callable):
  async for msg in stream_request(messages, "GPT-3.5-Turbo"):
    ...
```

## 5. Testing bots in production is lengthy and error prone
Ideally users would be able to deploy bot into production and be relatively confident that they work. Most of the API users doesn't want to have different deployments, environments or bots for testing. And, it shouldn't be expected from them. 

### Solution
- Add unit test helpers and include them in the quick-start. Check unit tests in this project for examples.

It should be easy to test following cases:
- call bot with a message, multiple messages e.g. `response = await bot_helper.send_message(SuggestedRepliesBot, "Hello")`
- mock LLM responses e.g. `mock = bot_helper.mock_bot("Claude-3.5-Sonnet", ["Hi, ", "I am a bot"])`
- assert bot calls and bot responses e.g. `mock.assert_called_with_content("Hello")`


## Dependency Injection

Dependency injection is a powerful pattern, adds ability to extend the core functionality without causing breaking changes or increasing the complexity of the code. It also provides easy way to build extensions that can be shared across bots. Building dependency injection in python is surprisingly simple but also existing libraries could be considered.

Ideally, given we already use FastAPI, we could implement FastAPI-style dependency injection for core bot functions, mainly for get_response and get_settings.

Key Dependencies (special cases matched on argument name, without requiring explicit typing)
- request
- messages (request.query is confusing)
- bot_name (useful)
- context - from get_response_with_context

API Functions
- get_final_response
- stream_request
- post_message_attachment
- ... other Poe API functions