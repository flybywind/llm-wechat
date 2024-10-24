from langchain_core.outputs import GenerationChunk
from langchain.llms.base import LLM
from typing import Optional, List
from loguru import logger
import qianfan
from qianfan.resources.typing import QfRole

from . import model_spec as spec
    
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

    def model_post_init(self, ctx):
        self._model = qianfan.ChatCompletion()
        

    def _stream(self, prompt:str, stop: Optional[List[str]] = None, run_manager=None, **kwargs):
        """
        Handle a single round of the chat by using the current prompt and the previous context.
        """
        logger.debug(f"Prompt: {prompt}")
        resp = self._model.do(model=self.model_spec.name, 
                                messages=[{"role":QfRole.User.value, "content":prompt}],
                                stream=True,
                                temperature=self.temperature, 
                                penalty_score=self.penalty_score,
                                top_p=self.top_p, 
                                disable_search=self.disable_search,
                                max_output_tokens=self.max_output_tokens)
        for r in resp:
            body = r["body"]
            g = GenerationChunk(text=body["result"])
            if body["is_end"]:
               break
            yield g
                
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