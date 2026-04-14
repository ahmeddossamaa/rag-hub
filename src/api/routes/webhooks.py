import re
from enum import Enum

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from src.api.dependencies import get_rag_engine, get_slack_client
from src.clients.slack_client import SlackClient
from src.core.rag_engine import RAGEngine

router = APIRouter()


class Channel(str, Enum):
    """Supported webhook channels."""

    slack = "slack"
    discord = "discord"  # Future
    teams = "teams"  # Future


class Bot(str, Enum):
    """Available bots."""

    hipaa = "hipaa"
    architecture = "architecture"  # Future
    onboarding = "onboarding"  # Future


def extract_question(text: str, channel: Channel) -> str:
    """Extract the question from message text, removing bot mentions."""
    if channel == Channel.slack:
        # Remove Slack user mentions like <@U123456>
        cleaned = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    elif channel == Channel.discord:
        # Remove Discord mentions like <@!123456> or <@123456>
        cleaned = re.sub(r"<@!?\d+>", "", text).strip()
    else:
        cleaned = text.strip()
    return cleaned


def format_slack_response(answer: str, sources: list) -> str:
    """Format the RAG response for Slack."""
    # Build source citations
    if sources:
        source_names = list(set(s.metadata.get("source", "") for s in sources if s.metadata.get("source")))
        if source_names:
            sources_text = "\n\n_Sources: " + ", ".join(source_names) + "_"
        else:
            sources_text = ""
    else:
        sources_text = ""

    return answer + sources_text


async def process_slack_message(
    question: str,
    channel_id: str,
    thread_ts: str,
    rag_engine: RAGEngine,
    slack_client: SlackClient,
):
    """Background task to process message and post reply."""
    result = await rag_engine.query(question)
    response_text = format_slack_response(result.answer, result.sources)

    await slack_client.post_message(
        channel=channel_id,
        text=response_text,
        thread_ts=thread_ts,
    )


@router.post("/{channel}/{bot}")
async def webhook_handler(
    channel: Channel,
    bot: Bot,
    request: Request,
    background_tasks: BackgroundTasks,
    rag_engine: RAGEngine = Depends(get_rag_engine),
    slack_client: SlackClient = Depends(get_slack_client),
):
    """
    Universal webhook handler for all channels and bots.

    Endpoints:
    - POST /api/v1/webhooks/slack/hipaa
    - POST /api/v1/webhooks/slack/architecture
    - POST /api/v1/webhooks/discord/hipaa (future)
    """
    # Get raw body for signature verification
    body_bytes = await request.body()
    body = await request.json()

    # Route to channel-specific handler
    if channel == Channel.slack:
        # Verify signature (skipped if no signing secret configured)
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")

        if not slack_client.verify_signature(body_bytes, timestamp, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Handle URL verification challenge
        if body.get("type") == "url_verification":
            return {"challenge": body.get("challenge")}

        # Handle event callbacks
        if body.get("type") == "event_callback":
            event = body.get("event", {})
            event_type = event.get("type")

            # Handle message or app_mention events
            if event_type in ("message", "app_mention"):
                # Skip bot messages to prevent loops
                if event.get("bot_id") or event.get("subtype") == "bot_message":
                    return {"ok": True}

                # Extract the question
                text = event.get("text", "")
                question = extract_question(text, Channel.slack)

                if not question:
                    return {"ok": True}

                # Get channel and thread info for reply
                channel_id = event.get("channel")
                thread_ts = event.get("ts")  # Reply in thread

                # Process in background (Slack requires response within 3 seconds)
                background_tasks.add_task(
                    process_slack_message,
                    question,
                    channel_id,
                    thread_ts,
                    rag_engine,
                    slack_client,
                )

        # Acknowledge receipt immediately
        return {"ok": True}

    elif channel == Channel.discord:
        raise HTTPException(
            status_code=501,
            detail="Discord integration not yet implemented",
        )

    elif channel == Channel.teams:
        raise HTTPException(
            status_code=501,
            detail="Teams integration not yet implemented",
        )

    raise HTTPException(status_code=400, detail=f"Unknown channel: {channel}")
