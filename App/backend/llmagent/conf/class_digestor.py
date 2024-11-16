import ast
import inspect
import importlib.util
from typing import Any, Dict, List, Tuple, Type
from collections import defaultdict
from pathlib import Path
from pydantic import BaseModel


def find_namedtuple_instances_with_names(file_path, target_namedtuple_name):
    """
    查找给定 namedtuple 类的所有实例及其变量名。

    参数:
        file_path (str): 目标 Python 文件路径。
        target_namedtuple_name (str): 要查找的 namedtuple 类名称。
    返回:
        list: 包含 (变量名, 参数列表) 的元组列表。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    # 解析 Python 文件为 AST
    tree = ast.parse(file_content)
    instances = []

    # 遍历 AST 节点
    for node in ast.walk(tree):
        # 查找赋值语句
        if isinstance(node, ast.Assign):
            # 检查赋值语句的值是否是目标 namedtuple 类的实例化
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == target_namedtuple_name
            ):
                # 获取赋值目标变量名
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variable_name = target.id
                        # 提取实例化的参数值
                        args = [ast.literal_eval(arg) for arg in node.value.args]
                        instances.append((variable_name, args))
    return instances


class Scanner:
    def __init__(self, directory: str):
        self.directory = directory
        self.base_class_dict = defaultdict(set)
        self.py_iterator = Path(directory).rglob("*.py")

    def get_class_module_path(
        self, base_class: Type, class_name: str
    ) -> Tuple[str, str]:
        if base_class not in self.base_class_dict:
            if base_class in {str, int, float, bool, list, set, tuple, dict}:
                return (None, base_class.__name__)

            for file in self.py_iterator:
                module_name = file.stem
                spec = importlib.util.spec_from_file_location(module_name, file)
                module = importlib.util.module_from_spec(spec)
                # 设置 __package__，假设文件在包 package 目录下
                if file.parent.name != ".":
                    parents = []
                    for parent in file.parents:
                        if parent.name == "llmagent":
                            parents.append("llmagent")
                            break
                        parents.append(parent.name)
                    module.__package__ = ".".join(reversed(parents))
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if is_subclass_of_base(obj, base_class):
                        self.base_class_dict[base_class].add((str(module), name))
        for module_path, class_name in self.base_class_dict[base_class]:
            if module_path.endswith("." + class_name):
                return (module_path, class_name)
        return (None, None)


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
