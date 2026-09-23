from __future__ import annotations

import os
import re
import secrets
import shlex
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Read optional .env values without overriding the process environment."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[7:].lstrip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if value.startswith(("\"", "'")):
            try:
                parts = shlex.split(value, comments=True, posix=True)
            except ValueError as exc:
                raise ValueError(f"Invalid quoted value for {key} in {path.name}") from exc
            value = " ".join(parts)
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            if value.startswith("#"):
                value = ""
        os.environ.setdefault(key, value)


_load_dotenv(BASE_DIR / ".env")


def _secret_key(var_dir: Path) -> str:
    env_value = os.getenv("SECRET_KEY", "").strip()
    if env_value:
        return env_value
    var_dir.mkdir(parents=True, exist_ok=True)
    key_file = var_dir / "secret_key"
    try:
        descriptor = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        key = key_file.read_text(encoding="utf-8").strip()
        if not key:
            raise ValueError("var/secret_key is empty; remove it to generate a new session key")
        key_file.chmod(0o600)
        return key
    key = secrets.token_urlsafe(48)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(key)
    return key


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    data_path: Path
    database_path: Path
    secret_key: str
    llm_mode: str
    openai_api_key: str
    openai_model: str
    openai_base_url: str


def get_settings() -> Settings:
    db_path = Path(os.getenv("DATABASE_PATH", "").strip() or "var/tandau.db")
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    return Settings(
        base_dir=BASE_DIR,
        data_path=BASE_DIR / "data" / "hackathon-dataset-anonymized.csv",
        database_path=db_path,
        secret_key=_secret_key(BASE_DIR / "var"),
        llm_mode=os.getenv("LLM_MODE", "off").strip().lower() or "off",
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
    )


settings = get_settings()
