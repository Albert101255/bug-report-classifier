import logging
from typing import Any

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class GitHubService:
    @staticmethod
    async def create_github_issue(
        title: str,
        body: str,
        labels: list[str] | None = None,
        custom_token: str | None = None,
        custom_repo: str | None = None,
    ) -> dict[str, Any]:
        token = custom_token or settings.GITHUB_TOKEN
        repo = custom_repo or settings.GITHUB_DEFAULT_REPO

        if not token or not repo or "/" not in repo:
            return {
                "success": False,
                "github_issue_number": None,
                "github_issue_url": None,
                "message": "Not configured: Valid GitHub token and target repository (owner/repo) must be configured in Settings.",
            }

        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Triage-Platform-Integration/2.0",
        }
        payload = {
            "title": title,
            "body": body,
            "labels": labels or ["bug", "triage-routed"],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "github_issue_number": data.get("number"),
                        "github_issue_url": data.get("html_url"),
                        "message": f"Successfully created GitHub issue #{data.get('number')} in {repo}",
                    }
                else:
                    error_msg = f"GitHub API error ({response.status_code}): {response.text[:200]}"
                    logger.warning(error_msg)
                    return {
                        "success": False,
                        "github_issue_number": None,
                        "github_issue_url": None,
                        "message": error_msg,
                    }
        except httpx.RequestError as exc:
            error_msg = f"Network failure communicating with GitHub API: {exc}"
            logger.exception(error_msg)
            return {
                "success": False,
                "github_issue_number": None,
                "github_issue_url": None,
                "message": error_msg,
            }
