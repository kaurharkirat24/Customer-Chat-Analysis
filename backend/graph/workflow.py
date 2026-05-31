from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import (
    llm_extraction_node, 
    rescue_agent_node, 
    escalation_agent_node, 
    feedback_agent_node, 
    default_agent_node
)

def route_intent(state: GraphState):
    intent = state.get("intent", "").lower()
    sentiment = state.get("sentiment", "").lower()
    
    if "cancel" in intent or ("negative" in sentiment or "frustrated" in sentiment):
        if "cancel" in intent:
            return "rescue"
        else:
            return "escalation"
    elif "escalation" in intent or "vip" in intent:
        return "escalation"
    elif "feedback" in intent or "bug" in intent:
        return "feedback"
    return "default"

workflow = StateGraph(GraphState)

workflow.add_node("llm_extractor", llm_extraction_node)
workflow.add_node("rescue", rescue_agent_node)
workflow.add_node("escalation", escalation_agent_node)
workflow.add_node("feedback", feedback_agent_node)
workflow.add_node("default", default_agent_node)

workflow.set_entry_point("llm_extractor")

workflow.add_conditional_edges(
    "llm_extractor",
    route_intent,
    {
        "rescue": "rescue",
        "escalation": "escalation",
        "feedback": "feedback",
        "default": "default"
    }
)

workflow.add_edge("rescue", END)
workflow.add_edge("escalation", END)
workflow.add_edge("feedback", END)
workflow.add_edge("default", END)

app_graph = workflow.compile()
