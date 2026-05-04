import os
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from utils.rag import RAGManager

load_dotenv()

# Initialize RAG
rag_manager = RAGManager()

class AgentState(TypedDict):
    file_path: str
    changed_code: str
    old_code: str
    code_intent: str
    retrieved_docs: List[dict] # List of {"content": "...", "source": "..."}
    contradictions: str
    generated_patch: str
    status: str

# Initialize the LLM (Local llama.cpp server)
# Ensure llama.cpp server is running on port 8080
llm = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed", # Local server usually doesn't require a key
    model="qwen"
)

def analyzer_node(state: AgentState):
    print("---ANALYZING CODE---")
    code = state["changed_code"]
    prompt = f"""You are a senior code analyzer.
Analyze the logical intent of the following code snippet. 
Respond with ONLY one sentence describing what this code does.

CODE TO ANALYZE:
---
{code}
---
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"code_intent": response.content, "status": "analyzed"}

def retriever_node(state: AgentState):
    print("---RETRIEVING DOCS---")
    intent = state["code_intent"]
    # Query actual docs from ChromaDB
    docs = rag_manager.query_docs(intent, n_results=1)
    if not docs:
        docs = [{"content": f"No documentation found for: {intent}", "source": "unknown"}]
    return {"retrieved_docs": docs, "status": "retrieved"}

def detector_node(state: AgentState):
    print("---DETECTING CONTRADICTIONS---")
    code = state["changed_code"]
    docs = "\n".join([d["content"] for d in state["retrieved_docs"]])
    prompt = f"""Compare the NEW CODE below with the EXISTING DOCUMENTATION.
Identify any contradictions or missing information.

NEW CODE:
---
{code}
---

EXISTING DOCUMENTATION:
---
{docs}
---

List the contradictions clearly:"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"contradictions": response.content, "status": "detected"}

def patcher_node(state: AgentState):
    print("---GENERATING PATCH---")
    contradictions = state["contradictions"]
    docs = "\n".join([d["content"] for d in state["retrieved_docs"]])
    prompt = f"""Based on the following contradictions, update the documentation to perfectly match the new code logic.
DO NOT include any conversational text like "Certainly" or "Here is the patch". 
ONLY output the updated markdown documentation.

CONTRADICTIONS FOUND:
{contradictions}

CURRENT DOCUMENTATION:
{docs}

NEW DOCUMENTATION:
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"generated_patch": response.content, "status": "patched"}
