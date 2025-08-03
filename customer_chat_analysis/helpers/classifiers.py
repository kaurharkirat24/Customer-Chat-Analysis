import re

def classify_message(msg):
    # Add more categories/rules as needed
    msg_lower = msg.lower()
    if re.search(r'\b(complain|not working|issue|error|problem|failed|refund|crash|trouble|wrong|broken)\b', msg_lower):
        return 'complaint'
    if "?" in msg:
        # Simple way to catch functional or general queries
        return 'query'
    if re.search(r"\bthank(s| you)\b|\bappreciate\b", msg_lower):
        return 'feedback'
    if re.search(r"\bhi\b|\bhello\b|\bgood (morning|afternoon|evening|day)\b", msg_lower):
        return 'greeting'
    if re.search(r"\bfeature request\b|\bsuggest\b", msg_lower):
        return 'feature request'
    if re.search(r"\bbug\b|report", msg_lower):
        return "bug report"
    return 'other'
