from typing import Annotated, TypedDict

from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver


# Define the calculator tool
@tool
def calculator(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# Initialize the Bedrock model
model = ChatBedrockConverse(
    model="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)


# Bind tool to the LLM
model_with_tools = model.bind_tools([calculator])


# Define graph state
class State(TypedDict):
    messages: Annotated[list, add_messages]


# LLM node
def chatbot(state: State):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# Tool node
tool_node = ToolNode([calculator])


# Decide whether to call a tool or finish
def should_continue(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# Create graph
graph = StateGraph(State)

graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbot")

graph.add_conditional_edges(
    "chatbot",
    should_continue
)

graph.add_edge("tools", "chatbot")


# Create memory/checkpointer
checkpointer = InMemorySaver()


# Compile graph with memory
app = graph.compile(
    checkpointer=checkpointer
)


# Conversation ID
config = {
    "configurable": {
        "thread_id": "user_1"
    }
}


# First message
result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "My name is Musaddiq."
            }
        ]
    },
    config
)

print(result["messages"][-1].content)


# Second message
result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is my name?"
            }
        ]
    },
    config
)

print(result["messages"][-1].content)

"""
Short Purpose

This code adds short-term memory to a LangGraph ReAct agent
using a checkpointer and thread-based conversation state.

Flow:
User → State → LLM/Tool → Checkpoint → Next Message → Previous Context
"""
