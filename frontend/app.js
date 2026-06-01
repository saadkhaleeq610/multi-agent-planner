const AGENT_MAP = {
  "Planner Agent": "planner",
  "Researcher Agent": "researcher",
  "Executor Agent": "executor",
  "Summarizer Agent": "summarizer",
};

function setStatus(key, status) {
  const el = document.getElementById(`status-${key}`);
  el.textContent = status === "running" ? "Running..." : status === "done" ? "Done" : "Waiting";
  el.className = `agent-status ${status}`;
}

function setCardState(key, state) {
  const card = document.getElementById(`card-${key}`);
  card.className = `agent-card ${state}`;
}

function showOutput(key, text) {
  const el = document.getElementById(`output-${key}`);
  el.textContent = text;
  el.classList.add("visible");
}

function resetUI() {
  Object.values(AGENT_MAP).forEach((key) => {
    setStatus(key, "waiting");
    setCardState(key, "");
    const out = document.getElementById(`output-${key}`);
    out.textContent = "";
    out.classList.remove("visible");
  });
  document.getElementById("finalResult").classList.add("hidden");
  document.getElementById("finalContent").textContent = "";
}

async function startPlanning() {
  const goal = document.getElementById("goalInput").value.trim();
  if (!goal) return;

  const btn = document.getElementById("planBtn");
  btn.disabled = true;
  btn.textContent = "Planning...";

  resetUI();
  document.getElementById("pipeline").classList.remove("hidden");

  try {
    const response = await fetch("http://localhost:8000/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const json = line.replace(/^data:\s*/, "").trim();
        if (!json) continue;

        try {
          const event = JSON.parse(json);
          handleEvent(event);
        } catch {}
      }
    }
  } catch (err) {
    alert("Error connecting to backend. Make sure the server is running.");
  }

  btn.disabled = false;
  btn.textContent = "Generate Plan";
}

let lastActiveKey = null;

function handleEvent(event) {
  const { agent, output } = event;

  if (agent === "done") return;
  if (agent === "error") {
    alert("Agent error: " + output);
    return;
  }

  if (lastActiveKey) {
    setStatus(lastActiveKey, "done");
    setCardState(lastActiveKey, "done");
  }

  const key = AGENT_MAP[agent];
  if (!key) return;

  setStatus(key, "running");
  setCardState(key, "active");
  showOutput(key, output);
  lastActiveKey = key;

  if (agent === "Summarizer Agent") {
    setTimeout(() => {
      setStatus(key, "done");
      setCardState(key, "done");
      document.getElementById("finalContent").textContent = output;
      document.getElementById("finalResult").classList.remove("hidden");
      lastActiveKey = null;
    }, 300);
  }
}

document.getElementById("goalInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    startPlanning();
  }
});
