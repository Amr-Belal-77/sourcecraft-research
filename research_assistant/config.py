"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings kept outside graph state."""

    api_key: str | None = None
    model: str = "gemini-3.1-flash-lite"
    temperature: float = 0.2

    @classmethod
    def from_env(cls, api_key: str | None = None) -> Settings:
        return cls(
            api_key=api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        )

    def require_api_key(self) -> str:
        if not self.api_key:
            raise ValueError(
                "A Gemini API key is required. Set GOOGLE_API_KEY or enter it in the app."
            )
        return self.api_key
