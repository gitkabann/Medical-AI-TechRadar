import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import os
from app.tools.dummy_search import DummySearchTool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
def create_react_agent():
    llm = ChatOpenAI(
                model_name='deepseek-chat',
                api_key='sk-5f99ca2a1b874d8295ed86b5155adfb7',
                base_url="https://api.deepseek.com")
    tools = [DummySearchTool()]
    agent = create_agent(
        llm,
        tools
    )
    return agent

if __name__ == "__main__":
    agent = create_react_agent()
    inputs = "请帮我查找关于癌症治疗的最新研究论文。"
    prompt ={"messages": [{"role": "user", "content": inputs}]}
    response = agent.invoke(prompt)
    for msg in response["messages"]:
        print(f"{msg.__class__.__name__}: {msg.content}\n")
