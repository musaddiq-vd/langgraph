from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict


app = FastAPI()


class AgentState(TypedDict):
    messages: list


class ChatRequest(BaseModel):
    message: str


llm = ChatBedrockConverse(
    model="amazon.nova-pro-v1:0"
)


def chatbot(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(AgentState)

graph.add_node("chatbot", chatbot)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

agent = graph.compile()


@app.post("/chat")
def chat(request: ChatRequest):

    response = agent.invoke({
        "messages": [
            SystemMessage(
                content="Your name is Nexa AI, You are a helpful assistant. Answer user questions carefully and to the point."
            ),
            HumanMessage(content=request.message)
        ]
    })

    return {
        "response": response["messages"][-1].content
    }

from mangum import Mangum

handler = Mangum(app)