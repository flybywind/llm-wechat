import os
from pathlib import Path
import webview
import webview.menu as wm
from llmagent.chain.base import TemplateConf
from llmagent.chain.qa_withcontext_chain import QAWithContextChain
from llmagent.conf.option_map import AgentOptionMap
from llmagent.conf.param import ItemParam, SingleParam, ListParam
from llmagent.llmapi.llm import QianfanLLM, QwenLLM
from llmagent.llmapi.embedding import QianfanEmbedding, QwenEmbedding
from llmagent.llmapi.model_spec import *
from llmagent.privatestore.confluence import ConfluenceConf, ConfluenceStore
from llmagent.privatestore.web import WebConf, WebStore

emb_func_list = ListParam(
    repr_name="向量化API列表",
    selections=[
        ItemParam(
            repr_name="千帆向量化",
            clazz_type=QianfanEmbedding,
            construct_params=dict(
                name=SingleParam(repr_name="name", value="Embedding-V1"),
            ),
        ),
        ItemParam(
            repr_name="通义向量化",
            clazz_type=QwenEmbedding,
            construct_params=dict(
                name=SingleParam(repr_name="name", value="text-embedding-v3"),
            ),
        ),
    ],
)
llm_list = ListParam(
    repr_name="大模型列表",
    selections=[
        ItemParam(
            repr_name="通义千问",
            clazz_type=QwenLLM,
            construct_params=dict(
                top_p=SingleParam(repr_name="top_p", value=0.8),
                model_spec=ListParam(repr_name="模型规格", selections=[QwenPlus]),
            ),
        ),
        ItemParam(
            repr_name="千帆",
            clazz_type=QianfanLLM,
            construct_params=dict(
                top_p=SingleParam(repr_name="top_p", value=0.8),
                model_spec=ListParam(
                    repr_name="模型规格",
                    selections=[
                        ERNIE4_8K,
                        ERNIE4_Turbo8K,
                        Speed128K,
                    ],
                ),
            ),
        ),
    ],
)
docstore_list = ListParam(
    repr_name="向量库",
    selections=[
        ItemParam(
            repr_name="Confluence",
            clazz_type=ConfluenceStore,
            construct_params=dict(
                name=SingleParam(repr_name="name", value="confluence"),
                persist_path=SingleParam(repr_name="persist_path", value="confluence"),
                emb_func=emb_func_list.model_copy(deep=True),
                extra_config=ItemParam(
                    repr_name="Confluence配置",
                    clazz_type=ConfluenceConf,
                    construct_params=dict(
                        url=SingleParam(
                            repr_name="url",
                            value="https://confluence.com",
                        ),
                        username=SingleParam(repr_name="username", value="admin"),
                        root_page_id=SingleParam(repr_name="root_page_id", value=1),
                        limit=SingleParam(repr_name="limit", value=10),
                    ),
                ),
            ),
        ),
        ItemParam(
            repr_name="Web",
            clazz_type=WebStore,
            construct_params=dict(
                name=SingleParam(repr_name="name", value="web"),
                persist_path=SingleParam(repr_name="persist_path", value="web"),
                emb_func=emb_func_list.model_copy(deep=True),
                extra_config=ItemParam(
                    repr_name="Web配置",
                    clazz_type=WebConf,
                    construct_params=dict(
                        url=SingleParam(repr_name="url", value="https://example.com"),
                        limit=SingleParam(repr_name="limit", value=10),
                    ),
                ),
            ),
        ),
    ],
)
agents_option_map = AgentOptionMap(
    agents=[
        ItemParam(
            repr_name="私有资料库QA",
            clazz_type=QAWithContextChain,
            construct_params=dict(
                llm=llm_list.model_copy(deep=True),
                documentstore=docstore_list.model_copy(deep=True),
                conf=ItemParam(
                    repr_name="上下文配置",
                    clazz_type=TemplateConf,
                    construct_params=dict(
                        context_num=SingleParam(repr_name="相关文章数量", value=3),
                        history_num=SingleParam(repr_name="历史会话的数量", value=3),
                    ),
                ),
            ),
        )
    ]
)
HTML_ROOT = Path(os.environ.get("HTML_ROOT"))


def show_ai_agents():
    active_window = webview.active_window()
    if active_window:
        active_window.load_html(HTML_ROOT / "config.html")


def config_aikeys():
    active_window = webview.active_window()
    if active_window:
        active_window.load_html(HTML_ROOT / "keys.html")


menu_items = [
    wm.MenuAction("Ai列表", show_ai_agents()),
    wm.MenuAction("Api Key", config_aikeys()),
    wm.MenuSeparator(),
    wm.MenuAction("退出", lambda: exit()),
]
