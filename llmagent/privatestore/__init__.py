from pathlib import Path
import pickle
from typing import Dict
from langchain_core.documents import Documents
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from loguru import logger
from pydantic import BaseModel, Field

class BaseConf(BaseModel):
    batch_size: int = Field(16, gt=1, description="请求embedding时的最大batch，和选择的LLM embeeding api有关")
    chunk_size: int = Field(300, gt=1, description="切分文档时，每个chunk的最大长度")
    chunk_overlap: int = Field(100, gt=1, description="切分文档时，每个chunk的重叠长度")

class BaseStore:
    def __init__(self, name:str, persist_path: str, emb_func:Embeddings, extra_config: BaseConf):
        self._name = name
        self._persist_path = persist_path
        self._emb_func = emb_func
        self._extra_config = extra_config
        self._vector_store = None
        self._documents_path = Path(persist_path) / "documents.bin"
        self._documents: Dict[str, Documents] = {}
        if self._documents_path.exists():
            with open(self._documents_path, "rb") as f:
                self._documents = pickle.load(f)

    def load(self):
        if not self.is_loaded():
            self.__download__()
            self.__load__()
    
    def __load__(self):
        """
        load document and construct vector store
        """
        documents = list(self._documents.values())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self._extra_config.chunk_size,
                                                       chunk_overlap=self._extra_config.chunk_overlap)
        splits = text_splitter.split_documents(documents)

        batch_size = self._extra_config.batch_size
        doc_ids = []
        for i in range(0, len(splits), batch_size):
            logger.info(f"Adding documents {i} to {i+batch_size}")
            texts = [doc.page_content for doc in splits[i:i+batch_size]]
            metadatas = [doc.metadata for doc in splits[i:i+batch_size]]
            doc_ids += self._vector_store.add_texts(texts, metadatas)
    
    def __download__(self):
        """
        download documents from remote server
        """
        raise NotImplementedError

    def is_loaded(self) -> bool:
        try:
            return (self._vector_store and 
                    self._vector_store._collection.count() > 0)
        except:
            return False
        
    def del_docment(self, key:str):
        self._documents.pop(key, None)
    
    def add_document(self, key:str, doc:Documents):
        self._documents[key] = doc
        
    def save_documents(self):
        with open(self._documents_path, "wb") as f:
            pickle.dump(self._documents, f)

    def __str__(self):
        return f"{self.__class__.__name__}({self._args}, {self._kwargs})"

    def __repr__(self):
        return str(self)