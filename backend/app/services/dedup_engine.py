import logging
import re
from typing import Any

from app.models import Issue
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z0-9_]{3,}\b", text.lower())
    # Include 2-grams for phrase overlap
    tokens = set(words)
    if len(words) > 1:
        for i in range(len(words) - 1):
            tokens.add(f"{words[i]}_{words[i + 1]}")
    return tokens


def _jaccard_similarity(s1: set[str], s2: set[str]) -> float:
    if not s1 or not s2:
        return 0.0
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return float(intersection) / float(union) if union > 0 else 0.0


async def find_duplicates(
    description: str,
    subject: str = "",
    organization_id: str | None = None,
    project_id: str | None = None,
    db: AsyncSession | None = None,
    limit: int = 3,
    threshold: float = 0.22,
) -> list[dict[str, Any]]:
    if not db:
        return []

    input_text = f"{subject} {description}".strip()
    input_tokens = _tokenize(input_text)
    if not input_tokens:
        return []

    try:
        query = select(Issue).order_by(Issue.created_at.desc()).limit(100)
        if organization_id:
            query = query.filter(Issue.organization_id == organization_id)
        if project_id:
            query = query.filter(Issue.project_id == project_id)

        res = await db.execute(query)
        candidates = res.scalars().all()

        scored: list[dict[str, Any]] = []
        for issue in candidates:
            candidate_text = f"{issue.title} {issue.description}".strip()
            candidate_tokens = _tokenize(candidate_text)
            sim = _jaccard_similarity(input_tokens, candidate_tokens)
            if sim >= threshold:
                shared = input_tokens.intersection(candidate_tokens)
                top_shared = [t for t in shared if "_" not in t][:4]
                explanation = (
                    f"Matches terms: {', '.join(top_shared)}"
                    if top_shared
                    else "High structural and vocabulary similarity"
                )
                scored.append(
                    {
                        "issue_id": issue.id,
                        "issue_key": issue.issue_key,
                        "title": issue.title,
                        "status": issue.status,
                        "similarity_score": round(sim, 3),
                        "explanation": explanation,
                    }
                )

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:limit]

    except Exception:
        logger.exception("Error executing duplicate detection")
        return []
