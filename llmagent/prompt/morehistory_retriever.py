from langchain_core.retrievers import BaseRetriever
from langchain.vectorstores import VectorStore

from .base import BaseTemplate
class MoreHistoryRetriever(BaseRetriever):
    vs: VectorStore
    template: BaseTemplate

    def _get_relevant_documents(
        self, chat_str: str, *, run_manager):
        return self.vs.similarity_search(self.template.get_history_wo_role()+"\n"+chat_str,
                                         k=self.template.conf.context_num)