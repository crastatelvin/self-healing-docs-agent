from langgraph.graph import StateGraph, END
from .nodes import AgentState, analyzer_node, retriever_node, detector_node, patcher_node

def create_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("detector", detector_node)
    workflow.add_node("patcher", patcher_node)

    # Set entry point
    workflow.set_entry_point("analyzer")

    # Add edges
    workflow.add_edge("analyzer", "retriever")
    workflow.add_edge("retriever", "detector")
    workflow.add_edge("detector", "patcher")
    workflow.add_edge("patcher", END)

    return workflow.compile()

# For local testing
if __name__ == "__main__":
    graph = create_graph()
    initial_state = {
        "file_path": "test.py",
        "changed_code": "def add(a, b, c): return a + b + c",
        "old_code": "def add(a, b): return a + b",
        "status": "starting"
    }
    # This will fail without an API key
    # result = graph.invoke(initial_state)
    # print(result)
