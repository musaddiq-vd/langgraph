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
