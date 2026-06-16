"""
NAME:model

Auther：ZT
Version：
DATE:2026/6/16
"""
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="0cd19b26a1ce4fe5ac45e4a2c5938674.seW5Bs8ZOIgr27kB",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4.7",
    temperature=0.3
)