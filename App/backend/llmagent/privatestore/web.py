'''
支持confluence的私有资料库
'''
from typing import Iterator
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from urllib.parse import urljoin, urlparse
from .base import *

class WebConf(BaseConf):
    root_url:str
    exclude_tags: List[str] = []
    limit: int = Field(10, gt=1, description="每次请求的最大数量")
    header_template:dict = {}
    verify_ssl:bool = False
    proxies:dict = None
    continue_on_failure:bool = True
    autoset_encoding:bool = True
    encoding:str = None
    default_parser:str = "html.parser"
    bs_kwargs:dict = None

def _build_metadata(soup, url: str) -> dict:
    """Build metadata from BeautifulSoup output."""
    metadata = {"source": url}
    if title := soup.find("title"):
        metadata["title"] = title.get_text()
    if description := soup.find("meta", attrs={"name": "description"}):
        metadata["description"] = description.get("content", "No description found.")
    if html := soup.find("html"):
        metadata["language"] = html.get("lang", "No language found.")
    return metadata

class WebRecursiveLoader(WebBaseLoader):
    def __init__(self, root_url:str, depth: int = 1, 
                 unwanted_tags:List[str] = [], 
                 already_loaded_url:Set[str] = set(), 
                 **kwargs):
        super().__init__(web_path=root_url, **kwargs)
        self.domain = urlparse(root_url).netloc
        self.depth = depth
        self.bs_transformer = BeautifulSoupTransformer()
        self.loaded_set = already_loaded_url
        self.unwanted_tags = list(set(unwanted_tags).union(set(["script", "style"])))

    def lazy_load(self) -> Iterator[Document]:
        def __inner_load__(url: str, depth: int):
            if depth < 0:
                return
            soup:BeautifulSoup = self._scrape(url, bs_kwargs=self.bs_kwargs)
            if url not in self.loaded_set:
                text = str(soup)
                metadata = _build_metadata(soup, url)
                yield Document(page_content=text, metadata=metadata)
                self.loaded_set.add(url)
            links = soup.find_all("a", href=True)
            for link in links:
                full_url = urljoin(url, link["href"])
                parsed_url = urlparse(full_url)
                if parsed_url.netloc == self.domain and full_url not in self.loaded_set:
                    yield from __inner_load__(full_url, depth - 1)
        yield from __inner_load__(self.web_path, self.depth)
    
    def load(self) -> List[Document]:
        return self.bs_transformer.transform_documents(
            list(self.lazy_load()),
            unwanted_tags=self.unwanted_tags)
class WebStore(BaseStore):
    def __init__(self, name:str, persist_path:str, emb_func: Embeddings, extra_config: WebConf):
        super().__init__(name, persist_path, emb_func, extra_config)
       
    def __transform__(self):
        loader = WebRecursiveLoader(
            root_url=self._extra_config.root_url,
            already_loaded_url=set(self._documents.keys()),
            unwanted_tags=self._extra_config.exclude_tags,
            requests_per_second=self._extra_config.limit,
            verify_ssl=self._extra_config.verify_ssl,
            proxies=self._extra_config.proxies,
            continue_on_failure=self._extra_config.continue_on_failure,
            default_parser=self._extra_config.default_parser)
        documents = loader.load()
        self.batch_add_document(documents)