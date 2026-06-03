# pr_bot/main.py
import os
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, Depends
from github import Github
from anthropic import Anthropic
from pydantic import BaseModel
import json

app = FastAPI(title="PR Review Bot")

# Configuration
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# Initialize clients
github_client = Github(GITHUB_TOKEN)
claude_client = Anthropic(api_key=ANTHROPIC_API_KEY)


class PRReviewRequest(BaseModel):
    """Request payload from GitHub webhook."""
    action: str
    pull_request: dict
    repository: dict


async def verify_webhook_signature(request: Request, payload: bytes):
    """Verify that the webhook request came from GitHub."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    expected = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected}", signature):
        raise HTTPException(status_code=400, detail="Invalid signature")


@app.post("/webhook/github")
async def handle_github_webhook(request: Request):
    """Handle incoming GitHub webhook events."""
    payload = await request.body()
    await verify_webhook_signature(request, payload)

    event = request.headers.get("X-GitHub-Event")
    if event != "pull_request":
        return {"status": "ignored", "event": event}

    data = json.loads(payload)

    # Only review opened and synchronized PRs
    if data["action"] not in ["opened", "synchronize"]:
        return {"status": "ignored", "action": data["action"]}

    # Extract PR details
    repo_name = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]
    pr_title = data["pull_request"]["title"]
    pr_body = data["pull_request"]["body"] or ""

    # Get the diff
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    diff = pr.get_files()

    # Format diff for Claude
    diff_text = ""
    for file in diff:
        diff_text += f"\n--- {file.filename} ---\n"
        if file.patch:
            diff_text += file.patch + "\n"

    # Review with Claude
    review_result = await review_with_claude(
        pr_title=pr_title,
        pr_body=pr_body,
        diff=diff_text,
        repo_name=repo_name,
    )

    # Post review comments
    await post_review_comments(
        repo=repo,
        pr_number=pr_number,
        review=review_result,
    )

    return {"status": "reviewed", "pr_number": pr_number}


async def review_with_claude(
    pr_title: str,
    pr_body: str,
    diff: str,
    repo_name: str,
) -> dict:
    """Send the PR diff to Claude for review."""

    system_prompt = """You are an expert code reviewer. Review the following pull request.

For each issue, provide:
1. File and line number (if applicable)
2. Severity: critical, major, minor, suggestion
3. Category: bug, security, performance, style, architecture, testing
4. Description of the issue
5. Suggestion for fixing it

Also provide:
- Overall summary of the PR
- Positive feedback on what's done well
- Whether the PR should be approved

Be constructive and specific. Focus on issues that matter."""

    user_prompt = f"""Repository: {repo_name}
PR Title: {pr_title}
PR Description: {pr_body}

Diff:
{diff}

Review this pull request and provide structured feedback as JSON."""

    response = claude_client.messages.create(
        model="claude-opus-4-8-20260415",
        max_tokens=4000,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return json.loads(response.content[0].text)


async def post_review_comments(
    repo,
    pr_number: int,
    review: dict,
):
    """Post review comments to the PR."""
    pr = repo.get_pull(pr_number)

    # Create review body
    review_body = f"## AI Code Review Summary\n\n{review['summary']}\n\n"

    if review.get("positive_feedback"):
        review_body += "### ✅ What's Good\n"
        for feedback in review["positive_feedback"]:
            review_body += f"- {feedback}\n"
        review_body += "\n"

    if review.get("issues"):
        review_body += "### Issues Found\n\n"
        for issue in review["issues"]:
            emoji = {
                "critical": "🔴",
                "major": "🟡",
                "minor": "🟢",
                "suggestion": "💡",
            }.get(issue["severity"], "⚪")

            review_body += f"{emoji} **{issue['severity'].upper()}** - {issue['category']}\n"
            review_body += f"**File:** {issue['file']}:{issue['line']}\n"
            review_body += f"**Issue:** {issue['description']}\n"
            review_body += f"**Suggestion:** {issue['suggestion']}\n\n"

    if review.get("should_approve"):
        review_body += "\n### ✅ Recommendation: Approve"
    else:
        review_body += "\n### ❌ Recommendation: Request Changes"

    # Post as a PR review comment
    pr.create_review(
        body=review_body,
        event="COMMENT",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
