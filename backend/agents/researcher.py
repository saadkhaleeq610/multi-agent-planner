from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 4) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        return "\n\n".join(
            f"**{r['title']}**\n{r['body']}" for r in results
        )
    except Exception as e:
        return f"Search failed: {str(e)}"


def run_researcher(goal: str, subtasks: str, llm: ChatGroq) -> str:
    query = f"{goal} how to guide steps"
    search_results = search_web(query)

    messages = [
        SystemMessage(content=(
            "You are a research agent. You have been given a goal, a list of subtasks, "
            "and web search results. Extract the most relevant facts, tips, and resources "
            "that will help accomplish the goal. Be concise and structured."
        )),
        HumanMessage(content=(
            f"Goal: {goal}\n\n"
            f"Subtasks:\n{subtasks}\n\n"
            f"Search Results:\n{search_results}"
        )),
    ]
    response = llm.invoke(messages)
    return response.content
