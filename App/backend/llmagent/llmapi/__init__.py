from . import model_spec
from .llm import QianfanLLM, QwenLLM
from .embedding import QianfanEmbedding, QwenEmbedding

__all__ = ["QianfanLLM","QwenLLM", "QianfanEmbedding", "QwenEmbedding", "model_spec"]