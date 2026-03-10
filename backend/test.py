from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="kimi-k2.5",
    api_key="sk-bhxBB1jkGZYUpWDCEwrLhe4DkMbAtk6yEkT4zA93t6c9zPB0",
    base_url="https://api.moonshot.ai/v1"
)

response = llm.invoke("Explain quantum mechanics simply")

print(response.content)