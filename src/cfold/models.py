"""Pydantic models for cfold data structures."""

from typing import List, Optional
from pydantic import BaseModel, field_validator


class Instruction(BaseModel):
    type: str  # 'system', 'user', or 'assistant'
    content: str
    name: Optional[str] = None


class FileEntry(BaseModel):
    path: str
    content: str


class Codebase(BaseModel):
    instructions: List[Instruction] = []
    files: List[FileEntry] = []

    @field_validator("instructions", mode="before")
    def convert_to_list(cls, v):
        if isinstance(v, dict):
            return [Instruction(**item) for item in v]
        return v



