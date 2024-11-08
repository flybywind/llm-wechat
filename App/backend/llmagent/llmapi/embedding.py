from http import HTTPStatus
from typing import Any, List
from langchain_core.embeddings import Embeddings
from pydantic import ConfigDict, Field, BaseModel
from loguru import logger
import qianfan

def _batched(inputs: List[str], MAX_BATCH_SIZE):
        for i in range(0, len(inputs), MAX_BATCH_SIZE):
            yield inputs[i:i + MAX_BATCH_SIZE]

class QianfanEmbedding(BaseModel, Embeddings):
    name: str = "Embedding-V1"
    MAX_BATCH_SIZE:int = 16
    retry_count:int = Field(gt=1, default=3)
    request_timeout:int = Field(gt=10, default=60)
    _client: qianfan.Embedding = None

    model_config = ConfigDict(
         arbitrary_types_allowed=True
    )

    def model_post_init(self, __context: Any) -> None:
        self._client = qianfan.Embedding()
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = None  # merge the results.
        batch_counter = 0
        for batch in _batched(texts, self.MAX_BATCH_SIZE):
            resp = self._client.do(batch, model=self.name,
                               retry_count=self.retry_count,
                               request_timeout=self.request_timeout)
            if resp.code == HTTPStatus.OK.value:
                if result is None:
                    result = resp
                else:
                    for emb in resp.body['data']:
                        emb['index'] += batch_counter
                        result.body['data'].append(emb)
            else:
                logger.error(f'error getting batch {batch}, {resp}')
        ret = [None]*len(texts)
        for r in result.body['data']:
            ret[r['index']] = r['embedding']

        return ret
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]



import dashscope

from .util import make_retriable
class QwenEmbedding(BaseModel, Embeddings):
    api_key: str
    name: str = dashscope.TextEmbedding.Models.text_embedding_v3
    MAX_BATCH_SIZE:int = 6
    
    @make_retriable(max_attempts=3,
                    max_delay=60, 
                    min_wait=1, 
                    max_wait=10,
                    logger=logger)
    def _call_qwen(self, model, input):
        return dashscope.TextEmbedding.call(model=model, input=input,api_key=self.api_key)
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = None  # merge the results.
        batch_counter = 0
        for batch in _batched(texts, self.MAX_BATCH_SIZE):
            resp = self._call_qwen(model=self.name, input=batch)
            if resp.status_code == HTTPStatus.OK:
                if result is None:
                    result = resp
                else:
                    for emb in resp.output['embeddings']:
                        emb['text_index'] += batch_counter
                        result.output['embeddings'].append(emb)
            else:
                logger.error(f'error getting batch {batch}, {resp}')
            batch_counter += len(batch)

        ret = [None]*len(texts)
        for r in result.output['embeddings']:
            ret[r['text_index']] = r['embedding']

        return ret
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
