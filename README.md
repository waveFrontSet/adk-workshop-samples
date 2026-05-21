# ADK Workshop: Custom Tools, Callbacks, and Multi-Agent Architectures

Hands-on examples for the Agent Development Kit (ADK) workshop. Each example
is a self-contained ADK agent package that can be run locally or in GCP Cloud
Shell using `adk web`.

## Examples

### `simple_tool` -- A minimal agent with a function tool

A weather assistant backed by a single `get_weather` function tool. The tool
returns mock data for Berlin and Tokyo and an error for anything else. This
example shows how ADK auto-wraps a plain Python function as a `FunctionTool`
and how the LLM uses the function name, docstring, and type hints to decide
when and how to call it.

### `callbacks` -- Guardrails and tool logging via callbacks

Builds on the same weather tool but adds three callbacks:

- **`before_model_callback` (input guardrail):** Scans the user's message for
  a blocklist of sensitive or malicious phrases (e.g. "ignore previous
  instructions", "drop table", "credit card"). If a match is found, the LLM
  call is skipped entirely and a refusal message is returned. In production
  you would use a dedicated service like LLM Guard or Model Armor instead of
  keyword matching.
- **`before_tool_callback` (request logger):** Prints the tool name and
  arguments before every tool call.
- **`after_tool_callback` (response logger):** Prints the tool name and
  response after every tool call.

Demonstrates how callbacks can inspect, modify, or block execution at
different lifecycle points, and highlights the importance of using the exact
parameter names (`callback_context`, `llm_request`, `tool`, `args`,
`tool_context`, `tool_response`).

### `subagents` -- Multi-agent with sub-agents (LLM-driven delegation)

A customer service bot for a meal kit delivery service, built as a coordinator
with two sub-agents:

- **`greeter_agent` (root):** Greets the customer and determines intent.
  Transfers to the appropriate sub-agent using `transfer_to_agent`.
- **`order_agent`:** Walks the customer through placing a new order -- meal
  selection from a menu, number of servings, delivery date -- then submits it
  via a `place_order` tool.
- **`status_agent`:** Asks for an order ID and looks it up via a
  `check_order_status` tool against a mock database.

Sub-agents share the full conversation history. The LLM decides which
sub-agent to transfer to based on each agent's `description`. This pattern is
a good fit for multi-turn conversational flows where context continuity
matters.

### `agent_tools` -- Multi-agent with AgentTool (isolated expert consultation)

A kitchen assistant that consults two domain experts, each wrapped as an
`AgentTool`:

- **`nutrition_expert`:** Looks up calories, protein, carbs, and fat for
  common ingredients via a `lookup_nutrition` tool.
- **`recipe_expert`:** Suggests recipes based on a main ingredient via a
  `search_recipes` tool.

Unlike sub-agents, each `AgentTool` call gets a fresh, isolated context -- the
expert does not see the parent's conversation history. This pattern is a good
fit for stateless, single-question consultations ("ask a question, get an
answer, continue").

### Sub-agents vs. AgentTool -- when to use which

| | Sub-agents | AgentTool |
|---|---|---|
| Conversation history | Shared with parent | Fresh/isolated per call |
| Routing mechanism | LLM calls `transfer_to_agent` | LLM calls the tool like a function |
| Context continuity | Full -- multi-turn flows work naturally | None -- each call is independent |
| Use case | Conversational workflows, multi-step flows | One-off expert consultations, stateless queries |

---

## Setup

### Prerequisites

- Python 3.13+
- One of the following authentication methods:
  - A **Gemini API key** from
    [Google AI Studio](https://aistudio.google.com/app/apikey), or
  - A **GCP project** with the
    [Vertex AI API enabled](https://console.cloud.google.com/apis/enableflow;apiid=aiplatform.googleapis.com)
    and `gcloud` authenticated against it

### Authentication

ADK supports two backends for Gemini models. Pick the one that fits your
setup.

**Option 1: Google AI Studio (API key)**

Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey) and
create a `.env` file in each agent package directory:

```bash
cat > simple_tool/.env << 'EOF'
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-here
EOF
```

Then symlink it into the other packages:

```bash
for dir in callbacks subagents agent_tools; do
  ln -s ../simple_tool/.env "$dir/.env"
done
```

**Option 2: Vertex AI (GCP project + gcloud)**

Authenticate with a GCP project that has Vertex AI enabled:

```bash
gcloud auth login
gcloud auth application-default login
```

Then create a `.env` file:

```bash
cat > simple_tool/.env << 'EOF'
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
EOF
```

Symlink as above:

```bash
for dir in callbacks subagents agent_tools; do
  ln -s ../simple_tool/.env "$dir/.env"
done
```

---

### Option A: Local development

#### 1. Install `gcloud` CLI (if not already installed)

Follow the instructions at
<https://cloud.google.com/sdk/docs/install> for your platform.

#### 2. Install `uv` (if not already installed)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via Homebrew
brew install uv
```

See <https://docs.astral.sh/uv/getting-started/installation/> for other options.

#### 3. Clone and install dependencies

```bash
git clone https://github.com/waveFrontSet/adk-workshop-samples 
cd adk-workshop-samples
uv sync
```

#### 4. Authenticate and configure `.env`

Follow the [Authentication](#authentication) section above.

#### 5. Run an agent

```bash
uv run adk web simple_tool
```

Open <http://localhost:8000>, select the agent in the top-left corner, and start
chatting. Replace `simple_tool` with any of the other package names
(`callbacks`, `subagents`, `agent_tools`).

---

### Option B: GCP Cloud Shell

Cloud Shell comes with `gcloud`, `uv`, and Python pre-installed and already
authenticated with your GCP credentials.

#### 1. Open Cloud Shell

Go to <https://console.cloud.google.com> and click the **Activate Cloud Shell**
button (terminal icon in the top-right toolbar). Alternatively, open it
directly at <https://shell.cloud.google.com>.

#### 2. (Optional) Open the Cloud Shell IDE

For a full editor experience, click **Open Editor** in the Cloud Shell toolbar
or go to <https://ide.cloud.google.com>. You can switch between the terminal and
editor freely.

#### 3. Clone the repository

In the Cloud Shell terminal:

```bash
git clone https://github.com/waveFrontSet/adk-workshop-samples 
cd adk-workshop-samples
```

#### 4. Install dependencies

```bash
uv sync
```

#### 5. Authenticate and configure `.env`

Follow the [Authentication](#authentication) section above. Since Cloud Shell
is already authenticated with your GCP project, the Vertex AI option only
requires creating the `.env` file -- no additional `gcloud auth` commands
needed.

#### 6. Run an agent

```bash
uv run adk web simple_tool --port 8080 --allow_origins="*"
```

Cloud Shell will show a **Web Preview** button in the toolbar. Click it and
select **Preview on port 8080** to open the ADK web UI in your browser.

The `--allow_origins="*"` flag is required because Cloud Shell's Web Preview
serves the UI from a proxied `*.cloudshell.dev` URL, which ADK's CORS
middleware blocks by default (you'll see `403 Forbidden: origin not allowed`
on `POST /apps/.../sessions` without it). For a tighter setup, pass the exact
preview URL instead of `*`.

---

## Further reading

- [ADK documentation](https://adk.dev)
- [ADK Python quickstart](https://adk.dev/get-started/python/)
- [Custom function tools](https://adk.dev/tools-custom/function-tools/)
- [Types of callbacks](https://adk.dev/callbacks/types-of-callbacks/)
- [Callback patterns & best practices](https://adk.dev/callbacks/design-patterns-and-best-practices/)
- [Multi-agent systems](https://adk.dev/agents/multi-agents/)
