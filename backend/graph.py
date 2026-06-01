from typing import TypedDict, AsyncGenerator
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from agents.planner import run_planner
from agents.researcher import run_researcher
from agents.executor import run_executor
from agents.summarizer import run_summarizer


class PlannerState(TypedDict):
    goal: str
    subtasks: str
    research: str
    execution_plan: str
    final_summary: str


def build_graph(llm: ChatGroq) -> StateGraph:
    def planner_node(state: PlannerState) -> PlannerState:
        result = run_planner(state["goal"], llm)
        return {**state, "subtasks": result}

    def researcher_node(state: PlannerState) -> PlannerState:
        result = run_researcher(state["goal"], state["subtasks"], llm)
        return {**state, "research": result}

    def executor_node(state: PlannerState) -> PlannerState:
        result = run_executor(state["goal"], state["subtasks"], state["research"], llm)
        return {**state, "execution_plan": result}

    def summarizer_node(state: PlannerState) -> PlannerState:
        result = run_summarizer(
            state["goal"], state["subtasks"],
            state["research"], state["execution_plan"], llm
        )
        return {**state, "final_summary": result}

    graph = StateGraph(PlannerState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("executor", executor_node)
    graph.add_node("summarizer", summarizer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "executor")
    graph.add_edge("executor", "summarizer")
    graph.add_edge("summarizer", END)

    return graph.compile()


async def stream_plan(goal: str, llm: ChatGroq) -> AsyncGenerator[dict, None]:
    app = build_graph(llm)
    state = {
        "goal": goal,
        "subtasks": "",
        "research": "",
        "execution_plan": "",
        "final_summary": "",
    }

    agent_labels = {
        "planner": ("Planner Agent", "subtasks"),
        "researcher": ("Researcher Agent", "research"),
        "executor": ("Executor Agent", "execution_plan"),
        "summarizer": ("Summarizer Agent", "final_summary"),
    }

    async for event in app.astream(state):
        for node_name, node_state in event.items():
            if node_name in agent_labels:
                label, key = agent_labels[node_name]
                yield {"agent": label, "output": node_state.get(key, "")}
