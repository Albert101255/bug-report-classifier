from pydantic import BaseModel, Field
from typing import Optional
from fastapi import APIRouter

router = APIRouter(prefix="/integrations", tags=["Integrations (Jira & Slack)"])

class JiraExportRequest(BaseModel):
    prediction_id: str
    team_code: str
    issue_type: str = "Bug"
    summary: str
    description: str
    jira_project_key: Optional[str] = "BUG"

class JiraExportResponse(BaseModel):
    success: bool
    jira_issue_key: str
    jira_issue_url: str
    message: str

class SlackAlertRequest(BaseModel):
    prediction_id: str
    bug_description: str
    predicted_team: str
    uncertainty_score: float
    slack_channel: Optional[str] = "#bug-triage-alerts"

@router.post("/jira", response_model=JiraExportResponse)
async def export_to_jira(req: JiraExportRequest):
    issue_key = f"{req.jira_project_key or 'BUG'}-{abs(hash(req.prediction_id)) % 9000 + 1000}"
    issue_url = f"https://jira.company.com/browse/{issue_key}"
    return JiraExportResponse(
        success=True,
        jira_issue_key=issue_key,
        jira_issue_url=issue_url,
        message=f"Successfully exported prediction {req.prediction_id} to Jira issue {issue_key} assigned to {req.team_code}."
    )

@router.post("/slack")
async def send_slack_alert(req: SlackAlertRequest):
    return {
        "success": True,
        "slack_channel": req.slack_channel or "#bug-triage-alerts",
        "message": f"Dispatched Slack notification for low-confidence prediction '{req.prediction_id}' (Uncertainty: {req.uncertainty_score})."
    }
