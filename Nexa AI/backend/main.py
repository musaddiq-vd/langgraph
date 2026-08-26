import json
from typing import TypedDict, Annotated

from fastapi import FastAPI
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrockConverse


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI()


# ============================================================
# BEDROCK LLM
# ============================================================

llm = ChatBedrockConverse(
    model="amazon.nova-lite-v1:0",
    temperature=0
)


# ============================================================
# LANGGRAPH STATE
# ============================================================

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default-user"


# ============================================================
# CHATBOT NODE
# ============================================================

def chatbot(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


# ============================================================
# MEMORY / CHECKPOINTER
# ============================================================

memory = InMemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# ============================================================
# CHAT API
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    result = graph.invoke(
        {
            "messages": [
                SystemMessage(
                    content="You are a helpful AI assistant."
                ),
                HumanMessage(
                    content=request.message
                )
            ]
        },
        config=config
    )

    response = result["messages"][-1].content

    return {
        "response": response,
        "thread_id": request.thread_id
    }


# ============================================================
# AWS LAMBDA HANDLER
# ============================================================

from mangum import Mangum

handler = Mangum(app)
