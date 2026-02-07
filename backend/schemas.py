from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


# -- Requests ----------------------------------------------------------------

class MessageRequest(BaseModel):
    message: str


# -- Responses ---------------------------------------------------------------

class RequirementsOut(BaseModel):
    budget_min: float | None = None
    budget_max: float | None = None
    budget_currency: str | None = None
    delivery_deadline: str | None = None
    category: str | None = None
    country: str | None = None
    city: str | None = None
    event_type: str | None = None
    event_name: str | None = None
    people_count: int | None = None
    reason: str | None = None
    preferences: list[str] = []
    must_haves: list[str] = []
    nice_to_haves: list[str] = []
    is_complete: bool = False


class MessageResponse(BaseModel):
    session_id: str
    reply: str
    requirements: RequirementsOut
    status: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    status: str
    requirements: RequirementsOut | None
    messages: list[MessageOut]
    created_at: datetime
