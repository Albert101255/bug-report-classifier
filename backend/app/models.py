import uuid
from datetime import UTC, datetime
from typing import Any

from app.database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), default="DEVELOPER"
    )  # ORG_ADMIN, PROJECT_MANAGER, TEAM_LEAD, DEVELOPER, QA_REPORTER, VIEWER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    memberships: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="user", cascade="all, delete-orphan"
    )
    reported_issues: Mapped[list["Issue"]] = relationship(
        "Issue", foreign_keys="Issue.reporter_id", back_populates="reporter"
    )
    assigned_issues: Mapped[list["Issue"]] = relationship(
        "Issue", foreign_keys="Issue.assignee_id", back_populates="assignee"
    )


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="organization", cascade="all, delete-orphan"
    )
    teams: Mapped[list["Team"]] = relationship(
        "Team", back_populates="organization", cascade="all, delete-orphan"
    )
    issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="organization", cascade="all, delete-orphan"
    )


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="DEVELOPER")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="members"
    )
    user: Mapped["User"] = relationship("User", back_populates="memberships")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "TRIAGE"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="projects"
    )
    issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="project", cascade="all, delete-orphan"
    )


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "BL-101"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Core Engineering")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="teams"
    )
    members: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    issues: Mapped[list["Issue"]] = relationship(
        "Issue", foreign_keys="Issue.team_id", back_populates="team"
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="MEMBER")  # LEAD, MEMBER
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User")


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issue_key: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    steps_to_reproduce: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    environment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    build_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    browser_os: Mapped[str | None] = mapped_column(String(100), nullable=True)
    technical_logs: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(30), default="NEW", index=True
    )  # NEW, TRIAGE, IN_PROGRESS, FIXED, VERIFICATION, CLOSED, REOPENED
    severity: Mapped[str] = mapped_column(
        String(30), default="P2 - Major", index=True
    )  # P0 - Blocker, P1 - Critical, P2 - Major, P3 - Minor, P4 - Trivial
    priority: Mapped[str] = mapped_column(
        String(30), default="MEDIUM", index=True
    )  # URGENT, HIGH, MEDIUM, LOW

    reporter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    assignee_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    team_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("teams.id"), nullable=True
    )
    recommended_team_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("teams.id"), nullable=True
    )
    triage_status: Mapped[str] = mapped_column(
        String(30), default="PENDING"
    )  # PENDING, APPROVED, OVERRIDDEN, MANUAL

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="issues"
    )
    project: Mapped["Project"] = relationship("Project", back_populates="issues")
    reporter: Mapped["User"] = relationship(
        "User", foreign_keys=[reporter_id], back_populates="reported_issues"
    )
    assignee: Mapped["User | None"] = relationship(
        "User", foreign_keys=[assignee_id], back_populates="assigned_issues"
    )
    team: Mapped["Team | None"] = relationship(
        "Team", foreign_keys=[team_id], back_populates="issues"
    )
    recommended_team: Mapped["Team | None"] = relationship(
        "Team", foreign_keys=[recommended_team_id]
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction", back_populates="issue", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="issue", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent", back_populates="issue", cascade="all, delete-orphan"
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issue_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("issues.id", ondelete="CASCADE"), nullable=True
    )
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bug_description: Mapped[str] = mapped_column(Text, nullable=False)
    predicted_team: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    uncertainty_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # HIGH / MEDIUM / LOW
    status: Mapped[str] = mapped_column(
        String(30), default="auto_assigned"
    )  # auto_assigned / needs_review / human_corrected
    top_alternatives: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    top_keywords: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="tfidf-logreg-v1")
    engine: Mapped[str] = mapped_column(String(50), default="tfidf-logreg")
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), index=True
    )

    issue: Mapped["Issue | None"] = relationship("Issue", back_populates="predictions")
    feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="prediction", cascade="all, delete-orphan"
    )


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    prediction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False
    )
    issue_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("issues.id", ondelete="SET NULL"), nullable=True
    )
    original_team: Mapped[str] = mapped_column(String(100), nullable=False)
    corrected_team: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    is_retrained: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    prediction: Mapped["Prediction"] = relationship(
        "Prediction", back_populates="feedbacks"
    )
    reviewer: Mapped["User"] = relationship("User")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    issue_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    issue: Mapped["Issue"] = relationship("Issue", back_populates="comments")
    author: Mapped["User"] = relationship("User")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issue_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("issues.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ISSUE_CREATED, STATUS_CHANGED, ASSIGNEE_CHANGED, TEAM_ROUTED, TRIAGE_OVERRIDDEN, etc.
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    details: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), index=True
    )

    issue: Mapped["Issue | None"] = relationship("Issue", back_populates="audit_events")
    actor: Mapped["User | None"] = relationship("User")


class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # github, jira, slack
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    repo_or_project: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
