"""Pydantic models for cfold data structures."""

from typing import List
from pydantic import BaseModel


class FileEntry(BaseModel):
    path: str
    content: str


class Codebase(BaseModel):
    system: str = ""
    user: str = ""
    assistant: str = ""
    files: List[FileEntry] = []

