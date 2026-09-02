from typing import Annotated, TypedDict

from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command
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


# Human approval node
def human_approval(state: State):

    # Pause execution and wait for human input
    decision = interrupt(
        "Approve calculator execution? Type 'yes' or 'no'."
    )

    if decision.lower() == "yes":
        return {"approved": True}

    return {"approved": False}


# Tool node
tool_node = ToolNode([calculator])


# Decide whether a tool is required
def should_continue(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "approval"

    return END


# Check human approval
def check_approval(state: State):

    if state["approved"]:
        return "tools"

    return END


# Create graph
graph = StateGraph(State)


# Add nodes
graph.add_node("chatbot", chatbot)
graph.add_node("approval", human_approval)
graph.add_node("tools", tool_node)


# Define edges
graph.add_edge(START, "chatbot")

graph.add_conditional_edges(
    "chatbot",
    should_continue
)

graph.add_conditional_edges(
    "approval",
    check_approval
)

graph.add_edge("tools", "chatbot")


# Add checkpointing
checkpointer = InMemorySaver()


# Compile graph
app = graph.compile(
    checkpointer=checkpointer
)


# Conversation ID
config = {
    "configurable": {
        "thread_id": "user_1"
    }
}


# Start the agent
result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is 10 + 20?"
            }
        ]
    },
    config
)


# Check if the graph is waiting for human input
print(result)


# Resume after human approval
result = app.invoke(
    Command(resume="yes"),
    config
)


# Print final answer
print(result["messages"][-1].content)
