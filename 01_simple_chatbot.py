from langgraph.graph import StateGraph, START, END
from langchain_aws import ChatBedrockConverse
from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage

class AgentState(TypedDict):
    messages: list

llm = ChatBedrockConverse(
    model="amazon.nova-pro-v1:0"
)

def chatbot(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages":[response]}

graph = StateGraph(AgentState)

graph.add_node("chatbot", chatbot)

graph.add_edge(START, "chatbot")
graph.add_edge("chatbot",END)

app = graph.compile()

print("\t🤖 Welcome\nType 'exit' to quit.\n")
while True:

    user_input = input("👤 you: ")
    if user_input.lower() == "exit":
        break

    response = app.invoke({
        "messages": [
            SystemMessage(content="you are helpful assistant, answer user questions carefully to the point"),
            HumanMessage(content=user_input)
        ]
    })
    print("\n🤖 AI: ",response["messages"][-1].content)
