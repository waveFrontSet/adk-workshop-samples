# ADK Workshop Slide Brief for Claude Design

**Workshop Title:** Custom Tools, Callbacks, and Trade-Offs
**Duration:** 60 minutes
**Audience:** Power users with Python and GCP familiarity
**Slide tool:** Claude Design (use clean, minimal slide layouts; dark or light theme at your discretion)

---

## Section 1: ADK Architecture Overview (12 min, ~10-12 slides)

### Goal
Give participants a mental model of how ADK is structured. This is not exhaustive — focus on the pieces that matter for the rest of the workshop.

### Slide 1-1: Title Slide
- Workshop title: "Custom Tools, Callbacks, and Trade-Offs"
- Subtitle: "A technical deep dive into the Agent Development Kit (ADK)"
- Speaker name placeholder

### Slide 1-2: What is ADK?
- "Build, Evaluate, and Deploy agents, seamlessly"
- Open-source framework by Google for building AI agents
- Available in Python, TypeScript, Go, Java (workshop uses Python)
- Docs: https://adk.dev

### Slide 1-3: ADK Component Map
Recreate the component grid from the ADK docs (see screenshot reference). Highlight these with visual emphasis:
- **Agents** (top-left)
- **Tool** (top)
- **Callbacks** (top-right)
- **Orchestration** (top)
- **Deployment** (middle-right)

Grey out / de-emphasize the rest (Bidirectional Streaming, Evaluation, Artifact Management, Memory, Code Execution, Planning). Keep Debugging, Trace, Models as background layers.

### Slide 1-4: Agent Types
Two categories:
1. **LlmAgent** — uses an LLM for reasoning, non-deterministic
   - Has: `name`, `model`, `instruction`, `description`, `tools`
2. **Workflow Agents** — deterministic orchestration, no LLM
   - `SequentialAgent`, `ParallelAgent`, `LoopAgent`

Code snippet (minimal):
```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant.",
    tools=[my_tool],
)
```

### Slide 1-5: How Agents Work — The Event Loop
Simple diagram showing the cycle:
```
User Message → Runner → Agent → LLM → Tool Call? → Tool → LLM → Response → Event
```
Key concepts to label:
- **Runner**: manages execution flow
- **Session**: conversation context + state
- **Event**: unit of communication (user message, agent reply, tool use)

