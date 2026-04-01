"""Session state — tracks counters, limits, and timing per session."""

import uuid
import logging
from datetime import datetime

logger = logging.getLogger("social-bot")


class SessionState:
    """Track one bot session's progress and limits."""

    def __init__(self, config: dict):
        self.id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.finish_time = None
        self.platform = None

        # Limits from config
        session_cfg = config.get("session", {})
        self.max_likes = session_cfg.get("max_likes", 50)
        self.max_comments = session_cfg.get("max_comments", 10)
        self.max_follows = session_cfg.get("max_follows", 20)
        self.max_duration_minutes = session_cfg.get("max_duration_minutes", 60)

        # Counters
        self.total_likes = 0
        self.total_comments = 0
        self.total_follows = 0
        self.total_scrolls = 0
        self.total_shares = 0
        self.total_watches = 0
        self.errors = 0

    @property
    def likes_limit_reached(self) -> bool:
        return self.total_likes >= self.max_likes

    @property
    def comments_limit_reached(self) -> bool:
        return self.total_comments >= self.max_comments

    @property
    def follows_limit_reached(self) -> bool:
        return self.total_follows >= self.max_follows

    @property
    def time_limit_reached(self) -> bool:
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        return elapsed >= self.max_duration_minutes

    @property
    def any_limit_reached(self) -> bool:
        return (
            self.likes_limit_reached
            or self.comments_limit_reached
            or self.time_limit_reached
        )

    def add_like(self):
        self.total_likes += 1
        logger.info(f"Like #{self.total_likes}/{self.max_likes}")

    def add_comment(self):
        self.total_comments += 1
        logger.info(f"Comment #{self.total_comments}/{self.max_comments}")

    def add_follow(self):
        self.total_follows += 1
        logger.info(f"Follow #{self.total_follows}/{self.max_follows}")

    def add_scroll(self):
        self.total_scrolls += 1

    def add_error(self):
        self.errors += 1

    def finish(self):
        self.finish_time = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform,
            "start_time": str(self.start_time),
            "finish_time": str(self.finish_time) if self.finish_time else None,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "total_follows": self.total_follows,
            "total_scrolls": self.total_scrolls,
            "total_shares": self.total_shares,
            "total_watches": self.total_watches,
            "errors": self.errors,
        }

    def summary(self) -> str:
        elapsed = (
            (self.finish_time or datetime.now()) - self.start_time
        ).total_seconds()
        return (
            f"Session {self.id[:8]} ({self.platform}) — "
            f"{int(elapsed)}s, "
            f"likes={self.total_likes}, comments={self.total_comments}, "
            f"follows={self.total_follows}, scrolls={self.total_scrolls}, "
            f"errors={self.errors}"
        )
