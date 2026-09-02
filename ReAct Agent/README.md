## Difference Between the Two Approaches

### 1. Using `create_agent()`

```text
create_agent()
     ↓
Agent internally manages
LLM + Tools + Tool Calling + Flow
```

* Simple and easy to implement.
* The agent workflow is mostly handled internally.
* Best when you want to quickly build an agent.

### 2. Using `StateGraph()`

```text
START
  ↓
Chatbot (LLM)
  ↓
Tool Required?
 ↙          ↘
YES          NO
 ↓            ↓
Tool         END
 ↓
LLM
 ↓
END
```

* The agent workflow is explicitly defined.
* We manually define `State`, `Nodes`, `Edges`, and `Conditional Edges`.
* `ToolNode` handles tool execution.
* `should_continue()` decides whether to call a tool or finish.

### Key Difference

**`create_agent()` → Use the agent.**

**`StateGraph()` → Build and control the agent workflow.**

For learning LangGraph and understanding how ReAct agents work internally, the `StateGraph()` approach is more important.

### Quick Comparison

| First Approach | StateGraph Approach |
|---|---|
| Uses `create_agent()` | Uses `StateGraph()` manually |
| LangGraph internal flow is mostly hidden | LangGraph flow is explicitly defined |
| Simple implementation | ReAct architecture is clearly visible |
| Tool calling is handled internally | Tool execution is handled using `ToolNode` |
| Conditional decision is handled internally | `should_continue()` is defined manually |
| Easier for quick implementation | More important for understanding the architecture |
| Best for using an agent | Best for building and controlling the agent workflow |


## 03. Agent Memory & Checkpointing

Added short-term memory to the LangGraph ReAct agent using `InMemorySaver`.

- `InMemorySaver` stores conversation state.
- `thread_id` identifies a conversation.
- The same `thread_id` allows the agent to remember previous messages.

### Flow

User → State → LLM/Tool → Checkpoint → Next Message → Previous Context

### Production Consideration

For production, `InMemorySaver` can be replaced with a persistent checkpointer.

Common options:

1. **PostgreSQL** — Reliable relational database and commonly used for production.
2. **DynamoDB** — Good choice for AWS/serverless applications. 
3. **Redis** — Useful for fast, low-latency state/session storage.
4. **MongoDB** — Suitable for document-based applications.

## 04. Error Handling

Added error handling to the LangGraph ReAct agent using `ToolNode`.

- `handle_tool_errors=True` prevents the agent from crashing when a tool fails.
- Tool errors are converted into a message that the LLM can understand.
- The LLM can then decide how to respond to the error.

### Flow

User → LLM → Tool → Error → ToolNode Handles Error → LLM → Final Response

> Note: `handle_tool_errors=True` provides error handling, not automatic retry.

## 04. Retry Policy
Added a retry policy to the LangGraph ReAct agent.

- `RetryPolicy` automatically retries a failed node.
- `max_attempts=3` allows up to 3 total execution attempts.
- Useful for handling temporary LLM or node failures.

### Flow

LLM Node → Failure → Retry → Retry → Success / Final Failure

> Note: Retry Policy handles retryable node failures, while `handle_tool_errors=True` handles tool errors.

## 05. Human-in-the-Loop (HITL)

Added Human-in-the-Loop approval to the LangGraph ReAct agent.

- `interrupt()` pauses the agent and waits for human input.
- `Command(resume="yes")` resumes the paused execution.
- `thread_id` maintains the same conversation state.
- Checkpointing allows the agent to pause and resume safely.

### Flow

User → LLM → Tool Call → `interrupt()` → Human Approval → `Command(resume)` → Tool → LLM → Final Answer

### Key Concepts

- **`interrupt()`** → Pause agent execution.
- **`Command(resume=...)`** → Resume execution after human input.
- **Checkpointer** → Saves the agent state while paused.
- **`thread_id`** → Identifies the conversation/execution.

> HITL is useful when an agent needs human approval before performing sensitive or important actions.

## 06. LangSmith Observability

Added LangSmith tracing to monitor and debug the LangGraph ReAct agent.

- Loads LangSmith configuration from `.env`.
- `LANGSMITH_TRACING=true` enables tracing.
- `LANGSMITH_PROJECT` groups agent runs under a project.
- LangSmith helps track LLM calls, tool calls, latency, and errors.

### `.env`

```env
LANGSMITH_API_KEY=your_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langgraph-react-agent

### Environment Variables

```python
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
```

## ReAct Agent with LangGraph

Implemented a basic ReAct Agent using `StateGraph`, `ToolNode`, and LLM tool calling.

### Key Components

- **LLM** → Decides whether a tool is required.
- **Tool** → Performs the required action.
- **State** → Maintains conversation messages.
- **ToolNode** → Executes tool calls.
- **Conditional Routing** → Decides between tool execution and final answer.
- **ReAct Loop** → LLM → Tool → LLM → Final Answer.

### Flow

User → LLM → Tool Decision → ToolNode → Tool Result → LLM → Final Answer

### Purpose

This implementation demonstrates the core ReAct agent architecture explicitly using LangGraph.