### Slide 1-6: Tools — The Agent's Hands
- Tools let agents do things beyond conversation
- Types available in ADK:
  - **FunctionTool** — wrap a Python function (today's focus)
  - **AgentTool** — use another agent as a tool
  - **MCP Tools** — Model Context Protocol integration
  - **OpenAPI Tools** — from OpenAPI specs
- The LLM decides which tool to call based on function name, docstring, and parameter schema

### Slide 1-7: Orchestration
- **LLM-driven routing**: the LLM decides which sub-agent handles a request (based on agent `description`)
- **Workflow agents**: you decide the execution pattern
  - Sequential: A then B then C
  - Parallel: A and B at the same time
  - Loop: repeat until condition met
- Can be combined: workflow agents orchestrate LlmAgents

### Slide 1-8: Callbacks (Preview)
- Custom code that runs at specific points in the agent lifecycle
- 6 callback hooks available (covered in detail in Section 3)
- Teaser: "Callbacks are the primary mechanism for customisation in high-code agents — and the primary source of maintenance debt"

### Slide 1-9: Deployment Options
- **Agent Runtime (Agent Engine)** — managed GCP service, today's focus
- **Cloud Run** — containerised, more control
- **GKE** — full Kubernetes, maximum control
- Agent Runtime enables integration with **Gemini Enterprise**

### Slide 1-10: Key Takeaway
- ADK gives you a spectrum: from simple single-agent + tool setups to complex multi-agent orchestrations
- Today we focus on the "high-code" end: custom tools, callbacks, and deployment to Agent Engine

---

## Section 2: Custom Tools Deep Dive (12 min, ~8-10 slides)

### Goal
Show participants how to build function tools, how the LLM interacts with them, and when to use different tool types.

### Slide 2-1: Section Title
"Custom Tools"

### Slide 2-2: Anatomy of a Function Tool
The LLM uses **three things** to understand a tool:
1. Function **name**
2. Function **docstring** (becomes the tool description)
3. Parameter **type hints** and **defaults** (become the schema)

```python
def get_weather(city: str, unit: str = "Celsius") -> dict:
    """
    Retrieves the current weather for a city.

    Args:
        city: The city name (e.g., "Berlin").
        unit: Temperature unit, 'Celsius' or 'Fahrenheit'.
    """
    # ... your logic here ...
    return {"status": "success", "temp": 22, "unit": unit}
```

Highlight: ADK auto-wraps this as a `FunctionTool` when you pass it to `tools=[]`.

### Slide 2-3: Required vs Optional Parameters
| Parameter | Type hint | Default | LLM must provide? |
|---|---|---|---|
| `city` | `str` | none | Yes (required) |
| `unit` | `str` | `"Celsius"` | No (optional) |
| `bio` | `Optional[str]` | `None` | No (optional) |

Rule: no default = required. The LLM gets an error if it omits a required param.

### Slide 2-4: Return Values Matter
- Preferred return type: **dict**
- Non-dict returns get wrapped as `{"result": <value>}`
- Include a `"status"` key — the LLM needs to understand outcomes
- Descriptive error messages > error codes (the LLM reads these, not code)

```python
# Good
return {"status": "error", "message": "City not found in database"}

# Bad
return -1
```

### Slide 2-5: Complete Example — Agent with Tool

```python
from google.adk.agents import LlmAgent

def get_capital_city(country: str) -> str:
    """Retrieves the capital city for a given country."""
    capitals = {"france": "Paris", "japan": "Tokyo"}
    return capitals.get(
        country.lower(),
        f"Sorry, I don't know the capital of {country}."
    )

agent = LlmAgent(
    name="capital_agent",
    model="gemini-2.5-flash",
    instruction="""You are an agent that provides capital cities.
    Use the get_capital_city tool to answer questions.""",
    tools=[get_capital_city],
)
```

### Slide 2-6: Passing Data Between Tools
- Tools within a single turn share the same `InvocationContext`
- Use `temp:` prefix in session state for ephemeral data passing:

```python
def tool_a(tool_context):
    tool_context.state["temp:intermediate"] = some_value

def tool_b(tool_context):
    value = tool_context.state["temp:intermediate"]
```

- `temp:` data is discarded after the invocation

### Slide 2-7: Agent-as-a-Tool
- Use another agent as a tool (via `AgentTool`)
- Key difference from sub-agents: AgentTool gets a **fresh, isolated context** — it doesn't see the parent's conversation history
- Use case: call a specialist agent for a one-off task without polluting the main conversation

### Slide 2-8: Tool Selection — When to Use What

| Need | Tool type |
|---|---|
| Custom business logic | FunctionTool |
| Delegate to a specialist agent | AgentTool |
| External tool server (standardised) | MCP Tools |
| Existing REST API with spec | OpenAPI Tools |

### Slide 2-9: Tool Best Practices
- Write thorough docstrings — they are your tool's UX for the LLM
- Use explicit type hints on all parameters
- Return dicts with descriptive keys
- Keep tools focused — one function, one purpose
- Test tools independently before wiring them to agents

Docs reference: https://adk.dev/tools-custom/function-tools/

---

## Section 3: Callbacks — Mechanics and Patterns (12 min, ~10-12 slides)

### Goal
This is the core of the abstract. Show all 6 callback types, real patterns, and explicitly discuss the maintenance implications.

### Slide 3-1: Section Title
"Callbacks: Mechanics and Patterns"

### Slide 3-2: What Are Callbacks?
- Custom functions you attach to an agent
- They fire at specific lifecycle points
- They can:
  - **Inspect** data (logging, monitoring)
  - **Modify** data (request/response transformation)
  - **Block** execution (guardrails, policy enforcement)
  - **Short-circuit** the agent (return early with custom response)

### Slide 3-3: The 6 Callback Hooks — Diagram
Create a visual showing the agent lifecycle with callback insertion points:

```
                    ┌─ before_agent_callback
                    │
    User Message ──>│  Agent Execution
                    │    ┌─ before_model_callback
                    │    │
                    │    │  LLM Call
                    │    │
                    │    └─ after_model_callback
                    │
                    │    ┌─ before_tool_callback
                    │    │
                    │    │  Tool Execution
                    │    │
                    │    └─ after_tool_callback
                    │
                    └─ after_agent_callback
```

### Slide 3-4: Callback Signatures (Python)
Important: parameter names **must match exactly** (ADK passes by keyword).

| Callback | Parameters | Returns to skip |
|---|---|---|
| `before_agent_callback` | `callback_context` | `Content` |
| `after_agent_callback` | `callback_context` | `Content` |
| `before_model_callback` | `callback_context`, `llm_request` | `LlmResponse` |
| `after_model_callback` | `callback_context`, `llm_response` | `LlmResponse` |
| `before_tool_callback` | `tool`, `args`, `tool_context` | `dict` |
| `after_tool_callback` | `tool`, `args`, `tool_context`, `tool_response` | `dict` |

Gotcha: Using `ctx` instead of `callback_context` will cause a runtime `TypeError`.

### Slide 3-5: Pattern — Guardrails (before_model_callback)
Block requests containing sensitive content before they hit the LLM:

```python
def content_guardrail(callback_context, llm_request):
    """Block requests with forbidden keywords."""
    last_msg = llm_request.contents[-1].parts[0].text
    forbidden = ["password", "credit card", "ssn"]

    if any(word in last_msg.lower() for word in forbidden):
        return LlmResponse(
            content=Content(parts=[
                Part(text="I cannot process requests with sensitive data.")
            ])
        )
    return None  # proceed normally
```

Attach it:
```python
agent = LlmAgent(
    ...,
    before_model_callback=content_guardrail,
)
```

### Slide 3-6: Pattern — Logging (after_tool_callback)
Observe tool usage without modifying behaviour:

```python
def log_tool_usage(tool, args, tool_context, tool_response):
    """Log every tool call for observability."""
    print(f"[TOOL] {tool.name} called with {args}")
    print(f"[TOOL] Response: {tool_response}")
    return None  # don't modify anything
```

### Slide 3-7: Pattern — Conditional Skip (before_agent_callback)
Skip an agent entirely based on session state:

```python
def check_if_agent_should_run(callback_context):
    """Skip agent if state flag is set."""
    if callback_context.state.get("skip_agent", False):
        return Content(
            parts=[Part(text="Agent skipped due to state condition.")],
            role="model",
        )
    return None  # let it run
```

### Slide 3-8: Pattern — Request Modification (before_model_callback)
Dynamically inject context into the LLM request:

```python
def inject_user_context(callback_context, llm_request):
    """Add user preferences to system instruction."""
    lang = callback_context.state.get("user_language", "en")
    if lang != "en":
        llm_request.config.system_instruction += (
            f"\nRespond in language: {lang}"
        )
    return None  # proceed with modified request
```

### Slide 3-9: Pattern — Caching (before/after_tool_callback pair)
Avoid redundant API calls:

```python
def cache_check(tool, args, tool_context):
    key = f"cache:{tool.name}:{args}"
    cached = tool_context.state.get(key)
    if cached:
        return cached  # skip tool execution
    return None

def cache_store(tool, args, tool_context, tool_response):
    key = f"cache:{tool.name}:{args}"
    tool_context.state[key] = tool_response
    return None
```

### Slide 3-10: Callback Design Best Practices
From the ADK docs (https://adk.dev/callbacks/design-patterns-and-best-practices/):

1. **Single responsibility** — one callback, one purpose
2. **Performance aware** — callbacks run synchronously; avoid blocking I/O
3. **Error handling** — always use try/except; don't crash the agent
4. **State hygiene** — use specific keys, consider prefixes (`temp:`, `app:`, `user:`)
5. **Idempotency** — design for safe retries if callbacks have side effects
6. **Test independently** — unit test with mock contexts before integration

### Slide 3-11: The Maintenance Warning
This slide is critical to the abstract's promise.

**Callbacks are invisible control flow.**

- They don't appear in the agent's instruction or tool list
- A new developer reading the code sees the agent definition but not the 6 callbacks scattered across files that modify its behaviour
- They compose unpredictably: a `before_model_callback` that modifies the request + an `after_model_callback` that modifies the response = hard to debug
- No built-in mechanism to see "what callbacks fired in what order" without custom logging
- Compare to: middleware in web frameworks — same power, same footgun

**Ask the audience:** "How do you document and test middleware in your web services? Apply the same rigour here."

---

## Section 4: Live Demo — Agent to Deployment (12 min, ~4-6 slides + live terminal)

### Goal
Walk through a pre-built agent project, run it locally, then show a pre-deployed instance on Agent Engine.

### Preparation Notes for Presenter
- **Pre-build** the project before the workshop
- **Pre-deploy** to Agent Engine before the workshop (deployment takes 5-10 min)
- Have a **pre-recorded 2-min screencast** of the deployment as backup
- Have the Agent Engine console open in a browser tab

### Slide 4-1: Section Title
"From Code to Production"

### Slide 4-2: Project Structure
Show the standard ADK project layout:

```
my_agent/
├── .env              # GOOGLE_API_KEY or auth config
├── __init__.py        # exports `root_agent`
└── agent.py           # agent definition + tools
```

The `__init__.py` must export `root_agent`:
```python
from .agent import root_agent
```

### Slide 4-3: Running Locally
Two options:
```bash
# Web UI (interactive, good for debugging)
adk web my_agent

# CLI (quick testing)
adk run my_agent
```

The web UI at `localhost:8000` shows:
- Agent conversation
- Event inspection
- State changes
- Tool call details

### Slide 4-4: Deploying to Agent Engine
Prerequisites:
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project MY-PROJECT-ID
```

Deploy command:
```bash
adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=us-central1 \
    --display_name="Workshop Agent" \
    my_agent
```

Output gives you a `RESOURCE_ID` for the deployed agent.

Docs: https://adk.dev/deploy/agent-runtime/deploy/

### Slide 4-5: Agent Engine in the Console
- Show screenshot/live view of Agent Engine UI at:
  `console.cloud.google.com/vertex-ai/agents/agent-engines`
- Show the deployed agent with its resource ID
- Mention: once deployed, the agent is available via REST API and can be integrated into Gemini Enterprise

### Slide 4-6: Querying the Deployed Agent
REST endpoint structure:
```
https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}:query
```

Or via Python SDK:
```python
import vertexai

agent_engine = vertexai.agent_engines.get(
    "projects/{PROJECT}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
)
```

---

## Section 5: Trade-Offs Discussion (7 min, ~5-6 slides)

### Goal
This section delivers on the abstract's promise of "actively balancing benefits against realities of long-term code maintenance."

### Slide 5-1: Section Title
"Trade-Offs: When High-Code Makes Sense"

### Slide 5-2: The ADK Spectrum
Visual showing a spectrum:

```
No-code ◄───────────────────────────────────► High-code

Gemini         ADK with         ADK with         Custom
Enterprise     basic tools      callbacks +       agent
Agent Designer (some code)      orchestration     framework
(no code)                       (lots of code)

Faster setup                               Full control
Less maintenance                           More maintenance
Less customisation                         More customisation
```

Note: we explored the boundaries of Agent Designer in a previous workshop.

### Slide 5-3: The No-Code / High-Code Wall
**Important limitation in the current version of Gemini Enterprise:**

No-code and high-code agents **cannot be mixed**.
- You cannot use a high-code ADK agent as a sub-agent inside Agent Designer
- You cannot call an Agent Designer (no-code) agent as a sub-agent or AgentTool from ADK

This means the choice between no-code and high-code is currently an **either/or decision per agent**, not a spectrum you can blend freely. Plan accordingly.

### Slide 5-4: When to Use ADK High-Code
Good fit:
- Custom business logic tools that can't be expressed as API calls
- Guardrails that must run deterministically (not prompt-based)
- Complex multi-agent orchestration with specific sequencing
- Need for fine-grained observability (callback-based logging)
- Deployment to Agent Engine for Gemini Enterprise integration

Bad fit:
- Simple Q&A over documents (use Agent Designer)
- Prototyping (use Vertex AI Studio or adk web locally)
- When your team doesn't have Python expertise to maintain it

### Slide 5-5: Maintenance Realities
Concrete costs to acknowledge:

| Aspect | Cost |
|---|---|
| **Callbacks** | Invisible control flow; requires documentation discipline |
| **Custom tools** | Every tool is code you own: bugs, API changes, test coverage |
| **Orchestration** | Multi-agent systems are hard to debug; failures cascade |
| **Deployment** | Agent Engine abstracts infra but not your code's correctness |
| **Testing** | No standard test harness for agent behaviour; you build your own |
| **Versioning** | Agent behaviour changes when the underlying LLM model changes |

### Slide 5-6: Deployment Target Comparison

| | Agent Engine | Cloud Run | GKE |
|---|---|---|---|
| Setup effort | Low | Medium | High |
| Scaling | Managed | Managed | Self-managed |
| Gemini Enterprise | Yes | No | No |
| Cost control | Limited | Good | Full |
| Custom runtime | No | Yes | Yes |
| When to use | Enterprise integration, quick deploy | Production APIs, custom domains | Full control, multi-cloud |

Docs references:
- Agent Engine: https://adk.dev/deploy/agent-runtime/deploy/
- Cloud Run: https://adk.dev/deploy/cloud-run/
- GKE: https://adk.dev/deploy/gke/

---

## Section 6: Q&A Buffer (5 min)

### Slide 6-1: Resources
- ADK Docs: https://adk.dev
- GitHub: https://github.com/google/adk-python
- Quickstart: https://adk.dev/get-started/python/
- Callbacks reference: https://adk.dev/callbacks/types-of-callbacks/
- Callback patterns: https://adk.dev/callbacks/design-patterns-and-best-practices/
- Custom tools: https://adk.dev/tools-custom/function-tools/
- Deployment: https://adk.dev/deploy/agent-runtime/deploy/

### Slide 6-2: Q&A
"Questions?"

---

## Design Notes for Claude Design

### Visual Style
- Clean, minimal, professional
- Use code blocks with syntax highlighting where shown
- Diagrams should be simple boxes + arrows, not overly polished
- Consistent colour coding: use one accent colour for "callbacks", another for "tools", a third for "agents"
- Slide count target: ~40-45 slides total (some will be quick transitions)

### Code Snippets
- All code is Python
- Use `gemini-2.5-flash` as the model name in all examples
- Keep imports minimal — only show what's needed for the snippet
- Use comments sparingly — the slide text provides context

### Pacing Notes (for presenter reference, not on slides)
- Section 1: ~1 slide per minute, mostly talking over diagrams
- Section 2: ~1.5 min per slide, code walkthrough pace
- Section 3: ~1 min per slide, code + discussion mix
- Section 4: mostly live terminal, slides are waypoints
- Section 5: discussion-heavy, fewer slides, more audience interaction
