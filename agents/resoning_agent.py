import os
from typing import Optional, Literal, Annotated

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_tavily import TavilySearch

user_question = "What is the self attention mechanism and how does it work in transformer models, also how anthropic explains it?"
context = [
    {
        "sub_query": "self attention mechanism definition and purpose",
        "retrieved_context": "Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence (Vaswani et al., 2017, Section 2). The Transformer uses self-attention in encoder and decoder layers to allow each position to attend to all positions in the previous layer, enabling modeling of dependencies without recurrence (Vaswani et al., 2017, Section 3.2.3). Self-attention connects all positions with a constant number of sequential operations, improving parallelization and shortening path lengths for long-range dependencies compared to recurrent layers (Vaswani et al., 2017, Section 4).",
        "citations": [
            "Vaswani et al., 2017 - Attention Is All You Need; Section 2, 3.2.3, 4; https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"
        ],
        "synthesized_answer": "Self-attention (intra-attention) relates positions within a single sequence to compute contextualized representations, enabling the model to represent each token with information from all other tokens in the sequence [Vaswani et al., 2017, Section 2].",
    },
    {
        "sub_query": "self attention operation within transformer architecture",
        "retrieved_context": "In a self-attention layer all keys, values and queries come from the same source (the previous layer) and each position can attend to all positions in that layer; in the decoder self-attention is masked to prevent leftward (future) information flow and the model also uses encoder-decoder attention where decoder queries attend encoder keys/values (Vaswani et al., 2017, Section 3.2.3). The Transformer implements multi-head attention and scaled dot-product attention to compute weights and aggregate values, enabling parallel computation and flexible representation learning (Vaswani et al., 2017, Sections 3.2.3 and 4).",
        "citations": [
            "Vaswani et al., 2017 - Attention Is All You Need; Section 3.2.3, 4; https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"
        ],
        "synthesized_answer": "Transformer self-attention forms queries, keys, and values from the same input, computes attention weights (e.g., scaled dot-product, often via multiple heads), applies those weights to values to produce context-aware outputs, uses masking in decoder self-attention to preserve autoregression, and includes encoder–decoder attention to let the decoder attend to encoder outputs [Vaswani et al., 2017, Sections 3.2.3 and 4].",
    },
]


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
    model = init_chat_model(model="gpt-5-mini")
    tools = [web_search, can_perform_web_search]
    reasoning_prompt = read_markdown_file("../prompts/reasoning_prompt.md")

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
        checkpointer=InMemorySaver(),
    )

    return agent, reasoning_prompt
