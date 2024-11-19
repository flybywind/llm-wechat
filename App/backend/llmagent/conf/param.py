from pydantic import BaseModel
from typing import Any, Dict, List, Union, Type


class BaseParam(BaseModel):
    # 用于显示的名称，人类可读
    repr_name: str
    # 参数name，用于构造函数
    name: str = ""
    value: Any = None
    # 参数含义解释
    description: str = ""

    def get(self):
        return self.value


class SingleParam(BaseParam):
    value: Any

    def select(self, value: Any):
        self.value = value
        return self


class ListParam(BaseParam):
    selections: List[Any]
    idx: int = 0

    def select(self, index: int):
        self.idx = index
        return self

    def get(self):
        v = self.selections[self.idx]
        if isinstance(v, BaseParam):
            return v.get()
        return v


class ItemParam(BaseParam):
    clazz_type: Type
    construct_param_dict: Dict[str, BaseParam]

    def select(self, key: str, value_or_index: Any):
        param = self.construct_param_dict[key]
        if isinstance(param, ListParam):
            assert isinstance(value_or_index, int)
        param.select(value_or_index)

    def get(self):
        return self.clazz_type(
            **{k: v.get() for k, v in self.construct_param_dict.items()}
        )
