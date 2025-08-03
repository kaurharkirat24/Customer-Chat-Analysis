import re

def analyze_tone(msg):
    msg_lower = msg.lower()
    # Extend with more sophisticated models if required
    if re.search(r"\bfrustrat(ed|ing)\b|\bannoy(ing|ed)\b|\bupset\b|\bangry\b|\bwtf\b", msg_lower):
        return "frustrated"
    if re.search(r"\bplease\b|\bthank you\b|\bappreciate\b|\bcould you\b", msg_lower):
        return "polite"
    if re.search(r"\bsorry\b|\bapolog(y|ize)\b", msg_lower):
        return "apologetic"
    # Use sentiment + lack of markers for neutrality
    if re.search(r"^ok\b|^okay\b|^noted\b|^sure\b", msg_lower):
        return "neutral"
    return "neutral"
