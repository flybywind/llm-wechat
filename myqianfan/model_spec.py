from collections import namedtuple

QianFanModel = namedtuple("QianFanModel", ["name", "max_str_len", "max_token_len"])
Speed128K = QianFanModel(name="ERNIE-Speed-128K", max_str_len=516096, max_token_len=126976)
Tiny8K = QianFanModel(name="ERNIE-Tiny-8K", max_str_len=24000, max_token_len=6144)
ERNIE4_8K = QianFanModel(name="ERNIE-4.0-8K", max_str_len=20000, max_token_len=5120)
ERNIE4_Turbo8K = QianFanModel(
    name="ERNIE-4.0-Turbo-8K", max_str_len=20000, max_token_len=5120
)
