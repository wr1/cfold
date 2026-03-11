"""Pydantic model for FileEntry."""

from typing import Optional
from pydantic import BaseModel, model_validator


class FileEntry(BaseModel):
    path: str
    content: Optional[str] = None
    delete: bool = False

    @model_validator(mode="after")
    def check_content(self):
        if not self.delete and self.content is None:
            raise ValueError("Content must be provided if not deleting")
        return self
