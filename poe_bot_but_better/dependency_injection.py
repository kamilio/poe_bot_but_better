from dataclasses import is_dataclass
from typing import Any, Callable, Dict, Optional, Type, get_type_hints, Annotated
import inspect
from typing import get_args, get_origin
import asyncio
from functools import partial

class Depends:
    def __init__(
        self, 
        dependency: Optional[Callable] = None,
        use_cache: bool = True
    ) -> None:
        self.dependency = dependency or (lambda: None)
        self.use_cache = use_cache

async def solve_dependencies(
    func: Callable,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    context = context or {}
    params = {}
    
    # Handle bound methods by getting the underlying function
    if inspect.ismethod(func):
        func = func.__func__
    
    signature = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)
    
    cache: Dict[Callable, Any] = {}

    async def resolve_dependency(param_name: str, param: inspect.Parameter) -> Any:
        # Skip self/cls parameters
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and param_name in ('self', 'cls'):
            return None

        if param_name in context:
            return context[param_name]

        annotation = hints.get(param_name, param.annotation)
        
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            for arg in args:
                if isinstance(arg, Depends):
                    dependency = arg.dependency
                    if arg.use_cache and dependency in cache:
                        return cache[dependency]
                    
                    dep_params = await solve_dependencies(dependency, context)
                    
                    if inspect.iscoroutinefunction(dependency):
                        result = await dependency(**dep_params)
                    else:
                        result = dependency(**dep_params)
                    
                    if arg.use_cache:
                        cache[dependency] = result
                    return result

        if isinstance(param.default, Depends):
            dependency = param.default.dependency
            if param.default.use_cache and dependency in cache:
                return cache[dependency]
            
            dep_params = await solve_dependencies(dependency, context)
            
            if inspect.iscoroutinefunction(dependency):
                result = await dependency(**dep_params)
            else:
                result = dependency(**dep_params)
            
            if param.default.use_cache:
                cache[dependency] = result
            return result

        if param.default != inspect.Parameter.empty:
            return param.default

        if (is_dataclass(annotation) and 
            annotation != inspect.Parameter.empty and 
            isinstance(annotation, type)):
            
            class_signature = inspect.signature(annotation)
            dep_params = await solve_dependencies(annotation, context)
            return annotation(**dep_params)

        raise ValueError(f"Cannot resolve dependency for parameter {param_name}")

    # Resolve all dependencies concurrently
    resolved = await asyncio.gather(
        *(resolve_dependency(name, param) 
          for name, param in signature.parameters.items())
    )
    
    # Filter out None values (from self/cls parameters)
    params = {
        name: value 
        for name, value, param in zip(signature.parameters.keys(), resolved, signature.parameters.values())
        if not (param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and name in ('self', 'cls'))
    }
    
    return params

def solve_dependencies_sync(
    func: Callable,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return asyncio.run(solve_dependencies(func, context))