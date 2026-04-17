"""Pydantic model for FileEntry."""

from typing import Optional

from pydantic import BaseModel, model_validator


class file_entry(BaseModel):
    """Represents a file entry in the folded codebase."""

    path: str
    content: Optional[str] = None
    delete: bool = False

    @model_validator(mode="after")
    def check_content(self):
        """Ensure content is provided unless deleting."""
        if not self.delete and self.content is None:
            raise ValueError("Content must be provided if not deleting")
        return self
