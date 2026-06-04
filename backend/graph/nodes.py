from .state import GraphState
from services.llm_factory import get_llm
from services.gmail_service import send_email

def llm_extraction_node(state: GraphState):
    llm = get_llm()
    result = llm.extract_intent_and_sentiment(state["text"], state.get("attachments", []))
    return {
        "intent": result.get("intent", "General Support"),
        "sentiment": result.get("sentiment", "Neutral"),
        "confidence_score": result.get("confidence", 1.0),
        "priority": result.get("priority", "P3"),
        "feature_tag": result.get("feature", None),
        "is_spam": result.get("is_spam", False)
    }

def retention_agent_node(state: GraphState):
    reply = "We noticed you requested to cancel or downgrade. We hate to see you go! A specialized retention specialist will reach out shortly with options that might better suit your needs."
    
    if state.get("customer_email") and "@" in state["customer_email"]:
        try:
            send_email(state["customer_email"], "Important: Your Account Request", reply)
        except Exception as e:
            print(f"Failed to send email: {e}")

    return {
        "action_type": "Retention_Offer_Sent",
        "outgoing_message": reply,
        "status": "Action_Taken"
    }

def frustration_agent_node(state: GraphState):
    reply = "We are incredibly sorry for the frustration. A senior team member has been notified and will reach out to you personally to resolve this immediately."
    
    if state.get("customer_email") and "@" in state["customer_email"]:
        try:
            send_email(state["customer_email"], "Apology from CX Flow", reply)
        except Exception as e:
            print(f"Failed to send email: {e}")

    return {
        "action_type": "Frustration_Apology_Sent",
        "outgoing_message": reply,
        "status": "Escalated"
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

def security_agent_node(state: GraphState):
    return {
        "action_type": "Security_Incident_Flagged",
        "outgoing_message": "Internal Action: Passed to security team.",
        "status": "Escalated"
    }

def billing_agent_node(state: GraphState):
    return {
        "action_type": "Billing_Review_Requested",
        "outgoing_message": "Internal Action: Passed to finance team.",
        "status": "Pending"
    }

def compliance_agent_node(state: GraphState):
    return {
        "action_type": "Legal_Compliance_Review",
        "outgoing_message": "Internal Action: Passed to legal team.",
        "status": "Escalated"
    }

def human_review_node(state: GraphState):
    # Generate an actual draft response for the human reviewer to approve/edit
    draft_message = None
    try:
        llm = get_llm()
        prompt = f"""You are a professional customer service agent. Draft a short, empathetic email reply 
to the following customer message. Be helpful, concise and professional. Do NOT include subject line or greetings like "Dear Customer". 
Just write the body of the response.

Customer message:
{state.get("text", "")}

Detected intent: {state.get("intent", "Unknown")}
Detected sentiment: {state.get("sentiment", "Unknown")}
"""
        response = llm.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        draft_message = response.text.strip()
    except Exception as e:
        print(f"Failed to generate draft for human review: {e}")

    if not draft_message:
        # Fallback if LLM call fails
        draft_message = "Thank you for reaching out. We have received your message and a team member will review and respond shortly."

    return {
        "action_type": "Human_Review_Required",
        "outgoing_message": draft_message,
        "status": "Draft_Pending_Approval"
    }

def default_agent_node(state: GraphState):
    reply = "Thank you for reaching out. We have received your message and will get back to you shortly."
    return {
        "action_type": "Standard_AutoReply",
        "outgoing_message": reply,
        "status": "Action_Taken"
    }
