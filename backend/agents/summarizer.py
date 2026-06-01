from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


def run_summarizer(goal: str, subtasks: str, research: str, execution_plan: str, llm: ChatGroq) -> str:
    messages = [
        SystemMessage(content=(
            "You are a summarizer agent. Compile all the work done by the planning, "
            "research, and execution agents into a clean, final action plan. "
            "Structure it with: an executive summary, key findings, and a final checklist. "
            "Make it actionable and easy to follow."
        )),
        HumanMessage(content=(
            f"Goal: {goal}\n\n"
            f"Subtasks:\n{subtasks}\n\n"
            f"Research:\n{research}\n\n"
            f"Execution Plan:\n{execution_plan}"
        )),
    ]
    response = llm.invoke(messages)
    return response.content
