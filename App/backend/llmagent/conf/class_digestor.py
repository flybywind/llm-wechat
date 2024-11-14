import os
import inspect
import importlib.util
from typing import Any, Dict, List, Type
from pathlib import Path
from pydantic import BaseModel


def is_subclass_of_base(cls: Type, base_class: Type) -> bool:
    return issubclass(cls, base_class) and cls is not base_class


def get_init_params(cls: Type) -> Dict[str, Any]:
    if issubclass(cls, BaseModel):
        return {name: field.annotation for name, field in cls.model_fields.items()}
    else:
        init_signature = inspect.signature(cls.__init__)
        return {
            name: param.annotation
            for name, param in init_signature.parameters.items()
            if name != "self"
        }


def resolve_param_type(param_type: Type, base_class: Type) -> Dict[str, Any]:
    if param_type in {int, float, str, bool, list, dict}:
        return param_type
    elif inspect.isclass(param_type) and is_subclass_of_base(param_type, base_class):
        return {param_type.__name__: get_class_init_params(param_type, base_class)}
    else:
        return str(param_type)


def get_class_init_params(cls: Type, base_class: Type) -> Dict[str, Any]:
    params = get_init_params(cls)
    resolved_params = {
        name: resolve_param_type(param_type, base_class)
        for name, param_type in params.items()
    }
    return resolved_params


def scan_subclasses(directory: str, base_class: Type) -> Dict[str, Any]:
    subclasses = {}

    for file in Path(directory).rglob("*.py"):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if is_subclass_of_base(obj, base_class):
                subclasses[name] = get_class_init_params(obj, base_class)

    return subclasses
