from http import HTTPStatus
from typing import Any, List
from langchain_core.embeddings import Embeddings
from pydantic import Field, BaseModel
from loguru import logger
import qianfan
class QianfanEmbedding(BaseModel, Embeddings):
    name: str = "Embedding-V1"
    retry_count:int = Field(gt=1, default=3)
    request_timeout:int = Field(gt=10, default=60)

    _client: qianfan.Embedding = None

    def model_post_init(self, __context: Any) -> None:
        self._client = qianfan.Embedding()
    #todo add batch operation
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.do(texts, model=self.name,
                               retry_count=self.retry_count,
                               request_timeout=self.request_timeout)
        ret = [None]*len(texts)
        for r in resp['body']['data']:
            ret[r['index']] = r['embedding']

        return ret
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]



import dashscope
class QwenEmbedding(BaseModel, Embeddings):
    name: str = dashscope.TextEmbedding.Models.text_embedding_v3
    DASHSCOPE_MAX_BATCH_SIZE = 25
    # todo, retry setup
    def _batched(self, inputs: List[str]):
        for i in range(0, len(inputs), self.DASHSCOPE_MAX_BATCH_SIZE):
            yield inputs[i:i + self.DASHSCOPE_MAX_BATCH_SIZE]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = None  # merge the results.
        batch_counter = 0
        for batch in self._batched(texts):
            resp = dashscope.TextEmbedding.call(model=self.name, input=batch)
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
