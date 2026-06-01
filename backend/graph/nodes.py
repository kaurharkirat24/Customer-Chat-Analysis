from .state import GraphState
from services.llm_factory import get_llm
from services.gmail_service import send_email

def llm_extraction_node(state: GraphState):
    llm = get_llm()
    result = llm.extract_intent_and_sentiment(state["text"])
    return {
        "intent": result.get("intent", "General Support"),
        "sentiment": result.get("sentiment", "Neutral")
    }

def rescue_agent_node(state: GraphState):
    reply = "We are incredibly sorry for the frustration. A senior team member has been notified and will reach out to you personally to resolve this immediately."
    
    if state.get("customer_email") and "@" in state["customer_email"]:
        try:
            send_email(state["customer_email"], "Apology from CX Flow", reply)
        except Exception as e:
            print(f"Failed to send email: {e}")

    return {
        "action_type": "Rescue_Apology",
        "outgoing_message": reply,
        "status": "Action_Taken"
    }

def escalation_agent_node(state: GraphState):
    reply = "Your issue has been escalated to our VIP support queue. You will receive a response within 1 hour."
    
    if state.get("customer_email") and "@" in state["customer_email"]:
        try:
            send_email(state["customer_email"], "Support Escalation Notice", reply)
        except Exception as e:
            print(f"Failed to send email: {e}")

    return {
        "action_type": "VIP_Escalation",
        "outgoing_message": reply,
        "status": "Escalated"
    }

def feedback_agent_node(state: GraphState):
    reply = "Thank you for your feedback! We have logged this directly with our product engineering team."
    return {
        "action_type": "Product_Feedback_Logged",
        "outgoing_message": reply,
        "status": "Logged"
    }

def default_agent_node(state: GraphState):
    reply = "Thank you for reaching out. We have received your message and will get back to you shortly."
    return {
        "action_type": "Standard_AutoReply",
        "outgoing_message": reply,
        "status": "Action_Taken"
    }
