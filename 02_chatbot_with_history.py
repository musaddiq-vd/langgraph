from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_aws import ChatBedrockConverse


llm = ChatBedrockConverse(
    model="amazon.nova-lite-v1:0",
    temperature=0
)

class ChatState(TypedDict):
    messages: list


def chatbot(state: ChatState):

    # Get complete conversation
    messages = state["messages"]

    # Send conversation to Bedrock
    response = llm.invoke(messages)

    # Add AI response to conversation
    messages.append(AIMessage(content=response.content))

    # Return updated conversation
    return {
        "messages": messages
    }


builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()


# Manual Conversation History, System msg directlty added here in empty list
conversation = [
    SystemMessage(content="You are a helpful assistant. Answer user questions carefully and to the point.")
]

print("\t🤖 Welcome")
print("Type 'exit' to quit.\n")

while True:

    user_input = input("👤 You: ")

    if user_input.lower() == "exit":
        break

    # Store user message
    conversation.append(
        HumanMessage(content=user_input)
    )

    # Execute graph
    result = graph.invoke({
        "messages": conversation
    })

    # Update conversation with AI response
    conversation = result["messages"]

    print("\n🤖 AI:", conversation[-1].content)