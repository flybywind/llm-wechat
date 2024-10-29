from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import Runnable
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.retrievers import BaseRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain.llms.base import LLM
from langchain.vectorstores import VectorStore
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, List
from loguru import logger

class TemplateConf(BaseModel):
    context_num:int = Field(0, ge=0, description="context的数量")
    history_num:int = Field(0, ge=0, description="历史会话的数量")

class BaseChain(BaseModel):
    """
    这个模版不仅仅是提示提的模版，也包含了llm，retriever，vectorstore等必备的组件
    """
    llm: LLM
    conf: TemplateConf
    retriever: BaseRetriever = None
    vectorstore: VectorStore = None
    _template: ChatPromptTemplate = None
    _history: List[BaseMessage] = []
    _current_human_question = ""
    _langchain:Runnable = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
    def model_post_init(self, __context: Any) -> None:
        # 初始化模版, 构建langchain等操作
        raise NotImplementedError

    def gen_prompt(self):
        def __runnable_lambda(input):
            question = input["question"]
            context = input.get("context", None)
            self._current_human_question = question
            kwargs = dict(question=question)
            if self.conf.context_num > 0 and context:
                kwargs["context"] = context
            if self.conf.history_num > 0:
                kwargs["history"] = self.get_history()
            lc_msgs = self._template.format_messages(**kwargs)
            if self.llm._llm_type.startswith("QianFan_"):
                return "\n".join(m.content for m in lc_msgs)
            else:
                return lc_msgs

        return RunnableLambda(__runnable_lambda)

    def stream(self, question:str):
        ans = []
        try:
            for tok in self._langchain.stream(question):
                t = str(tok)
                yield t
                ans.append(t)
            self._update_history("".join(ans))
            self._current_human_question = ""
        except Exception as e:
            logger.exception(e)

    def invoke(self, question:str):
        return "".join(self.stream(question))

    def _get_history(self):
        return self._history[-self.conf.history_num*2:]

    def get_history(self):
        """
        用在prompt中，用来生成问题的context
        """
        return "\n".join([f"{message.type}: {message.content}" 
                        for message in self._get_history()])

    def get_history_wo_role(self):
        """
        可以用来做retriever的输入，召回更多有用的内容
        """
        return "\n".join(
            [
                f"{message.content}"
                for message in self._get_history()
                if message.type == "ai"
            ]
        )

    def _update_history(self, ans:str):
        if self._current_human_question and ans:
            self._history+=[HumanMessage(content=self._current_human_question),
                        AIMessage(content=ans)]
