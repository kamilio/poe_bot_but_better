import pytest
import fastapi_poe as fp
from typing import List
import asyncio

from poe_bot_but_better.client import create_get_final_response, create_stream_request, normalize_request

def test_normalize_request_string():
    # Create a sample original request
    original_request = fp.QueryRequest(
        query=[],
        version="1.0",
        type="query",
        user_id="test_user",
        conversation_id="test_conv",
        message_id="test_msg",
        access_key="test_key"
    )
    
    # Test with a simple string
    request = normalize_request(original_request, "Hello")
    
    assert isinstance(request, fp.QueryRequest)
    assert len(request.query) == 1
    assert request.query[0].role == "user"
    assert request.query[0].content == "Hello"
    assert request.version == original_request.version
    assert request.access_key == original_request.access_key

@pytest.mark.asyncio
async def test_create_get_final_response():
    # Create a sample request
    original_request = fp.QueryRequest(
        query=[],
        version="1.0",
        type="query",
        user_id="test_user",
        conversation_id="test_conv", 
        message_id="test_msg",
        access_key="test_key"
    )
    
    # Create the wrapped function
    get_final_response = create_get_final_response(original_request)
    
    # Mock the fastapi_poe.get_final_response function
    async def mock_get_final_response(*args, **kwargs):
        # Verify the access key was passed correctly
        assert kwargs['api_key'] == original_request.access_key
        # Verify the request was normalized
        assert isinstance(kwargs['request'], fp.QueryRequest)
        return "Mock response"
    
    # Temporarily replace the original function with our mock
    original_func = fp.get_final_response
    fp.get_final_response = mock_get_final_response
    
    try:
        # Test the wrapper
        response = await get_final_response(
            "Test message",
            "test_bot"
        )
        assert response == "Mock response"
        
    finally:
        # Restore the original function
        fp.get_final_response = original_func

@pytest.mark.asyncio
async def test_create_stream_request():
    # Create a sample request
    original_request = fp.QueryRequest(
        query=[],
        version="1.0",
        type="query",
        user_id="test_user",
        conversation_id="test_conv",
        message_id="test_msg",
        access_key="test_key"
    )
    
    # Create the wrapped function
    stream_request_func = create_stream_request(original_request)
    
    # Mock response messages
    mock_messages = [
        fp.PartialResponse(text="Hello"),
        fp.PartialResponse(text=" World")
    ]
    
    # Mock the fastapi_poe.stream_request function
    async def mock_stream_request(*args, **kwargs):
        # Verify the access key was passed correctly
        assert kwargs['api_key'] == original_request.access_key
        # Verify the request was normalized
        assert isinstance(kwargs['request'], fp.QueryRequest)
        for msg in mock_messages:
            yield msg
    
    # Temporarily replace the original function with our mock
    original_func = fp.stream_request
    fp.stream_request = mock_stream_request
    
    try:
        # Test the wrapper
        received_messages = []
        async for message in stream_request_func(
            "Test message",
            "test_bot"
        ):
            received_messages.append(message)
            
        # Verify we received all mock messages
        assert len(received_messages) == len(mock_messages)
        for received, expected in zip(received_messages, mock_messages):
            assert received.text == expected.text
            
    finally:
        # Restore the original function
        fp.stream_request = original_func