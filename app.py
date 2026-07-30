import time
from fastapi import FastAPI

START_TIME = time.time()

app = FastAPI(
    title="Vera Merchant AI Assistant",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Vera Merchant AI Assistant",
        "message": "Vera API is running",
        "health": "/v1/healthz",
        "metadata": "/v1/metadata",
        "docs": "/docs"
    }


@app.get("/v1/healthz")
async def healthz():
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - START_TIME)
    }


@app.get("/v1/metadata")
async def metadata():
    return {
        "team_name": "Vera AI",
        "team_members": ["Mehak"],
        "model": "deterministic-rule-based",
        "approach": "Deterministic context-aware merchant assistant",
        "contact_email": "mehak.917542@gmail.com",
        "version": "1.0.0",
        "submitted_at": "2026-07-29T18:30:00Z"
    }

# ============================================================
# CONTEXT
# ============================================================

class ContextBody(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str | None = None


@app.post("/v1/context")
async def push_context(body: ContextBody):
    context_store = get_store_for_scope(body.scope)

    # Reject unknown scopes
    if context_store is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported scope: {body.scope}"
        )

    existing = context_store.get(body.context_id)

    # Reject an older version
    if existing and body.version < existing["version"]:
        return {
            "accepted": False,
            "reason": "stale_version",
            "context_id": body.context_id,
            "version": body.version
        }

    # Same version is idempotent
    if existing and body.version == existing["version"]:
        return {
            "accepted": True,
            "reason": "already_exists",
            "context_id": body.context_id,
            "version": body.version
        }

    # Store new/latest context
    context_store[body.context_id] = {
        "version": body.version,
        "payload": body.payload
    }

    return {
        "accepted": True,
        "reason": "stored",
        "context_id": body.context_id,
        "version": body.version
    }


# ============================================================
# TICK
# ============================================================

class TickBody(BaseModel):
    now: str
    available_triggers: list[str]


@app.post("/v1/tick")
async def tick(body: TickBody):
    actions = []

    for trigger_id in body.available_triggers:

        # ----------------------------------------------------
        # 1. Resolve trigger
        # ----------------------------------------------------

        trigger = get_trigger(trigger_id)

        if not trigger:
            continue

        # ----------------------------------------------------
        # 2. Check suppression
        # ----------------------------------------------------

        suppression_key = trigger.get(
            "suppression_key",
            ""
        )

        # Do not send the same suppressed trigger twice
        if (
            suppression_key
            and suppression_key in sent_suppression_keys
        ):
            continue

        # ----------------------------------------------------
        # 3. Resolve merchant ID
        # ----------------------------------------------------

        # Real judge trigger format:
        # merchant_id is at the top level.
        merchant_id = trigger.get("merchant_id")

        # Backward compatibility with local test triggers:
        # merchant_id may be inside payload.
        if not merchant_id:
            merchant_id = trigger.get(
                "payload",
                {}
            ).get("merchant_id")

        if not merchant_id:
            continue

        # ----------------------------------------------------
        # 4. Resolve merchant
        # ----------------------------------------------------

        merchant = get_merchant(merchant_id)

        if not merchant:
            continue

        # ----------------------------------------------------
        # 5. Resolve merchant category
        # ----------------------------------------------------

        category_slug = merchant.get("category_slug")

        if not category_slug:
            continue

        # ----------------------------------------------------
        # 6. Resolve category context
        # ----------------------------------------------------

        category = get_category(category_slug)

        if not category:
            continue

        # ----------------------------------------------------
        # 7. Compose merchant-facing message
        # ----------------------------------------------------

        message = compose_message(
            category,
            merchant,
            trigger
        )

        # ----------------------------------------------------
        # 8. Create action
        # ----------------------------------------------------

        actions.append({
            "conversation_id": (
                f"conv_{merchant_id}_{trigger_id}"
            ),
            "merchant_id": merchant_id,
            "customer_id": trigger.get("customer_id"),
            "send_as": "vera",
            "trigger_id": trigger_id,
            "body": message["body"],
            "cta": message["cta"],
            "suppression_key": suppression_key,
            "rationale": (
                "Resolved trigger, merchant and category context."
            )
        })

        # ----------------------------------------------------
        # 9. Remember suppression key
        # ----------------------------------------------------

        if suppression_key:
            sent_suppression_keys.add(
                suppression_key
            )

    return {
        "actions": actions
    }


# ============================================================
# REPLY
# ============================================================

class ReplyBody(BaseModel):
    conversation_id: str
    merchant_id: str | None = None
    customer_id: str | None = None
    from_role: str
    message: str
    received_at: str
    turn_number: int


@app.post("/v1/reply")
async def reply(body: ReplyBody):
    result = handle_reply(body.message)

    response = {
        "action": result["action"],
        "rationale": result["rationale"]
    }

    # Send actions require a non-empty body
    if result["action"] == "send":
        response["body"] = result["body"]
        response["cta"] = "open_ended"

    # Wait actions include a wait duration
    elif result["action"] == "wait":
        response["wait_seconds"] = 14400

    return response
