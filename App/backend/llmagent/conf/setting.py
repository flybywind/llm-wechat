import builtins
import importlib
from pydantic import BaseModel, computed_field
from typing import List, Tuple, Any, Type
from pathlib import Path
from .class_digestor import Scanner

ROOT_DIR = Path(__file__).resolve().parents[1]

_scanner = Scanner(ROOT_DIR)
class OptionSpec(BaseModel):
    readible_name: str
    param_name: str
    value: Any = None
    base_clazz: Type = None

    @computed_field
    def module_name(self) -> Tuple[str, str]:
        if self.base_clazz:
            return _scanner.get_class_module_path(self.base_clazz, self.param_name)
        return (None, None)


class Setting(BaseModel):
    name: str
    readible_name: str
    base_clazz: Type
    # option and its construct-options
    options: List[Tuple[OptionSpec, List[OptionSpec]]]

    _module_name: str = None
    _current_option: OptionSpec = None
    _construct_params: List[OptionSpec] = None

    def model_post_init(self, __context: Any) -> None:
        self._module_name, _ = _scanner.get_class_module_path(
            self.base_clazz, self.name
        )

    def select_option(self, index: int, **sub_option_kwargs):
        self._current_option, self._construct_params = self.options[index]
        for sub_option in self._construct_params:
            if sub_option.param_name in sub_option_kwargs:
                sub_option.value = sub_option_kwargs[sub_option.param_name]
        self._current_option.value = self.__build_sub_instance()

    def get_option(self, index: int):
        return self.options[index]

    def get_instance(self):
        kwargs = {opt[0].param_name: opt[0].value for opt in self.options}
        return self.__build_instance_from_module(self._module_name, self.name, kwargs)

    def __build_sub_instance(self):
        ## init instance by the module_name and the construct_params
        module_name, class_name = _scanner.get_class_module_path(
            self._current_option.base_clazz, self._current_option.param_name
        )
        kwargs = {opt.param_name: opt.value for opt in self._construct_params}
        return self.__build_instance_from_module(module_name, class_name, kwargs)

    def __build_instance_from_module(self, module_name: str, class_name: str, kwargs):
        if hasattr(builtins, class_name):
            return kwargs["value"]
        else:
            module = importlib.import_module(module_name)
            # 获取类对象
            cls = getattr(module, class_name)
            # 初始化类实例
            instance = cls(**kwargs)

            return instance
