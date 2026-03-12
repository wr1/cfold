"""Pydantic model for Instruction."""

from typing import Optional
from pydantic import BaseModel


class Instruction(BaseModel):
    """Represents a single instruction in the folded codebase."""
    type: str
    content: str
    name: Optional[str] = None
    synopsis: Optional[str] = None
