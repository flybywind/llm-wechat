from typing import Any, List
from pydantic import BaseModel

from .param import ItemParam, ListParam, SingleParam


class AgentOptionMap(BaseModel):
    agents: List[ItemParam]

    def clone_agent(self, index: int, agent_name: str):
        agent = self.agents[index]
        agent2 = ItemParam(**agent.model_dump())
        agent2.repr_name = agent_name
        self.agents.append(agent2)

    def update_agent(self, value: Any, index: int, *paths: str | int):
        agent = self.agents[index]
        param = agent.construct_param_dict[paths[0]]
        for path in paths[1:]:
            if isinstance(param, ItemParam):
                param = param.select(path, value)
            else:
                if isinstance(param, ListParam):
                    assert isinstance(path, int)
                param = param.select(path)

    def get_agent(self, index: int):
        return self.agents[index].get()
