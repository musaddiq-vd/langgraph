from typing import Annotated
from typing_extensions import TypedDict

from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


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


# Bind tools to the LLM
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


# Add nodes
graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)


# START → chatbot
graph.add_edge(START, "chatbot")


# chatbot → tools OR END
graph.add_conditional_edges(
    "chatbot",
    should_continue
)


# tools → chatbot
graph.add_edge("tools", "chatbot")


# Compile graph
app = graph.compile()


# Run the agent
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is 10 + 20?"
        }
    ]
})


# Print final answer
print(result["messages"][-1].content)
