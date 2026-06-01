from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


def run_executor(goal: str, subtasks: str, research: str, llm: ChatGroq) -> str:
    messages = [
        SystemMessage(content=(
            "You are an execution agent. Given a goal, subtasks, and research findings, "
            "produce a detailed step-by-step execution plan. For each subtask, provide: "
            "what to do, how to do it, estimated time, and any tools or resources needed. "
            "Format each step clearly with headers."
        )),
        HumanMessage(content=(
            f"Goal: {goal}\n\n"
            f"Subtasks:\n{subtasks}\n\n"
            f"Research Findings:\n{research}"
        )),
    ]
    response = llm.invoke(messages)
    return response.content
