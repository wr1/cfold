"""Pydantic models for cfold data structures."""

from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator


class Instruction(BaseModel):
    type: str  # 'system', 'user', or 'assistant'
    content: str
    name: Optional[str] = None
    synopsis: Optional[str] = None


class FileEntry(BaseModel):
    path: str
    content: Optional[str] = None
    delete: bool = False

    @model_validator(mode='after')
    def check_content(self):
        if not self.delete and self.content is None:
            raise ValueError("Content must be provided if not deleting")
        return self


class Codebase(BaseModel):
    instructions: List[Instruction] = []
    files: List[FileEntry] = []

    @field_validator("instructions", mode="before")
    @classmethod
    def convert_to_list(cls, v):
        if isinstance(v, dict):
            return [Instruction(**item) for item in v]
        return v







