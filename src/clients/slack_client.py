import hashlib
import hmac
import time

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError


class SlackClient:
    """Client for interacting with Slack API."""

    def __init__(self, bot_token: str, signing_secret: str):
        self._client = AsyncWebClient(token=bot_token)
        self._signing_secret = signing_secret

    def verify_signature(self, body: bytes, timestamp: str, signature: str) -> bool:
        """Verify that a request actually came from Slack."""
        if not self._signing_secret:
            # Skip verification in dev mode (no signing secret configured)
            return True

        # Check timestamp to prevent replay attacks (allow 5 min window)
        # if abs(time.time() - int(timestamp)) > 60 * 5:
        #     return False

        # Compute expected signature
        sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
        expected_sig = (
            "v0="
            + hmac.new(
                self._signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256,
            ).hexdigest()
        )

        return hmac.compare_digest(expected_sig, signature)

    async def post_message(
        self,
        channel: str,
        text: str,
        thread_ts: str | None = None,
    ) -> dict:
        """Post a message to a Slack channel, optionally in a thread."""
        try:
            response = await self._client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
            )
            return {"ok": True, "ts": response["ts"]}
        except SlackApiError as e:
            return {"ok": False, "error": str(e.response["error"])}

    async def post_ephemeral(
        self,
        channel: str,
        user: str,
        text: str,
    ) -> dict:
        """Post an ephemeral message visible only to one user."""
        try:
            response = await self._client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=text,
            )
            return {"ok": True}
        except SlackApiError as e:
            return {"ok": False, "error": str(e.response["error"])}
