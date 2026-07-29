def handle_reply(text: str):
    """
    Deterministic merchant reply handling.

    Handles:
    1. STOP / hostile replies
    2. Automatic replies
    3. Positive commitment
    4. Normal conversation
    """

    message = text.strip().lower()

    # ========================================================
    # 1. STOP / HOSTILE
    # ========================================================

    stop_phrases = [
        "stop",
        "not interested",
        "don't message me",
        "do not message me",
        "leave me alone",
        "unsubscribe",
        "remove me",
        "spam"
    ]

    if any(phrase in message for phrase in stop_phrases):
        return {
            "action": "end",
            "body": None,
            "rationale": (
                "Merchant requested conversation termination."
            )
        }

    # ========================================================
    # 2. AUTOMATIC REPLY
    # ========================================================

    auto_reply_phrases = [
        "thank you for contacting",
        "thanks for contacting",
        "thank you for reaching",
        "thanks for reaching",
        "we will respond shortly",
        "we'll respond shortly",
        "our team will get back",
        "we will get back to you",
        "business hours",
        "currently unavailable",
        "away message"
    ]

    if any(phrase in message for phrase in auto_reply_phrases):
        return {
            "action": "wait",
            "body": None,
            "rationale": (
                "Detected an automated merchant response."
            )
        }

    # ========================================================
    # 3. POSITIVE / COMMITMENT
    # ========================================================

    positive_phrases = [
        "yes",
        "yeah",
        "sure",
        "interested",
        "go ahead",
        "proceed",
        "let's do it",
        "lets do it",
        "what's next",
        "send it"
    ]

    if any(phrase in message for phrase in positive_phrases):
        return {
            "action": "send",
            "body": (
                "Great — I'll move this forward. "
                "I'll share the key takeaway and the next practical step."
            ),
            "rationale": (
                "Merchant showed clear interest or commitment."
            )
        }

    # ========================================================
    # 4. NORMAL REPLY
    # ========================================================

    return {
        "action": "send",
        "body": (
            "Got it. I can keep this focused on what is most "
            "relevant for your business. Want me to continue?"
        ),
        "rationale": (
            "Continuing the merchant conversation."
        )
    }