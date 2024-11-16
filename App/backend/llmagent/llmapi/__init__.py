from . import model_spec
from .llm import QianfanLLM, QwenLLM, LLM
from .embedding import QianfanEmbedding, QwenEmbedding

__all__ = ["QianfanLLM","QwenLLM", "QianfanEmbedding", "QwenEmbedding", "model_spec"]
