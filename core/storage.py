"""Persistent storage — JSON-based session and interaction history."""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("social-bot")

ACCOUNTS_DIR = "accounts"


class Storage:
    """Per-account persistent storage."""

    def __init__(self, username: str, platform: str):
        self.username = username
        self.platform = platform
        self.account_dir = Path(ACCOUNTS_DIR) / username / platform
        self.account_dir.mkdir(parents=True, exist_ok=True)

        self._sessions_path = self.account_dir / "sessions.json"
        self._interacted_path = self.account_dir / "interacted.json"

        self.interacted = self._load_json(self._interacted_path, {})

    def _load_json(self, path: Path, default):
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Corrupt JSON: {path}, resetting")
        return default

    def _save_json(self, path: Path, data):
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(path)  # atomic write

    def save_session(self, session_dict: dict):
        """Append session to sessions.json."""
        sessions = self._load_json(self._sessions_path, [])
        sessions.append(session_dict)
        self._save_json(self._sessions_path, sessions)
        logger.info(f"Session saved: {session_dict.get('id', '?')[:8]}")

    def add_interaction(self, user_id: str, action: str):
        """Record interaction with a user."""
        if user_id not in self.interacted:
            self.interacted[user_id] = {}
        self.interacted[user_id]["last_interaction"] = datetime.now().isoformat()
        self.interacted[user_id][f"last_{action}"] = datetime.now().isoformat()
        count_key = f"total_{action}s"
        self.interacted[user_id][count_key] = self.interacted[user_id].get(count_key, 0) + 1
        self._save_json(self._interacted_path, self.interacted)

    def can_interact(self, user_id: str, cooldown_hours: int = 24) -> bool:
        """Check if enough time passed since last interaction."""
        user = self.interacted.get(user_id)
        if not user:
            return True
        last = user.get("last_interaction")
        if not last:
            return True
        last_dt = datetime.fromisoformat(last)
        hours_passed = (datetime.now() - last_dt).total_seconds() / 3600
        return hours_passed >= cooldown_hours

    def load_comments(self) -> list[str]:
        """Load comment templates from comments.txt."""
        comments_file = self.account_dir / "comments.txt"
        if comments_file.exists():
            lines = comments_file.read_text().strip().splitlines()
            return [l.strip() for l in lines if l.strip()]
        return []
