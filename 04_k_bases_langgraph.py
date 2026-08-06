from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_aws import (
    ChatBedrockConverse,
    AmazonKnowledgeBasesRetriever,
)


llm = ChatBedrockConverse(
    model="amazon.nova-lite-v1:0",
    temperature=0
)

# Bedrock Knowledge Base Retriever

retriever = AmazonKnowledgeBasesRetriever(

    # Your Knowledge Base ID
    knowledge_base_id="LETD843TMS",

    retrieval_config={
        "vectorSearchConfiguration": {

            # Retrieve Top 3 documents
            "numberOfResults": 3
        }
    }
)


class State(TypedDict):

    question: str      # User question

    context: list      # Retrieved documents

    answer: str        # Final answer


#Retriever Node
def retrieve(state: State):

    # Search Knowledge Base
    docs = retriever.invoke(state["question"])

    # Return retrieved documents
    return {
        "context": docs
    }


# def retrieve(state: State):

#     docs = retriever.invoke(state["question"])

#     print("\n========== Retrieved Documents ==========")

#     for i, doc in enumerate(docs, 1):
#         print(f"\nDocument {i}")
#         print(doc.page_content[:200])      
#         print("\nMetadata:", doc.metadata)

#     return {
#         "context": docs
#     }


def chatbot(state: State):

    # Convert documents into text
    context = "\n\n".join(doc.page_content for doc in state["context"])


    # Send context + question to LLM
    response = llm.invoke(
        f"""
        Context:
        {context}

        Question:
        {state["question"]}
        """
    )

    # Return final answer
    return {
        "answer": response.content
    }



builder = StateGraph(State)

# Add Nodes
builder.add_node("retriever", retrieve)

builder.add_node("chatbot", chatbot)

# Graph Flow
builder.add_edge(START, "retriever")

builder.add_edge("retriever", "chatbot")

builder.add_edge("chatbot", END)

# Compile
graph = builder.compile()



result = graph.invoke({

    "question": "what is loan policy in short"

})



print("\nAnswer:\n")

print(result["answer"])