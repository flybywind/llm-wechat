from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)
from langchain_core.outputs import GenerationChunk
from langchain_core.language_models.base import LanguageModelInput
from langchain.llms.base import LLM
from typing import Any, Iterator, Optional, List
from loguru import logger
from pydantic import Field
import qianfan
from qianfan.resources.typing import QfRole

from . import model_spec as spec

class QianfanLLM(LLM):
    model_spec: spec.LLMModelSpec
    # （1）较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定
    # （2）默认0.8，范围 (0, 1.0]，不能为0
    # temperature: float = Field(0.8, ge=0.0, le=1.0)
    # 通过对已生成的token增加惩罚，减少重复生成的现象。说明：
    # （1）值越大表示惩罚越大
    # （2）默认1.0，取值范围：[1.0, 2.0]
    penalty_score: float = 1.0
    # （1）影响输出文本的多样性，取值越大，生成文本的多样性越强
    # （2）默认0.8，取值范围 [0, 1.0]
    # 和temperature类似，建议只设置一个
    top_p: float = Field(0.8, ge=0.0, le=1.0)
    # 是否强制关闭实时搜索功能，
    enable_search: bool = False
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
        resp = self._model.do(
            model=self.model_spec.name,
            messages=[{"role": QfRole.User.value, "content": prompt}],
            stream=True,
            penalty_score=self.penalty_score,
            top_p=self.top_p,
            disable_search=(not self.enable_search),
            max_output_tokens=self.max_output_tokens,
        )
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


class QwenLLM(LLM):
    model_spec: spec.LLMModelSpec
    # 核采样的概率阈值，用于控制模型生成文本的多样性。
    # top_p越高，生成的文本更多样。反之，生成的文本更确定。
    # 取值范围：（0,1.0]
    # 由于temperature与top_p均可以控制生成文本的多样性，因此建议您只设置其中一个值。
    top_p: float = Field(0.8, ge=0.0, le=1.0)
    # 通过对已生成的token增加惩罚，减少重复生成的现象。说明：
    # （1）值越大表示惩罚越大
    # （2）默认1.0，取值范围：[-2.0, 2.0]
    presence_penalty: float = Field(1.0, ge=-2.0, le=2.0)
    # 是否强制关闭实时搜索功能，
    enable_search: bool = True
    max_tokens: int = 5000
    _model: OpenAI

    def model_post_init(self, ctx):
        self._model = OpenAI(
                    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                    # api_key=os.getenv("DASHSCOPE_API_KEY"),
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                )

    def stream(
        self,
        input: LanguageModelInput,
        config:  None,
        *,
        stop: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """
        Handle a single round of the chat by using the current prompt and the previous context.
        """
        mesg_list = []
        for m in input:
            if m.type == "system":
                mesg_list.append(
                    ChatCompletionSystemMessageParam(role="system", content=m.content)
                )
            elif m.type == "human":
                mesg_list.append(
                    ChatCompletionUserMessageParam(role="user", content=m.content)
                )
            elif m.type == "ai":
                mesg_list.append(
                    ChatCompletionAssistantMessageParam(
                        role="assistant", content=m.content
                    )
                )
            else:
                raise ValueError(f"unknown message type {m.type}")
        logger.debug(
            f"input after transform to ChatCompletionMessageParam: {mesg_list}"
        )
        completion = self._model.chat.completions.create(
            model=self.model_spec.name,
            messages=mesg_list,
            stream=True,
            top_p=self.top_p,
            presence_penalty=self.presence_penalty,
            max_tokens=self.max_tokens,
            extra_body={"enable_search": self.enable_search},
        )
        for ck in completion:
            ans = ck.choices[0].delta.content
            if ans:
                yield ans

    @property
    def _identifying_params(self) -> dict:
        """Parameters that uniquely identify the LLM."""
        d = self.__dict__.copy()
        d['model'] = self.model_spec.name
        return d

    @property
    def _llm_type(self) -> str:
        """Defines the LLM type."""
        return f"Qwen_{self.model_spec.name}"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        raise NotImplementedError("This method is not implemented.")


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
