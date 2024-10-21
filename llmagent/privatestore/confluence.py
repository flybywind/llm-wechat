'''
支持confluence的私有资料库
'''
import getpass
from atlassian import Confluence
from langchain_community.document_loaders import ConfluenceLoader
from . import * 

class ConfluenceConf(BaseConf):
    url: str
    username: str
    root_page_id: int
    limit: int = Field(10, gt=1, description="每次请求的最大数量")

class ConfluenceStore(BaseStore):
    def __init__(self, name:str, persist_path:str, emb_func: Embeddings, extra_config: ConfluenceConf):
        super().__init__(name, persist_path, emb_func, extra_config)
        self._vector_store = Chroma(collection_name=name, 
                                    embedding_function=emb_func, 
                                    persist_directory=self._persist_path)

    def __download__(self):
        def get_children_pages_recursively(client, page_id: str):
            child_pages = client.get_page_child_by_type(page_id)
            for page in child_pages:
                yield page
                if "id" in page:
                    yield from get_children_pages_recursively(client, page["id"])

        # get all pages under some page
        confluence = Confluence(
            url=self._extra_config.url,
            username=self._extra_config.username,
            password=self._extra_config.passwd)
        child_pages = [p for p in get_children_pages_recursively(confluence, self._extra_config.root_page_id)
                       if p['url'] not in self._documents]
        if child_pages:
            passwd = getpass.getpass()
            loader = ConfluenceLoader(
                url=self._extra_config.url,
                page_ids=[p["id"] for p in child_pages ],
                username=self._extra_config.username,
                api_key=passwd,
                limit=self._extra_config.limit,
            )
            documents = loader.load()
            for doc in documents:
                self.add_document(doc.metadata["source"], doc)
            self.save_documents()