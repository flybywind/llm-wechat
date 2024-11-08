from pathlib import Path
import pickle
from typing import Dict
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from loguru import logger
from pydantic import BaseModel, Field
from typing import List, Dict, Set

class BaseConf(BaseModel):
    batch_size: int = Field(256, gt=1, description="请求embedding时的最大batch")
    chunk_size: int = Field(300, gt=1, description="切分文档时，每个chunk的最大长度")
    chunk_overlap: int = Field(100, gt=1, description="切分文档时，每个chunk的重叠长度")

class BaseStore:
    def __init__(self, name:str, persist_path: str, emb_func:Embeddings, extra_config: BaseConf):
        self._name = name
        self._persist_path = persist_path
        self._emb_func = emb_func
        self._extra_config = extra_config
        self._documents_path = Path(persist_path) / "documents.bin"
        self._documents: Dict[str, Document] = {}
        if self._documents_path.exists():
            with open(self._documents_path, "rb") as f:
                self._documents = pickle.load(f)
        self._vector_store = Chroma(collection_name=name, 
                                    embedding_function=emb_func, 
                                    persist_directory=self._persist_path)

    def reload(self):
        self.__transform__()
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
    
    def __transform__(self):
        """
        download content from remote server and transform to documents
        """
        raise NotImplementedError

    def collection_count(self) -> int:
        return 0 if not self._vector_store else self._vector_store._collection.count()
        
    def del_docment(self, key:str):
        self._documents.pop(key, None)
    
    def batch_add_document(self, docs:List[Document]):
        for d in docs:
            self._documents[d.metadata['source']] = d
        self.save_documents()
        
    def save_documents(self):
        with open(self._documents_path, "wb") as f:
            pickle.dump(self._documents, f)

    def vectorstore(self)->VectorStore:
        return self._vector_store
    
    def __str__(self):
        return f"{self.__class__.__name__}({self._args}, {self._kwargs})"

    def __repr__(self):
        return str(self)
