import json
from llmagent.conf.option_map import AgentOptionMap
from llmagent.conf.param import ItemParam, SingleParam, ListParam
from llmagent.llmapi.llm import QianfanLLM, QwenLLM
from llmagent.llmapi.embedding import QianfanEmbedding, QwenEmbedding
from llmagent.llmapi.model_spec import *
from llmagent.privatestore.confluence import ConfluenceConf, ConfluenceStore
from llmagent.privatestore.web import WebConf, WebStore
from llmagent.chain.base import TemplateConf
from llmagent.chain.qa_withcontext_chain import QAWithContextChain
from llmagent.secret.load import AK_SK

qwen_key = AK_SK("llmagent/secret/keystore/qwen.keys")
qfan_key = AK_SK("llmagent/secret/keystore/qianfan.keys")
import os

os.environ["QIANFAN_ACCESS_KEY"] = qfan_key.get_ak()
os.environ["QIANFAN_SECRET_KEY"] = qfan_key.get_sk()
os.environ["OPENAI_API_KEY"] = qwen_key.get_ak()


def test_agent_options():
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
                    persist_path=SingleParam(
                        repr_name="persist_path", value="confluence"
                    ),
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
                            url=SingleParam(repr_name="url", value="https://web.com"),
                            limit=SingleParam(repr_name="limit", value=10),
                        ),
                    ),
                ),
            ),
        ],
    )
    agent_opts = AgentOptionMap(
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
                            history_num=SingleParam(
                                repr_name="历史会话的数量", value=3
                            ),
                        ),
                    ),
                ),
            )
        ]
    )

    agent0 = agent_opts.get_agent(0)
    agent_opts.clone_agent(0, "私有资料库QA2")
    # 把LLM设置为llm_list的第二个
    agent_opts.update_agent_of_paths(1, 1, "llm")
    # 把LLM设置为llm_list的第二个
    agent_opts.update_agent_of_paths(0.9, 1, "llm", "top_p")
    agent1 = agent_opts.get_agent(1)
    assert agent0.llm.model_spec == QwenPlus
    assert isinstance(agent0.llm, QwenLLM)
    assert isinstance(agent1.llm, QianfanLLM)
    assert agent1.llm.model_spec == ERNIE4_8K
    agent_opts.update_agent_of_paths(2, 1, "llm", "model_spec")
    agent1 = agent_opts.get_agent(1)
    assert isinstance(agent0.llm, QwenLLM)
    assert isinstance(agent1.llm, QianfanLLM)
    assert agent1.llm.model_spec == Speed128K

    print("json dump:{}".format(agent_opts.model_dump_json()))