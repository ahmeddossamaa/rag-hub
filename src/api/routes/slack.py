from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/events")
async def slack_events(request: Request):
    """Handle Slack Events API webhooks."""
    body = await request.json()

    # Handle URL verification challenge
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    # TODO: Implement actual event handling
    # For now, just acknowledge receipt
    return {"ok": True}
