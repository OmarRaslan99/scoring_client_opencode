from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when a required runtime configuration value is missing."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_environment() -> None:
    load_dotenv(project_root() / ".env", override=False)


def require_env(name: str) -> str:
    load_environment()
    value = os.getenv(name, "").strip()
    if not value or value.startswith("replace_with_"):
        raise ConfigError(f"Variable d'environnement manquante ou invalide: {name}")
    return value


def clean_text(value: str | None, max_chars: int | None = None) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if max_chars is not None and len(text) > max_chars:
        return text[: max_chars - 3].rstrip() + "..."
    return text