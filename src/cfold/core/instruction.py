"""Pydantic model for Instruction."""

from typing import Optional
from pydantic import BaseModel


class Instruction(BaseModel):
    type: str  # 'system', 'user', or 'assistant'
    content: str
    name: Optional[str] = None
    synopsis: Optional[str] = None
