from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


def run_planner(goal: str, llm: ChatGroq) -> str:
    messages = [
        SystemMessage(content=(
            "You are a task planning agent. Given a user goal, break it down into "
            "3-6 clear, actionable subtasks. Return them as a numbered list. "
            "Be specific and practical."
        )),
        HumanMessage(content=f"Goal: {goal}"),
    ]
    response = llm.invoke(messages)
    return response.content
