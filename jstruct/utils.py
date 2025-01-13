import typing
import logging
from dataclasses import is_dataclass, fields, asdict as dataclass_asdict
from typing import TypeVar, Type, Dict, Any

logger = logging.getLogger(__name__)
T = TypeVar('T')

def instantiate(class_: Type[T], args: dict) -> T:
    """Create an instance of a dataclass with only supported arguments"""
    if not is_dataclass(class_):
        return class_(**args)
        
    field_names = {f.name for f in fields(class_)}
    supported_args = {k: v for k, v in args.items() if k in field_names}
    unsupported_args = {k: v for k, v in args.items() if k not in field_names}

    if unsupported_args:
        logger.warning(f"unknown arguments {unsupported_args}")

    # Apply converters from field metadata
    for field_ in fields(class_):
        if field_.name in supported_args and 'converter' in field_.metadata:
            supported_args[field_.name] = field_.metadata['converter'](supported_args[field_.name])

    return class_(**supported_args)

def asdict(obj: Any) -> Dict:
    """Convert a dataclass instance to a dictionary"""
    if not is_dataclass(obj):
        return obj
    
    def _asdict_inner(obj):
        if is_dataclass(obj):
            result = {}
            for f in fields(obj):
                value = getattr(obj, f.name)
                result[f.name] = _asdict_inner(value)
            return result
        elif isinstance(obj, (list, tuple)):
            return [_asdict_inner(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: _asdict_inner(v) for k, v in obj.items()}
        else:
            return obj
            
    return _asdict_inner(obj)
