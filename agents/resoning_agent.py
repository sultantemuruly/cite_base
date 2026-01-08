import os
from typing import Optional, Literal, Annotated
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_tavily import TavilySearch

class FinalAnswer(TypedDict):
    final_answer: Annotated[str, "The final answer to the user's question"]


def read_markdown_file(filepath):
    """Reads the content of a Markdown file as a string."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    except FileNotFoundError:
        return f"Error: The file at {filepath} was not found."
    except Exception as e:
        return f"An error occurred: {e}"


@tool
def can_perform_web_search() -> bool:
    """
    Check if web search can be performed.
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        return False
    return True


@tool
def web_search(
    query: Annotated[str, "The search query"],
    topic: Annotated[
        Optional[Literal["general", "news", "finance"]], "The topic to search within"
    ] = "general",
    max_results: Annotated[
        Optional[int], "The maximum number of results to return"
    ] = 5,
) -> list[dict]:
    """
    Search the web using TavilySearch.
    You can specify a topic and the maximum number of results to return in order to refine the search.
    """
    search = TavilySearch(max_results=max_results, topic=topic)
    results = search.run(query)
    return results


def create_reasoning_agent():
    """Create reasoning agent without static system prompt (will be set dynamically)."""
    model = init_chat_model(model="gpt-4o-mini")
    tools = [web_search, can_perform_web_search]

    agent = create_agent(
        model=model,
        tools=tools,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "can_perform_web_search": False,
                    "web_search": {"allowed_decisions": ["approve", "reject"]},
                },
                description_prefix="Tool execution pending approval",
            )
        ],
        response_format=FinalAnswer,
        checkpointer=InMemorySaver(),
    )

    return agent
