from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_aws import ChatBedrockConverse


# Bedrock LLM
llm = ChatBedrockConverse(
    model="amazon.nova-lite-v1:0",
    temperature=0
)


# State
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # Adds metadata to the type: (Annotated) /  # Stores chat messages: (list)
                                             # Automatically appends/merges new messages: (add_messages)       



# Chatbot Node
def chatbot(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# Graph
builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)


# Checkpointer
memory = InMemorySaver() # Stores chat history in RAM

graph = builder.compile(checkpointer=memory)


# Thread ID
thread_id = input("Enter User ID: ")

config = {
    "configurable": {
        "thread_id": thread_id
    }
}


print("\t🤖 Welcome")
print("Type exit to quit\n")

while True:

    user = input("👤 You: ")

    if user.lower() == "exit":
        break

    result = graph.invoke(
        {
            "messages": [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content=user)
            ]
        },
        config=config
    )

    print("\n🤖 AI:", result["messages"][-1].content)