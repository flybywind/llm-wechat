from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import Runnable
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.retrievers import BaseRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain.llms.base import LLM
from langchain.vectorstores import VectorStore
from pydantic import BaseModel, Field
from typing import Any, List
from loguru import logger

class TemplateConf(BaseModel):
    context_num:int = Field(0, ge=0, description="context的数量")
    history_num:int = Field(0, ge=0, description="历史会话的数量")

class BaseTemplate(BaseModel):
    """
    这个模版不仅仅是提示提的模版，也包含了llm，retriever，vectorstore等必备的组件
    """
    llm: LLM
    conf: TemplateConf
    retriever: BaseRetriever
    vectorstore: VectorStore = None
    _template: ChatPromptTemplate = None
    _history: List[BaseMessage] = []
    _current_human_question = ""
    _langchain:Runnable = None

    def model_post_init(self, __context: Any) -> None:
        # 初始化模版, 构建langchain等操作
        raise NotImplementedError

    def gen_prompt(self):
        def __runnable_lambda(question:str, context: str):
            self._current_human_question = question
            kwargs = dict(question=question)
            if self._conf.context_num > 0 and context:
                kwargs["context"] = context
            if self._conf.history_num > 0:
                kwargs["history"] = self.get_history()
            return self._template.format_messages(**kwargs)
            
        return RunnableLambda(__runnable_lambda)
    
    def stream(self, question:str):
        ans = []
        try:
            for tok in self._langchain.stream(question):
                yield tok
                ans.append(tok)
            self._update_history(ans)
            self._current_human_question = ""
        except Exception as e:
            logger.exception(e)

    def get_history(self):
        return "\n".join([f"{message.type}: {message.content}" 
                        for message in self._history[-self._conf.history_num:]]) 
    def get_history_wo_role(self):
        return "\n".join([f"{message.content}" 
                        for message in self._history[-self._conf.history_num:]])
    def _update_history(self, ans:str):
        if self._current_human_question and ans:
            self._history+=[HumanMessage(content=self._current_human_question),
                        AIMessage(content=ans)]
        
    