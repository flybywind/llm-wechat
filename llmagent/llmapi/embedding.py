from typing import Any
from langchain_core.embeddings import Embeddings
from pydantic import Field, BaseModel
import qianfan

class QianfanEmbedding(BaseModel, Embeddings):
    name: str = "Embedding-V1"
    retry_count:int = Field(gt=1, default=3)
    request_timeout:int = Field(gt=10, default=60)

    _client: qianfan.Embedding = None

    def model_post_init(self, __context: Any) -> None:
        self._client = qianfan.Embedding()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.do(texts, model=self.name)
        ret = [None]*len(texts)
        for r in resp['body']['data']:
            ret[r['index']] = r['embedding']

        return ret
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
