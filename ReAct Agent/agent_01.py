from langchain.agents import create_agent
from langchain_core.tools import tool


# Define a tool that the agent can use
@tool
def calculator(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Define weather tool
@tool
def get_weather(city: str) -> str:
    """Get weather information for a city."""
    return f"The weather in {city} is sunny."
  
# Create an agent by connecting the LLM and tools
agent = create_agent(
    model="openai:gpt-5.5",              # LLM model
    tools=[calculator, get_weather],                  # Tools available to the agent
    system_prompt="You are a helpful assistant."  # Agent behavior
)


# Send the user's question to the agent
result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is 10 + 20?"
        }
    ]
})


# Print final response
print(result["messages"][-1].content)

"""
Short Purpose

This code creates a basic AI agent that can use an external tool (calculator, weather) to answer the user's question.

Flow:
User Question → Agent → Decide Tool → Calculator or weather → Final Answer
"""
