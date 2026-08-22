"""Shared Pydantic response schemas.

Schemas are the API's contract. Keeping them separate from SQLAlchemy models
means we decide deliberately what leaves the server — a habit that stops
`password_hash` from ever being serialised into a JSON response by accident.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    app: str
    environment: str


class DatabaseHealthResponse(BaseModel):
    status: str = Field(examples=["ok", "error"])
    database: str = Field(description="Reachability of the MySQL server")
    detail: str | None = None
