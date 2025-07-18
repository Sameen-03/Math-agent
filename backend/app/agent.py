import os
from dotenv import load_dotenv
from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tavily import TavilyClient
from qdrant_client import QdrantClient

from langgraph.graph import StateGraph, END
from .schemas import AgentState

# Load environment variables
load_dotenv()

# --- LLM and Tool Initialization ---
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=os.getenv("GOOGLE_API_KEY"))
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --- Vector Store Connection (File-Based) ---
qdrant_client = QdrantClient(path="./qdrant_db")

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="math_problems",
    embedding=embeddings,
)
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={'score_threshold': 0.7}
)


# --- Prompt Templates ---
solution_prompt = PromptTemplate.from_template(
    """You are a math professor. Your goal is to provide a clear, step-by-step solution to the user's question.
    Use the following context to help you answer. If the context is empty or irrelevant, rely on your own knowledge.

    IMPORTANT: Your final answer must be in plain text only. Do not use any markdown formatting like asterisks for bolding or hashes for headers.

    Context:
    {context}

    Question:
    {question}

    Provide a detailed, step-by-step solution as plain text:
    """
)

# --- Agent Nodes ---
def retrieve_from_kb(state: AgentState):
    """Retrieves relevant documents from the knowledge base."""
    print("-> Retrieving from Knowledge Base...")
    question = state.original_question
    docs = retriever.get_relevant_documents(question)

    if docs:
        print("--> Found document objects in KB.")
        context = "\n\n".join([doc.page_content for doc in docs])
        if context.strip():
            print("--> Context is valid, using Knowledge Base.")
            return {"context": context, "source": "Knowledge Base"}

    print("--> No relevant text found in KB documents.")
    return {"context": "", "source": "N/A"}


def web_search(state: AgentState):
    """Performs a web search using Tavily."""
    print("-> Performing Web Search...")
    question = state.original_question
    try:
        response = tavily.search(query=question, search_depth="basic")
        context = "\n\n".join([res["content"] for res in response["results"]])
        return {"context": context, "source": "Web Search"}
    except Exception as e:
        return {"error": f"Web search failed: {str(e)}", "context": ""}

def generate_solution(state: AgentState):
    """Generates a solution based on the retrieved context."""
    print("-> Generating Solution...")
    chain = solution_prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "context": state.context,
        "question": state.original_question
    })
    return {"answer": answer}

# --- Conditional Logic ---
def decide_route(state: AgentState) -> Literal["web_search", "generate_solution"]:
    """Decides whether to perform a web search or generate a solution."""
    print("-> Deciding route...")
    if state.context:
        print("--> Route: Context found, generating solution.")
        return "generate_solution"
    else:
        print("--> Route: No context, performing web search.")
        return "web_search"

# --- Define the Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("retrieve_from_kb", retrieve_from_kb)
workflow.add_node("web_search", web_search)
workflow.add_node("generate_solution", generate_solution)
workflow.set_entry_point("retrieve_from_kb")
workflow.add_conditional_edges(
    "retrieve_from_kb",
    decide_route,
    {
        "web_search": "web_search",
        "generate_solution": "generate_solution",
    },
)
workflow.add_edge("web_search", "generate_solution")
workflow.add_edge("generate_solution", END)
math_agent = workflow.compile()