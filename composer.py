def compose_message(category, merchant, trigger):
    """
    Compose a deterministic merchant-facing message
    using category, merchant and trigger context.
    """

    identity = merchant.get("identity", {})

    owner_name = identity.get("owner_name", "there")
    business_name = identity.get("name", "your business")
    locality = identity.get("locality", "")

    trigger_kind = trigger.get("kind", "")

    if trigger_kind == "research_digest_release":
        body = (
            f"Hi {owner_name}, I found a dentistry research update "
            f"that could be relevant for {business_name}"
        )

        if locality:
            body += f" in {locality}"

        body += (
            ". It may be useful for planning your next patient "
            "recall campaign. Want the key takeaway?"
        )

        return {
            "body": body,
            "cta": "reply_yes"
        }

    # Safe fallback
    return {
        "body": (
            f"Hi {owner_name}, I found an update that may be "
            f"relevant for {business_name}. Want the details?"
        ),
        "cta": "reply_yes"
    }