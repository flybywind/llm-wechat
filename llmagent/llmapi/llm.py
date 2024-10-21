from io import StringIO
from langchain.llms.base import LLM
from typing import Optional, List
import qianfan

from . import model_spec as spec
from .role import Role
    
class QianfanLLM(LLM):
    model_spec: spec.LLMModelSpec
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
    # max_token_len: int = 1024
    _model: qianfan.ChatCompletion
    _conversation_history: List[dict]
    _conversation_str_len: List[int]
    _user_question_history: List[str]
    _current_str_len: int

    def model_post_init(self, ctx):
        self._model = qianfan.ChatCompletion()
        self._user_question_history = []
        self._conversation_history = []  # List to maintain chat history
        self._conversation_str_len = []
        self._current_str_len = 0
        # todo, 看看超出有啥影响？
        # self.conversation_token_len = []
        # self.current_token_len = 0

    def _stream(self, prompt: str, stop: Optional[List[str]] = None):
        """
        Handle a single round of the chat by using the current prompt and the previous context.
        """
        # Add the user's input to the conversation history
        self._conversation_history.append(dict(role=Role.U, content=prompt))
        self._conversation_str_len.append(len(prompt))
        self._current_str_len += self._conversation_str_len[-1]
        # truncate by max_content_len and max_token_len
        max_str_len = min(self.max_content_len, self.model_spec.max_str_len)
        # max_token_len = self.model_spec.max_token_len

        start_i = max(0, len(self._conversation_history) - self.history_len)
        self._current_str_len -= sum(self._conversation_str_len[:start_i])
        self._conversation_history = self._conversation_history[start_i:]
        self._conversation_str_len = self._conversation_str_len[start_i:]
        # need truncate
        for i, sn in enumerate(self._conversation_str_len):
            if max_str_len > self._current_str_len:
                # and max_token_len > self.current_token_len:
                break
            self._current_str_len -= sn
            # self.current_token_len -= tn
            start_i = i+1
        if self._conversation_history[start_i]['role'] == Role.A:
            self._current_str_len -= self._conversation_str_len[start_i]
            # self.conversation_token_len -= self.conversation_token_len[start_i]
            start_i += 1
        self._conversation_history = self._conversation_history[start_i:] 
        assert len(self._conversation_history) > 0 and self._conversation_history[-1]['role'] == Role.U
        # Call the model to get the response
        resp = self._model.do(model=self.model_spec.name, 
                                messages=self._conversation_history,
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
                self._conversation_history.append(dict(role=Role.A, content=this_content))
                self._conversation_str_len.append(len(this_content))
                self._current_str_len += self._conversation_str_len[-1]
                # usage = body["usage"]
                # self.conversation_token_len.append(usage["prompt_tokens"])
                # self.conversation_token_len.append(usage["completion_tokens"])
            else:
                full_ans.write(body["result"])
            yield body["result"]
                
    @property
    def _identifying_params(self) -> dict:
        """Parameters that uniquely identify the LLM."""
        d = self.__dict__.copy()
        d['model'] = self.model_spec.name
        return d

    @property
    def _llm_type(self) -> str:
        """Defines the LLM type."""
        return f"QianFan_{self.model_spec.name}"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the QianFan API to generate the response."""
        stream = self._stream(prompt, stop)
        return "".join(stream)
    
    @property
    def conversation_history(self):
        return self._conversation_history
    
    @property
    def user_question_history(self):
        return self._user_question_history
    
    def add_user_question(self, str):
        self._user_question_history.append(str)
    
    def clear_history(self):
        """Clear the conversation history when starting a new conversation."""
        self._conversation_history = []
        self._conversation_str_len = []
        self._user_question_history = []
        self._current_str_len = 0
    
class MyCustomLLM(LLM):
    some_param: str
    _a : int

    def model_post_init(self, ctx):
        print(f"Init MyCustomLLM with {self.some_param}, context: {ctx}")
        self._a = 1

    def _call(self, prompt, stop):
        # 这里实现你的自定义逻辑
        return "Generated response"

    @property
    def _identifying_params(self):
        return {"some_param": self.some_param}
    
    @property
    def _llm_type(self):
        return "MyCustomLLM"    