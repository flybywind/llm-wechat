import os
import qianfan
from myqianfan import model_spec
from secret import AK_SK
keys = AK_SK('qianfan.keys')
os.environ["QIANFAN_ACCESS_KEY"] = keys.get_ak()
os.environ["QIANFAN_SECRET_KEY"] = keys.get_sk()

def testRawModel():
    chat_comp = qianfan.ChatCompletion()
    # 指定特定模型
    resp = chat_comp.do(model=model_spec.Tiny8K.name, messages=[{
        "role": "user",
        "content": "你好, 世界上最大的动物是什么？"
    }, {
        "role": "assistant",
        "content": "世界上最大的动物是蓝鲸。它是已知最大的已知动物，是海洋生物中的巨无霸。"
    }, {
        "role": "user",
        "content": "那蓝鲸的体重有多重？"
    }], stream=True)

    for r in resp:
        print(r['body'])

def testLLM():
    from myqianfan.llm import QianfanLLM
    llm = QianfanLLM(model_spec=model_spec.Tiny8K, temperature=0.3)#, max_content_len=20)
    # stream = llm._stream("你好, 世界上最大的动物是什么？")
    # for token in stream:
    #     print(token)
    # print("==="*10)
    # stream = llm._stream("世界上最聪明的动物又是什么？")
    # for token in stream:
    #     print(token)
    # print("==="*10)
    # print(llm.conversation_history)

    print(llm.invoke("你好, 世界上最大的动物是什么？"))
    print(llm.invoke("世界上最聪明的动物又是什么？"))
    print(llm.conversation_history)

def testCustomLLM():
    from myqianfan.llm import MyCustomLLM
    llm = MyCustomLLM(some_param="abc")
    llm.generate(["hello"])

if __name__ == "__main__":
    testLLM()