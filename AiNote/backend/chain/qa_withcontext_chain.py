from typing import Any
from langchain_core.documents import Document

from .base import *

from .morehistory_retriever import MoreHistoryRetriever

class QAWithContextChain(BaseChain):
    def _format_docs(self, docs:List[Document]):
        return "\n\n".join(f"{d.page_content}\nsource: {d.metadata['source']}" for d in docs) 

    def model_post_init(self, __context: Any) -> None:
        assert self.documentstore is not None, "需要设置语料库"
        self.llm.top_p = 0.5
        self.retriever = MoreHistoryRetriever(
            vs=self.documentstore.vectorstore(), template=self
        )
        self._template = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个解答用户问题的assistant，可以根据context资料回答问题。请尽量保证回答的内容都可以在context中找到根据，并务必保留资料最后的 source。以下是context资料：\n{context}，\n以下是之前的聊天历史：\n{history}"),
                ("human", "问题：{question}"),
            ]
        )
        self._langchain =  (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.gen_prompt()
            | self.llm
            | StrOutputParser()
        )

    def get_history_wo_role(self):
        return "\n".join([f"{message.content}" 
                        for message in self._get_history() 
                        if message.type == "human"])
