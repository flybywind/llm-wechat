'''
支持confluence的私有资料库
'''
from langchain_community.document_loaders import WebBaseLoader
from . import * 

class WebConf(BaseConf):
    limit: int = Field(10, gt=1, description="每次请求的最大数量")
    header_template:dict
    verify_ssl:bool = False
    proxies:dict = None
    continue_on_failure:bool = True
    autoset_encoding:bool = True
    encoding:str = None
    default_parser:str = "html.parser"
    bs_kwargs:dict = None

class WebStore(BaseStore):
    def __init__(self, name:str, persist_path:str, emb_func: Embeddings, extra_config: WebConf):
        super().__init__(name, persist_path, emb_func, extra_config)
        self._vector_store = Chroma(collection_name=name, 
                                    embedding_function=emb_func, 
                                    persist_directory=self._persist_path)

    

    def __download__(self):
        loader = WebBaseLoader(
            web_path=self._extra_config.url,
            requests_per_second=self._extra_config.limit,
                               verify_ssl=self._extra_config.verify_ssl,
                               proxies=self._extra_config.proxies,
                               continue_on_failure=self._extra_config.continue_on_failure,
                               default_parser=self._extra_config.default_parser)
        self.save_documents()