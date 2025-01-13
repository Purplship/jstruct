from dataclasses import dataclass, field, MISSING, fields
from functools import reduce
from typing import List, Dict, Union, Tuple, Optional, TypeVar, Any, Callable
import logging

import jstruct.utils as utils

logger = logging.getLogger(__name__)
REQUIRED = True

T = TypeVar('T')

def struct(cls):
    """Decorator that converts a class into a dataclass with JStruct functionality"""
    cls = dataclass(cls)
    original_init = cls.__init__

    def __init__(self, **kwargs):
        # Apply converters before initialization
        for field_ in fields(cls):
            if field_.name in kwargs and 'converter' in field_.metadata:
                kwargs[field_.name] = field_.metadata['converter'](kwargs[field_.name])
        original_init(self, **kwargs)

    cls.__init__ = __init__
    return cls

class _JStruct:
    """A typing definition wrapper used to define nested struct."""

    def __getitem__(
        self, arguments: Union[type, Tuple[type, Optional[bool], Optional[dict]]]
    ):
        class_, required_, *kwargs = (
            arguments if isinstance(arguments, tuple) else (arguments, False)
        )

        def converter(args) -> class_:
            if args is None and required_:
                raise TypeError(f"Missing required field of type {class_.__name__}")
            return utils.instantiate(class_, args) if isinstance(args, dict) else args

        if required_:
            return field(
                default=MISSING,
                metadata={'converter': converter}
            )
        else:
            return field(
                default=None,
                metadata={'converter': converter}
            )

class _JList:
    """A typing definition wrapper used to define nested collection (list) of struct."""

    def __getitem__(
        self, arguments: Union[type, Tuple[type, Optional[bool], Optional[dict]]]
    ):
        class_, required_, *kwargs = (
            arguments if isinstance(arguments, tuple) else (arguments, False)
        )

        def converter(args) -> List[class_]:
            if args is None:
                if required_:
                    raise TypeError(f"Missing required list field of type List[{class_.__name__}]")
                return []
                
            if isinstance(args, list):
                items = args
            else:
                items = [args]

            return [
                (utils.instantiate(class_, item) if isinstance(item, dict) else item) 
                for item in items
            ]

        if required_:
            return field(
                default=MISSING,
                metadata={'converter': converter}
            )
        else:
            return field(
                default_factory=list,
                metadata={'converter': converter}
            )

class _JDict:
    """A typing definition wrapper used to define nested dictionary struct typing."""

    def __getitem__(self, arguments: Tuple[type, type, Optional[bool], Optional[dict]]):
        key_type, value_type, required_, *kwargs = (
            arguments + (False,) if len(arguments) > 3 else arguments
        )

        def converter(args) -> Dict[key_type, value_type]:
            if args is None:
                if required_:
                    raise TypeError(f"Missing required dict field of type Dict[{key_type.__name__}, {value_type.__name__}]")
                return {}

            return {
                key_type(key): (
                    utils.instantiate(value_type, value)
                    if isinstance(value, dict) else value
                )
                for (key, value) in args.items()
            }

        if required_:
            return field(
                default=MISSING,
                metadata={'converter': converter}
            )
        else:
            return field(
                default_factory=dict,
                metadata={'converter': converter}
            )

# Instances
JStruct = _JStruct()
JList = _JList()
JDict = _JDict()
