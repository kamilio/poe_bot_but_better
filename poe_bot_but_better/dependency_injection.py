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
    signature = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)
    
    cache: Dict[Callable, Any] = {}

    async def resolve_dependency(param_name: str, param: inspect.Parameter) -> Any:
        # Check if parameter is in context
        if param_name in context:
            return context[param_name]

        annotation = hints.get(param_name, param.annotation)
        
        # Handle Annotated types
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

        # Handle direct Depends
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

        # Handle default values
        if param.default != inspect.Parameter.empty:
            return param.default

        # Handle dataclass instantiation
        if (is_dataclass(annotation) and 
            annotation != inspect.Parameter.empty and 
            isinstance(annotation, type)):  # ensure it's a class
            
            # Get signature from the class itself
            class_signature = inspect.signature(annotation)
            dep_params = await solve_dependencies(annotation, context)
            return annotation(**dep_params)

        raise ValueError(f"Cannot resolve dependency for parameter {param_name}")

    # Resolve all dependencies concurrently
    param_names = list(signature.parameters.keys())
    resolved_values = await asyncio.gather(
        *(resolve_dependency(name, signature.parameters[name]) for name in param_names)
    )
    
    params = dict(zip(param_names, resolved_values))
    return params

# Helper function for sync execution
def solve_dependencies_sync(
    func: Callable,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return asyncio.run(solve_dependencies(func, context))