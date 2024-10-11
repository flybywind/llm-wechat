from dataclasses import dataclass
from io import StringIO
from langchain.llms.base import LLM
import os
from typing import Generator, Optional, List
import qianfan
from secret import AK_SK

from . import model_spec as spec
from .role import Role

@dataclass
class QianfanLLM(LLM):
    api_key: str
    api_secret: str
    model_spec: spec.QianFanModel
    # （1）较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定
    # （2）默认0.8，范围 (0, 1.0]，不能为0
    temperature: float = 0.8
    # 通过对已生成的token增加惩罚，减少重复生成的现象。说明：
    # （1）值越大表示惩罚越大
    # （2）默认1.0，取值范围：[1.0, 2.0]
    penalty_score: float = 1.0
    # （1）影响输出文本的多样性，取值越大，生成文本的多样性越强
    # （2）默认0.8，取值范围 [0, 1.0]
    top_p: float = 1.0
    # 是否强制关闭实时搜索功能，
    disable_search: bool = False
    max_output_tokens: int = 1024
    history_len: int = 10
    max_content_len: int = 20000
    max_token_len: int = 1024

    def __init__(self, secret_file: str, model_spec: str = spec.Tiny8K,
                 temperature: float = 0.8,
                 penalty_score: float = 1.0, 
                 top_p: float = 1.0,
                 disable_search: bool = False,
                 max_output_tokens: int = 1024,
                 history_len: int = 10):
        ak_sk = AK_SK(secret_file)
        self.api_key = ak_sk.get_ak()
        self.api_secret = ak_sk.get_sk()
        self.model_spec = model_spec
        self.temperature = temperature
        self.penalty_score = penalty_score
        self.top_p = top_p
        self.disable_search = disable_search
        self.max_output_tokens = max_output_tokens
        self.history_len = history_len
        # take place globally
        os.environ["QIANFAN_ACCESS_KEY"] = self.api_key
        os.environ["QIANFAN_SECRET_KEY"] = self.api_secret

        self.model = qianfan.ChatCompletion()
        self.conversation_history = []  # List to maintain chat history
        self.conversation_str_len = []
        self.current_str_len = 0
        # todo, 看看超出有啥影响？
        # self.conversation_token_len = []
        # self.current_token_len = 0

    @property
    def llm_type(self) -> str:
        """Defines the LLM type."""
        return f"QianFan_{self.model_name}"

    def _stream(self, prompt: str, stop: Optional[List[str]] = None):
        """
        Handle a single round of the chat by using the current prompt and the previous context.
        """
        # Add the user's input to the conversation history
        self.conversation_history.append(dict(role=Role.U, content=prompt))
        self.conversation_str_len.append(len(prompt))
        self.current_str_len += self.conversation_str_len[-1]
        # truncate by max_content_len and max_token_len
        max_str_len = self.model_spec.max_str_len
        # max_token_len = self.model_spec.max_token_len

        start_i = max(0, len(self.conversation_history) - self.history_len)
        self.current_str_len -= sum(self.conversation_str_len[:start_i])
        self.conversation_history = self.conversation_history[start_i:]
        self.conversation_str_len = self.conversation_str_len[start_i:]
        # need truncate
        for i, sn in enumerate(self.conversation_str_len):
            if max_str_len > self.current_str_len:
                # and max_token_len > self.current_token_len:
                break
            self.current_str_len -= sn
            # self.current_token_len -= tn
            start_i = i
        if self.conversation_history[start_i]['role'] == Role.A:
            self.conversation_str_len -= self.conversation_str_len[start_i]
            # self.conversation_token_len -= self.conversation_token_len[start_i]
            start_i += 1
        self.conversation_history = self.conversation_history[start_i:] 
        # Call the model to get the response
        resp = self.model.do(model=self.model_name, 
                                messages=self.conversation_history,
                                stream=True,
                                temperature=self.temperature, 
                                penalty_score=self.penalty_score,
                                top_p=self.top_p, 
                                disable_search=self.disable_search,
                                max_output_tokens=self.max_output_tokens)
        full_ans = StringIO()
        for r in resp:
            body = r["body"]
            if body["is_end"]:
                this_content = full_ans.getvalue()
                full_ans.close()
                self.conversation_history.append(dict(role=Role.A, content=this_content))
                self.conversation_str_len.append(len(this_content))
                self.current_str_len += self.conversation_str_len[-1]
                # usage = body["usage"]
                # self.conversation_token_len.append(usage["prompt_tokens"])
                # self.conversation_token_len.append(usage["completion_tokens"])
            else:
                full_ans.write(body["result"])
            yield body["result"]
                
    @property
    def _identifying_params(self) -> dict:
        """Parameters that uniquely identify the LLM."""
        attrs = self.__dataclass_fields__.keys()
        d = {k: getattr(self, k) for k in attrs}
        return d

    def clear_history(self):
        """Clear the conversation history when starting a new conversation."""
        self.conversation_history = []
    