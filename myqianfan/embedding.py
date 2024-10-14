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


if __name__ == "__main__":
    import os
    import sys
    sys.path[0] = os.path.abspath(".")
    import secret
    ak_sk = secret.AK_SK("qianfan.keys")
    os.environ["QIANFAN_ACCESS_KEY"] = ak_sk.get_ak()
    os.environ["QIANFAN_SECRET_KEY"] = ak_sk.get_sk()
    emb = QianfanEmbedding()
    """
    填写文本，说明：
    （1）不能为空List，List的每个成员不能为空字符串
    （2）文本数量不超过16
    （3）每个文本token数不超过384且长度不超过1000个字符
    """
    q = ["你好, 世界上最大的动物是什么？"*50]*16
    emb = emb.embed_documents(q)
    print(f"query length: {len(q[0])}, embedding length: {len(emb)}")