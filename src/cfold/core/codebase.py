"""Pydantic model for Codebase."""

from typing import List
from pydantic import BaseModel, field_validator

from .instruction import Instruction
from .file_entry import FileEntry


class Codebase(BaseModel):
    instructions: List[Instruction] = []
    files: List[FileEntry] = []

    @field_validator("instructions", mode="before")
    @classmethod
    def convert_to_list(cls, v):
        if isinstance(v, dict):
            return [Instruction(**item) for item in v]
        return v
