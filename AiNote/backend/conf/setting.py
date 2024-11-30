import json
from pydantic import BaseModel, computed_field
from typing import List, Dict, Tuple, Any, Type, Union
from pathlib import Path
from .class_digestor import Scanner

ROOT_DIR = Path(__file__).resolve().parents[1]

_scanner = Scanner(ROOT_DIR)

# llmopt :
#     - qwen:
#         top_p: 0.8
#         model_spec: QwenPlus
#             - name: "qwen-plus1"
#             - name: "qwen-plus2"
#     - qianfan:
#         top_p: 0.8
# privatestore:
#     - confluence:
#         url: "https://confluence.com"
#         username: "admin"
#         root_page_id: 1
#         limit: 10
#     - web:
#         url: "https://web.com"
#         limit: 10

# chain:
#     - qa:
#         llm: qwen
#             - qwen
#             - qianfan
#         store: confluence


class SimpleOptionSpec(BaseModel):
    # 配置的唯一标识，人类可读
    readible_name: str
    base_clazz: Type
    value: Any
    # 如果value只有固定的几个值提供，那么这个字段应该是可枚举值的列表
    enum_values: List = []

    def model_post_init(self, __context: Any) -> None:
        # todo, 构造namedtuple
        pass

    def gen_value(self, value: Any = None):
        if value:
            self.value = value
        return self.value


class StructOptionSpec(BaseModel):
    # 配置的唯一标识，人类可读
    readible_name: str
    type: Type
    construct_params: Dict[str, SimpleOptionSpec]
    value: Any = None

    def gen_value(self, kwargs=None):
        if kwargs is None or len(kwargs) == 0:
            return self.value

        for key, opt in self.construct_params.items():
            if opt.readible_name in kwargs:
                opt.value = kwargs[opt.readible_name]
            else:
                raise ValueError(f"Invalid key {key}")
        self.value = self.type(**{k: v.value for k, v in self.construct_params.items()})
        return self.value


class ClassOptionSpec(BaseModel):
    # 配置的唯一标识，人类可读
    readible_name: str
    base_clazz: Type
    this_class_name: str
    construct_params: Dict[str, Union[StructOptionSpec, SimpleOptionSpec]]
    value: Any = None

    def model_post_init(self, __context: Any) -> None:
        _scanner.scan_base_class(self.base_clazz)

    @computed_field
    def this_class_type(self) -> Tuple[str, str]:
        return _scanner.get_class_type_of_name(self.base_clazz, self.this_class_name)

    def __update_construct_param(self, value: Any, readible_name: str):
        opt = self.construct_params.get(readible_name)
        if isinstance(opt, SimpleOptionSpec):
            opt.gen_value(value)
        else:
            if isinstance(value, dict):
                opt.gen_value(value)
            else:
                raise ValueError(
                    "Invalid value type for StructOptionSpec, expect a dict, but got: "
                    + str(type(value))
                )

    def gen_value(self, kwargs=None):
        if kwargs is None or len(kwargs) == 0:
            return self.value
        for key, value in kwargs.items():
            self.__update_construct_param(value, key)
        tp = self.this_class_type()
        self.value = tp(**{k: v.gen_value() for k, v in self.construct_params.items()})
        return self.value


class ComposeOptionSpec(ClassOptionSpec):
    # 构造时依赖哪些class的实例，key是构造函数的参数名，value是具体实例value
    construct_params: Dict[
        str, Union[ClassOptionSpec, StructOptionSpec, SimpleOptionSpec]
    ]


class Setting(BaseModel):
    # option and its construct-options
    options: List[ComposeOptionSpec]

    _current_option: ComposeOptionSpec = None
    _construct_params: Dict[str, Any] = {}

    def set_option(self, readible_name: str, kwargs: Dict[str, Any]):
        for opt in self.options:
            if opt.readible_name == readible_name:
                self._current_option = opt
                self._construct_params = kwargs
                break
        if self._current_option is None:
            raise ValueError("No such option")
        return self

    def get_instance(self):
        return self._current_option.gen_value(self._current_option)

    def save(self, json_path: str):
        with open(json_path, "w") as f:
            opt_list = [opt.model_dump() for opt in self.options]
            f.write(json.dumps(opt_list))

    @staticmethod
    def load(json_path: str):
        setting = Setting(options=[])
        with open(json_path, "r") as f:
            opt_list = json.loads(f.read())
            for param in opt_list:
                opt = ComposeOptionSpec(**param)
                setting.options.append(opt)
        return setting
