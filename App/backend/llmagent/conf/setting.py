from pydantic import BaseModel, computed_field
from typing import List, Tuple, Any, Type
from pathlib import Path
from .class_digestor import scan_class_module_path

ROOT_DIR = Path(__file__).resolve().parent(2)


class OptionSpec(BaseModel):
    readible_name: str
    param_name: str
    value: Any
    clazz: Type = None

    @computed_field
    def module_name(self):
        if self.clazz:
            return scan_class_module_path(ROOT_DIR, self.clazz)
        return ""


class Setting(BaseModel):
    name: str
    # option and its construct-options
    options: List[Tuple[OptionSpec, List[OptionSpec]]]

    _current_option: OptionSpec = None
    _construct_params: List[OptionSpec] = None

    def select_option(self, index: int, **sub_option_kwargs):
        self._current_option, self._construct_params = self.options[index]
        for sub_option in self._construct_params:
            setattr(self, sub_option.param_name, sub_option.value)

    # def build_instance(self, **kwargs):
    #     return self.__class__(**kwargs)
