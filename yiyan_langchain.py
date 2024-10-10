import os
import qianfan
import myqianfan
from myqianfan import QianFanModel
from secret import AK_SK
keys = AK_SK('qianfan.keys')
os.environ["QIANFAN_ACCESS_KEY"] = keys.get_ak()
os.environ["QIANFAN_SECRET_KEY"] = keys.get_sk()
chat_comp = qianfan.ChatCompletion()

# 指定特定模型
resp = chat_comp.do(model=QianFanModel.Tiny8K, messages=[{
    "role": "user",
    "content": "你好, 世界上最大的动物是什么？"
}])

chat_comp = qianfan.ChatCompletion()

print(resp["body"])