from typing_extensions import TypedDict
from typing import List, Any, Annotated
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from deepagents.middleware.subagents import SubAgentMiddleware

from utils.file_io import read_markdown_file


@dataclass
class Context:
    rag_chain: Annotated[Any, "The RAG chain to use for retrieval"]


class AggregatedContext(TypedDict):
    sub_query: Annotated[str, "The sub-query string"]
    retrieved_context: Annotated[str, "The retrieved context string"]
    citations: Annotated[List[str], "List of citation identifiers"]
    synthesized_answer: Annotated[str, "The synthesized answer string"]


class AggregatedContextList(TypedDict):
    results: Annotated[
        List[AggregatedContext], "List of aggregated context for each sub-query"
    ]


@tool
def retrieve_from_vectorstore(
    queries: Annotated[list[str], "The list of queries to retrieve answers for"],
    runtime: ToolRuntime[Context],
) -> dict:
    """Retrieve and generate answers from the vectorstore for a list of queries.
    This function invokes the RAG chain for each query and returns aggregated results.
    """

    rag_chain = runtime.context.rag_chain

    resp_dict = {}
    for query in queries:
        resp_dict[query] = rag_chain.invoke({"input": query})

    return resp_dict


def create_retrieval_orchestrator_agent():
    examples = read_markdown_file("../prompts/query_decomposition_examples.md")
    query_decomposition_prompt = read_markdown_file(
        "../prompts/query_decomposition_prompt.md"
    )
    query_decomposition_prompt = query_decomposition_prompt.format(examples=examples)
    query_decomposition_model = "gpt-4o-mini"
    query_decomposition_description = "Analyzes research queries and generates optimized, non-overlapping sub-queries for vector database retrieval."

    vectorstore_retrieval_prompt = read_markdown_file(
        "../prompts/vectorstore_retrieval_prompt.md"
    )
    vectorstore_retrieval_model = "gpt-4o-mini"
    vectorstore_retrieval_description = "Executes batch retrieval of academic context from vector database and preserves citations and metadata for structured result aggregation."

    retrieval_orchestrator_prompt = read_markdown_file(
        "../prompts/retrieval_orchestrator_prompt.md"
    )

    model = init_chat_model(model="gpt-4o-mini")

    agent = create_agent(
        model=model,
        system_prompt=retrieval_orchestrator_prompt,
        middleware=[
            SubAgentMiddleware(
                default_model="gpt-4o",
                default_tools=[],
                subagents=[
                    {
                        "name": "query_decomposition_subagent",
                        "description": query_decomposition_description,
                        "system_prompt": query_decomposition_prompt,
                        "model": query_decomposition_model,
                    },
                    {
                        "name": "vectorstore_retrieval_subagent",
                        "description": vectorstore_retrieval_description,
                        "system_prompt": vectorstore_retrieval_prompt,
                        "tools": [retrieve_from_vectorstore],
                        "model": vectorstore_retrieval_model,
                    },
                ],
            ),
        ],
        response_format=AggregatedContextList,
        context_schema=Context,
    )
    return agent
