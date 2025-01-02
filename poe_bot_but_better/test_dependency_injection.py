import pytest
from dataclasses import dataclass
from typing import Annotated

from poe_bot_but_better.dependency_injection import Depends, solve_dependencies, solve_dependencies_sync

@pytest.mark.asyncio
async def test_basic_dependency():
    def get_value():
        return 42

    async def target(value: Annotated[int, Depends(get_value)]):
        return value

    result = await solve_dependencies(target)
    assert result["value"] == 42

@pytest.mark.asyncio
async def test_nested_dependencies():
    def get_base():
        return 10

    def get_multiplier(base: Annotated[int, Depends(get_base)]):
        return base * 2

    async def target(
        value: Annotated[int, Depends(get_multiplier)]
    ):
        return value

    result = await solve_dependencies(target)
    assert result["value"] == 20

@pytest.mark.asyncio
async def test_context_override():
    def get_value():
        return 42

    async def target(value: Annotated[int, Depends(get_value)]):
        return value

    result = await solve_dependencies(target, context={"value": 100})
    assert result["value"] == 100

@pytest.mark.asyncio
async def test_async_dependency():
    async def get_async_value():
        return 42

    async def target(value: Annotated[int, Depends(get_async_value)]):
        return value

    result = await solve_dependencies(target)
    assert result["value"] == 42

@pytest.mark.asyncio
async def test_cache_dependency():
    call_count = 0
    
    def get_value():
        nonlocal call_count
        call_count += 1
        return 42

    async def target(
        value1: Annotated[int, Depends(get_value)],
        value2: Annotated[int, Depends(get_value)]
    ):
        return value1, value2

    result = await solve_dependencies(target)
    assert result["value1"] == 42
    assert result["value2"] == 42
    assert call_count == 1  # Should be called only once due to caching

@pytest.mark.asyncio
async def test_no_cache_dependency():
    call_count = 0
    
    def get_value():
        nonlocal call_count
        call_count += 1
        return 42

    async def target(
        value1: Annotated[int, Depends(get_value, use_cache=False)],
        value2: Annotated[int, Depends(get_value, use_cache=False)]
    ):
        return value1, value2

    result = await solve_dependencies(target)
    assert result["value1"] == 42
    assert result["value2"] == 42
    assert call_count == 2  # Should be called twice due to no caching

@pytest.mark.asyncio
async def test_dataclass_dependency():
    @dataclass
    class Config:
        name: str = "test"
        value: int = 42

    async def target(config: Config):
        return config

    result = await solve_dependencies(target)
    assert isinstance(result["config"], Config)
    assert result["config"].name == "test"
    assert result["config"].value == 42

def test_sync_wrapper():
    def get_value():
        return 42

    def target(value: Annotated[int, Depends(get_value)]):
        return value

    result = solve_dependencies_sync(target)
    assert result["value"] == 42