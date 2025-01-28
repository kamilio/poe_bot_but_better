# Minor things I've encountered

- Assert that num_tries https://github.com/poe-platform/fastapi_poe/blob/1af6fb471a25bffc3f0470bb67981eeba2702aaf/src/fastapi_poe/client.py#L329 can't be 0. I've spend significant time debugging why my bot was not working. I was getting that bot didn't respond https://github.com/poe-platform/fastapi_poe/blob/1af6fb471a25bffc3f0470bb67981eeba2702aaf/src/fastapi_poe/client.py#L639 but the problem was the 0 tries. I think it's more conventional to have num_retries as an argument to the function, so I assumed that and wanted to turn of retries. 
- Assert yielding a PartialResponse for correct type. Otherwise, it will give confusing error message.
- Retries in general, it confused me so much, why is my bot called twice?  https://github.com/poe-platform/fastapi_poe/blob/1af6fb471a25bffc3f0470bb67981eeba2702aaf/src/fastapi_poe/client.py#L383
- Default error handler swallows the error. https://github.com/poe-platform/fastapi_poe/blob/1af6fb471a25bffc3f0470bb67981eeba2702aaf/src/fastapi_poe/client.py#L382 The problem is that it fails, and the bot running, incurring costs but being in a broken state.

# Architecture

- The function definitions are inconsistent. There's a mix of instance methods like post_message_attachment or auth/capture API and pure functions like get_final_response. 
- skip_system_prompt is on `QueryRequest`, which is really hard to find. It would be more predictable to be as an argument to get_final_response, stream_request

# Deployment

- The chicken-egg problem deploy first or create bot first.
    - The deployment script would update the API URL of the bot. No need to update it via UI.
    - Do not require the bot name, isn't the access_key enough to identify the bot? It would be nice to be able to change the bot name without a deployment.