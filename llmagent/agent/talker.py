import sys
import os

from ..llmapi import model_spec
from ..secret import AK_SK
keys = AK_SK('keystore/qianfan.keys')
os.environ["QIANFAN_ACCESS_KEY"] = keys.get_ak()
os.environ["QIANFAN_SECRET_KEY"] = keys.get_sk()

def main(agent_api:str, model_spec:model_spec.LLMModelSpec,
        private_store:str=None,
        private_store_kwargs:dict=None):
    if agent_api == 'QianFan':
        from ..llmapi import QianfanLLM, QianfanEmbedding
        llm = QianfanLLM(model_spec=model_spec, temperature=0.5)
        if private_store:
            