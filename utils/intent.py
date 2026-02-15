def detect_intent(query):
    q = query.lower()

    if any(word in q for word in ["next", "future", "predict"]):
        return "prediction"

    if any(word in q for word in ["top", "best", "highest"]):
        return "analysis"

    if any(word in q for word in ["risk", "down", "loss"]):
        return "risk"

    return "general"
