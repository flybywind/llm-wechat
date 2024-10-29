import os
from loguru import logger
import json

__cwd__ = os.path.abspath(os.path.dirname(__file__))
__root__ = os.path.abspath(os.path.join(__cwd__, ".."))
class ConfigManager:
    """
    langchain相关的配置
    """
    def __init__(self):
        self.config_file = "app_config.json"
        self.config = self.load_config()
        self.command_prefix = ":"
        self.langchain = None

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def set_config(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def get_langchain_or_default(self):
        if self.langchain:
            return self.langchain
        logger.info("未设置langchain, 使用默认配置")
        return self._get_default_langchain()
    
    def _get_default_langchain(self):
        from ..privatestore import WebStore, WebConf
        from ..secret import AK_SK
        from ..llmapi import model_spec, QwenEmbedding, QwenLLM
        from ..chain import QAWithContextChain, TemplateConf
        qw_key = AK_SK(os.path.join(__root__, "secret/keystore/qwen.keys"))
        os.environ["OPENAI_API_KEY"] = qw_key.ak
        llm = QwenLLM(model_spec=model_spec.QwenPlus, temperature=0.6)
        embedding = QwenEmbedding(api_key=qw_key.ak)
        webstore = WebStore("llmtutorial", 
                            os.path.join(__root__, "..", "vectorstore/llmtutorial_qwen"), 
                            emb_func=embedding, extra_config=WebConf(
                                root_url="https://aitutor.liduos.com/",
                                limit=10,
                            ))
        chain = QAWithContextChain(llm=llm, 
                               vectorstore=webstore.vectorstore(),
                               conf=TemplateConf(context_num=10, history_num=3))
        return chain
