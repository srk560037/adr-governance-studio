import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request, Response, status

# 1. Environment and Configuration Loading
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "development_secret")

app = FastAPI(title="ADR Governance Studio API")


def load_governance_policy() -> Dict[str, Any]:
    """Helper to parse governance policy JSON safely."""
    policy_path = BASE_DIR / "governance_policy.json"
    if not policy_path.exists():
        return {"policy_version": "1.0", "rules": []}
    try:
        return json.loads(policy_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse governance policy: {str(e)}"
        )


def verify_hmac_signature(raw_body: bytes, signature_header: str) -> None:
    """Verifies incoming X-Hub-Signature-256 header against GITHUB_WEBHOOK_SECRET."""
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Webhook secret not configured on server."
        )

    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid signature header format."
        )

    expected_signature = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="HMAC signature verification failed."
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Health check endpoint enforcing governance policy file readability."""
    policy = load_governance_policy()
    return {"status": "ok", "policy_loaded": bool(policy)}


@app.post("/v1/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: str = Header(None, alias="X-GitHub-Event")
):
    """GitHub Webhook Receiver enforcing HMAC auth and evaluating ADR changes."""
    raw_body = await request.body()

    # 1. Authenticate Request Signature
    verify_hmac_signature(raw_body, x_hub_signature_256)

    # 2. Parse Raw Payload JSON
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload received."
        )

    # 3. Filter Non-Pull-Request Events
    if not x_github_event or x_github_event != "pull_request":
        return {"status": "ignored", "reason": f"Event '{x_github_event}' ignored"}

    # 4. Handle PR Actions
    action = payload.get("action")
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "reason": f"Action '{action}' not evaluated"}

    # 5. Evaluate ADR Files in Repository
    adr_dir = BASE_DIR.parent / ".adr" / "decisions"
    evaluated_files = []

    if adr_dir.exists() and adr_dir.is_dir():
        for adr_file in adr_dir.glob("*.md"):
            if adr_file.is_file():
                try:
                    content = adr_file.read_text(encoding="utf-8")
                    evaluated_files.append({"file": adr_file.name, "length": len(content)})
                except Exception as err:
                    # Ignore unreadable files gracefully during batch scans
                    pass

    return {
        "status": "processed",
        "action": action,
        "pr_number": payload.get("number"),
        "evaluated_adrs": len(evaluated_files)
    }