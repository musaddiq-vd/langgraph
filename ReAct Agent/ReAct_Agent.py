from typing import Annotated, TypedDict

from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# Tool
@tool
def calculator(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# LLM
model = ChatBedrockConverse(
    model="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

# Bind tools
model_with_tools = model.bind_tools([calculator])


# Agent State
class State(TypedDict):
    messages: Annotated[list, add_messages]


# LLM Node
def chatbot(state: State):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# Tool Node
tool_node = ToolNode([calculator])


# Routing logic
def should_continue(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# Build Graph
graph = StateGraph(State)

graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbot")

graph.add_conditional_edges(
    "chatbot",
    should_continue
)

graph.add_edge("tools", "chatbot")


# Compile Agent
app = graph.compile()


# Run Agent
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is 10 + 20?"
        }
    ]
})


# Final Answer
print(result["messages"][-1].content)




"""
created a ReAct agent using LangGraph where the LLM decides whether a tool is required. 
If a tool is required, the request goes to ToolNode, the result comes back to the LLM, 
and the cycle continues until the LLM generates the final answer.
"""
