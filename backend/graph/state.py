from typing import TypedDict, Optional

class GraphState(TypedDict):
    interaction_id: int
    text: str
    intent: Optional[str]
    sentiment: Optional[str]
    summary: Optional[str]
    action_type: Optional[str]
    outgoing_message: Optional[str]
    status: Optional[str]
