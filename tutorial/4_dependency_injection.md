# Dependency injection and building a bot that caches LLM requests

LLMs are expensive and some prompts tends to be repeated so why not cache it. This is also useful for testing, so we don't blow through monthly points. 

Let's re-use the image bot to demonstrate the concept. We'll need a cache, let's just use python dict, on production you would want to use something else. Modal has the handy `modal.Dict.from_name` that is persistent. 

```python
dummy_cache: dict = {}
def create_cache():
    return dummy_cache
```

Then we wrap the get_final_response with the cache. Notice that we use factory functions for dependencies i.e. function returning a function. Classes work as well. 

```python 
from poe_bot_but_better import Depends
import hashlib
from typing import Annotated

def create_cached_get_final_response(
        get_final_response, # dependency injection (implicit by name)
        cache: Annotated[dict, Depends(create_cache)] # dependency injection of cache (explicit using Depends)
    ):
    async def get_final_response_cached(prompt, model):
        key = hashlib.md5((model+prompt).encode()).hexdigest() # has it just in case it's too long
        if key not in cache:
            cache[key] = await get_final_response(prompt, model)
        return cache[key]
    return get_final_response_cached
```

We can add types for the factory function return value, if we want to be really fancy
```python
from typing import Annotated, Awaitable, Callable

GetFinalResponseCachedCallable = Callable[[str, str], Awaitable[str]]                                          
def create_cached_get_final_response(
        get_final_response, 
        cache: Annotated[dict, Depends(create_cache)]
    ) -> GetFinalResponseCachedCallable:
```

Let's double check and make sure it works, the dependency injection makes testing very simple. 

```python
from unittest.mock import AsyncMock
import pytest
from poe_bot_but_better.test import bot_helper
from cached_bot import CachedBot, create_cached_get_final_response

@pytest.mark.asyncio
async def test_get_final_response_cached():
    cache = {}
    get_final_response = AsyncMock(side_effect=lambda prompt, bot_name: f"{prompt}-{bot_name}") # create mock original get final response
    
    get_final_response_cached = create_cached_get_final_response(get_final_response, cache)

    # miss
    response = await get_final_response_cached("Hello", "GPT-4")
    assert response == "Hello-GPT-4"
    get_final_response.assert_called_once_with("Hello", "GPT-4")
    
    # hit
    response = await get_final_response_cached("Hello", "GPT-4")
    assert response == "Hello-GPT-4"
    get_final_response.assert_called_once_with("Hello", "GPT-4")

    # miss 2nd
    response = await get_final_response_cached("Goodbye", "GPT-4")
    assert response == "Goodbye-GPT-4"
    assert get_final_response.call_count == 2

    # hit 2nd
    response = await get_final_response_cached("Hello", "GPT-4")
    assert response == "Hello-GPT-4"
    assert get_final_response.call_count == 2
```

Now that we have our cached get_final_response function, we can use it in our bot instead of the original.

```python
@poe_bot_but_better
class CachedBot: 
    async def get_response( # switch to async method
        self, 
        messages, 
        get_final_response_cached: Annotated[GetFinalResponseCachedCallable, Depends(create_cached_get_final_response)] # dependency injection
    ): 
        last_message_text = messages[-1].content
        prompt = "Output only Black&white image\n" + last_message_text
        image = await get_final_response_cached(prompt, "FLUX-pro-1.1") # use cached 
        return image

    def get_settings(self):
        # ... remains the same
```

And now let's verify by writing a unit test.

```python
@pytest.mark.asyncio
async def test_cached_bot_simple(bot_helper):
    mock = bot_helper.mock_bot("FLUX-pro-1.1", "image.jpg")
    response = await bot_helper.send_message(CachedBot, "Hello")

    assert response == "image.jpg"
    assert mock.call_count == 1
    

    # repeat the same message
    response = await bot_helper.send_message(CachedBot, "Hello")
    assert response == "image.jpg"
    assert mock.call_count == 1 
```