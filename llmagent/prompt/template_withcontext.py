from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个解答用户问题的assistant，可以根据从语料库中召回的context文本回答问题。请尽量保证回答的内容都可以在context中找到根据，并务必保留 source 后面的url链接。\n以下是context文本：{context}，\n以下是之前的聊天历史：{history}"),
            ("human", "{question}"),
        ]
    )

# 假设有一些聊天历史记录
chat_history = [
    HumanMessage(content="Hi, how are you?"),
    AIMessage(content="I'm good, thanks! How can I help you today?"),
    HumanMessage(content="Tell me a joke."),
    AIMessage(content="Why don't scientists trust atoms? Because they make up everything!")
]

# 将历史记录转换为字符串，控制需要传递的历史消息长度
recent_history = "\n".join([f"{message.type}: {message.content}" for message in chat_history])

# 将裁剪后的历史和用户输入传递给模板
prompt = template.format_messages(
    history=recent_history,
    input="Can you explain that joke?"
)

for message in prompt:
    print(f"{message.type}: {message.content}")

