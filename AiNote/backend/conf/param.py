import enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Union, Type


class ParamEnum(enum.Enum):
    Single = "S"
    List = "L"
    Item = "I"


class BaseParam(BaseModel):
    # 用于显示的名称，人类可读
    repr_name: str
    # 参数含义解释
    description: str = ""
    ptype: ParamEnum

class SingleParam(BaseParam):
    ptype: ParamEnum = Field(ParamEnum.Single)
    value: Any = None
    def select(self, value: Any):
        self.value = value

    def get(self):
        return self.value


class ListParam(BaseParam):
    ptype: ParamEnum = Field(ParamEnum.List)
    selections: List[Any]
    value: int = Field(0, ge=0)

    def select(self, index: int):
        assert isinstance(index, int), f"Invalid index {index} for ListParam: {self}"
        self.value = index

    def get(self):
        v = self.selections[self.value]
        if isinstance(v, BaseParam):
            return v.get()
        return v

    def get_param(self):
        p = self.selections[self.value]
        assert isinstance(p, BaseParam), f"Invalid param type {type(p)}"
        return p


class ItemParam(BaseParam):
    ptype: ParamEnum = Field(ParamEnum.Item)
    construct_params: Dict[str, Any]
    clazz_type: Type = Field(..., exclude=True)

    def select(self, key: str, value_or_index: Any):
        param = self.construct_params[key]
        if isinstance(param, ListParam):
            assert isinstance(
                value_or_index, int
            ), f"Invalid index {value_or_index} for ListParam: {param}"
        else:
            assert isinstance(param, SingleParam), f"Invalid param type {type(param)}"
        param.select(value_or_index)

    def get(self):
        return self.clazz_type(**{k: v.get() for k, v in self.construct_params.items()})

    def get_param(self, name):
        p = self.construct_params[name]
        assert isinstance(p, BaseParam), f"Invalid param type {type(p)}"
        return p
