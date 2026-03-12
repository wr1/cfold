"""Pydantic model for Codebase."""

from typing import List
from pydantic import BaseModel, field_validator

from .instruction import instruction
from .file_entry import file_entry


class codebase(BaseModel):
    """Represents the entire folded codebase."""

    instructions: List[instruction] = []
    files: List[file_entry] = []

    @field_validator("instructions", mode="before")
    @classmethod
    def convert_to_list(cls, v):
        """Convert dict to list of Instruction objects if needed."""
        if isinstance(v, dict):
            return [instruction(**item) for item in v]
        return v
