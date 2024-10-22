from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate


class TemplateConf(BaseModel):
    context_num:int = Field(0, ge=0, description="context的数量")
    history_num:int = Field(0, ge=0, description="历史会话的数量")

class BaseTemplate:
    """
    在prompt中保存用户的聊天历史，并把最终的提示词输出到llm。
    """
    def __init__(self, conf:TemplateConf):
        self._conf = conf
        self._template: ChatPromptTemplate = None
        self._history: List[BaseMessage] = []
        self._current_human_question = ""
        pass

    def gen_prompt(self, context: str):
        def __runnable_lambda(question:str):
            self._current_human_question = question
            kwargs = dict(question=question)
            if self._conf.context_num > 0 and context:
                kwargs["context"] = context
            if self._conf.history_num > 0:
                kwargs["history"] = "\n".join([f"{message.type}: {message.content}" for message in self._history[-self._conf.history_num:]])
            return self._template.format_messages(**kwargs)
            
        return RunnableLambda(__runnable_lambda)
    
    def update_history(self):
        def __runnable_lambda(ans:str)
            if self._current_human_question and ans:
                self._history+=[HumanMessage(content=self._current_human_question),
                            AIMessage(content=ans)]
        return RunnableLambda(__runnable_lambda)
        
    