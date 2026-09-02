from typing import Annotated, TypedDict

from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# Define a tool that can raise an error
@tool
def calculator(a: int, b: int) -> int:
    """Divide two numbers."""

    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a // b


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


# Tool node with automatic error handling
tool_node = ToolNode(
    [calculator],
    handle_tool_errors=True
)


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


# Compile graph
app = graph.compile()


# Run the agent
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Divide 10 by 0."
        }
    ]
})


# Print final response
print(result["messages"][-1].content)
