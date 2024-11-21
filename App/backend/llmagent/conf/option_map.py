from typing import Any, List
from pydantic import BaseModel

from .param import ItemParam, ListParam, SingleParam


class AgentOptionMap(BaseModel):
    agents: List[ItemParam]

    def clone_agent(self, index: int, agent_name: str):
        agent = self.agents[index]
        agent2 = agent.model_copy(deep=True)
        agent2.repr_name = agent_name
        self.agents.append(agent2)

    def update_agent_of_paths(self, value: Any, index: int, *paths: str | int):
        agent = self.agents[index]
        param = agent.construct_params[paths[0]]
        def __find_next_param(param, path):
            if isinstance(param, ItemParam):
                return param.get_param(path)
            if isinstance(param, ListParam):
                param = param.get_param()
                param = __find_next_param(param, path)
            return param

        for path in paths[1:]:
            if isinstance(param, SingleParam):
                raise ValueError(f"Invalid path {path} for {type(param)}")
            param = __find_next_param(param, path)

        assert isinstance(param, SingleParam) or isinstance(
            param, ListParam
        ), f"Invalid param {param} for value: {value}"
        param.select(value)

    def get_agent(self, index: int):
        return self.agents[index].get()
