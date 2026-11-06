"""Pydantic models shared across Handshake."""

from __future__ import annotations

import time
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["founder", "investor", "engineer", "operator"]
Stage = Literal["opening", "exploring", "negotiating", "verdict"]
Decision = Literal["pending", "approved", "declined"]


class Profile(BaseModel):
    id: str
    display_name: str
    role: Role
    headline: str
    public_bio: str
    looking_for: str
    # Roles this person wants to meet. Empty means "every allowed role".
    seeking: list[Role] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    location: str = ""
    stage: str | None = None
    public_terms: dict[str, str] = Field(default_factory=dict)
    private_limits: list[str] = Field(default_factory=list)
    secret_terms: list[str] = Field(default_factory=list)  # exact strings for the leak check
    hub_username: str | None = None
    hub_evidence: list[str] = Field(default_factory=list)
    is_demo: bool = False

    def public_view(self) -> dict:
        """What other agents (and the judge) are allowed to read."""
        return self.model_dump(exclude={"private_limits", "secret_terms", "is_demo", "seeking"})


class AgentTurn(BaseModel):
    speaker_id: str
    message: str
    private_thought: str = ""
    stage: Stage = "exploring"
    wants_to_end: bool = False
    leak_check_passed: bool = True
    leak_caught: bool = False  # the first draft leaked and was rewritten


class DealMemo(BaseModel):
    verdict: Literal["worth_meeting", "maybe_later", "not_fit"]
    score: int = Field(ge=0, le=100)
    reasons: list[str]
    agreed: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    meeting_questions: list[str] = Field(default_factory=list)
    intro_message: str = ""


class Negotiation(BaseModel):
    id: str
    profile_a_id: str
    profile_b_id: str
    turns: list[AgentTurn] = Field(default_factory=list)
    memo: DealMemo | None = None
    memo_ar: DealMemo | None = None  # Arabic translation, made on first request
    status: Literal["running", "complete", "failed"] = "running"
    language: str = "en"  # en or fusha (Modern Standard Arabic)
    decision_a: Decision = "pending"
    decision_b: Decision = "pending"
    created_at: float = Field(default_factory=time.time)
    decided_at: dict[str, float] = Field(default_factory=dict)   # profile id -> when they approved or passed
    notes: dict[str, str] = Field(default_factory=dict)          # profile id -> optional note to the other person
    snoozed: list[str] = Field(default_factory=list)             # profile ids who chose "Not now"


class Match(BaseModel):
    profile: Profile
    score: int  # 0-100 for display
    reason: str
    fit: Literal["strong", "possible"] = "strong"
