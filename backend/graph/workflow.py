from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import (
    llm_extraction_node, 
    retention_agent_node,
    frustration_agent_node,
    escalation_agent_node, 
    feedback_agent_node,
    security_agent_node,
    billing_agent_node,
    compliance_agent_node,
    human_review_node,
    default_agent_node
)

def route_intent(state: GraphState):
    confidence = state.get("confidence_score", 1.0)
    intent = state.get("intent", "").lower()
    sentiment = state.get("sentiment", "").lower()
    
    # 1. Human-in-the-Loop Gateway
    if confidence < 0.75:
        return "human_review"
    if "refund" in intent or "legal" in intent or "compliance" in intent:
        return "human_review" # High risk items require review

    # 2. Strict Intent Routing
    if "security" in intent:
        return "security"
    elif "compliance" in intent:
        return "compliance"
    elif "billing" in intent:
        return "billing"
    elif "cancel" in intent or "downgrade" in intent:
        return "retention"
    elif "escalation" in intent or "vip" in intent:
        return "escalation"
    elif "negative" in sentiment or "frustrated" in sentiment:
        return "frustration"
    elif "feedback" in intent or "bug" in intent:
        return "feedback"
    
    return "default"

workflow = StateGraph(GraphState)

workflow.add_node("llm_extractor", llm_extraction_node)
workflow.add_node("retention", retention_agent_node)
workflow.add_node("frustration", frustration_agent_node)
workflow.add_node("escalation", escalation_agent_node)
workflow.add_node("feedback", feedback_agent_node)
workflow.add_node("security", security_agent_node)
workflow.add_node("billing", billing_agent_node)
workflow.add_node("compliance", compliance_agent_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("default", default_agent_node)

workflow.set_entry_point("llm_extractor")

workflow.add_conditional_edges(
    "llm_extractor",
    route_intent,
    {
        "retention": "retention",
        "frustration": "frustration",
        "escalation": "escalation",
        "feedback": "feedback",
        "security": "security",
        "billing": "billing",
        "compliance": "compliance",
        "human_review": "human_review",
        "default": "default"
    }
)

workflow.add_edge("retention", END)
workflow.add_edge("frustration", END)
workflow.add_edge("escalation", END)
workflow.add_edge("feedback", END)
workflow.add_edge("security", END)
workflow.add_edge("billing", END)
workflow.add_edge("compliance", END)
workflow.add_edge("human_review", END)
workflow.add_edge("default", END)

app_graph = workflow.compile()
