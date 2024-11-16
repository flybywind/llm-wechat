from llmagent.conf import setting

from llmagent.privatestore import BaseStore
from llmagent.llmapi import LLM, model_spec
from llmagent.chain import BaseChain


def test_setting():
    chain_setting = setting.Setting(
        name="QAWithContextChain",
        readible_name="个人知识库",
        base_clazz=BaseChain,
        options=[
            (
                setting.OptionSpec(
                    param_name="vectorstore",
                    readible_name="向量库",
                    base_clazz=BaseStore,
                ),
                [
                    setting.OptionSpec(
                        param_name="root_url",
                        readible_name="根URL",
                        base_clazz=str,
                    ),
                    setting.OptionSpec(
                        param_name="depth",
                        readible_name="深度",
                        base_clazz=int,
                    ),
                ],
            ),
            (
                setting.OptionSpec(
                    readible_name="大模型", param_name="llm", base_clazz=LLM
                ),
                [
                    setting.OptionSpec(
                        param_name="model_spec",
                        readible_name="模型规格",
                        base_clazz=model_spec.LLMModelSpec,
                    ),
                    setting.OptionSpec(
                        param_name="top_p",
                        readible_name="核采样概率阈值",
                        base_clazz=float,
                    ),
                    setting.OptionSpec(
                        param_name="enable_search",
                        readible_name="是否打开实时搜索功能",
                        base_clazz=bool,
                    ),
                ],
            ),
        ],
    )
    chain_setting.select_option(0, root_url="http://www.baidu.com", depth=3)
    assert chain_setting.get_option(0)[0].value == "http://www.baidu.com"
    assert chain_setting.get_option(0)[1].value == 3
