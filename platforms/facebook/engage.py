"""Facebook engagement — login, scroll feed, like, comment."""

import logging
from random import choice

from core.device import Device
from core.session import SessionState
from core.storage import Storage
from core.utils import random_sleep, chance
from platforms.facebook import selectors as sel

logger = logging.getLogger("social-bot.facebook")


class FacebookBot:
    """Facebook automation via Android app (UIAutomator2)."""

    def __init__(self, device: Device, config: dict):
        self.device = device
        self.config = config.get("platforms", {}).get("facebook", {})
        self.like_pct = self.config.get("like_percentage", 70)
        self.comment_pct = self.config.get("comment_percentage", 20)
        self.share_pct = self.config.get("share_percentage", 5)
        self.scroll_count = self.config.get("scroll_count", 15)

    def open_app(self):
        """Launch Facebook app."""
        logger.info("Opening Facebook app")
        self.device.app_start(sel.PACKAGE)
        random_sleep(3.0, 5.0)

    def is_logged_in(self) -> bool:
        """Check if already logged in (feed visible)."""
        return self.device.exists(**sel.FEED_LIST) or self.device.exists(description="News Feed")

    def login(self, email: str, password: str) -> bool:
        """Login to Facebook. Returns True if successful."""
        logger.info(f"Logging in as {email}")

        if self.is_logged_in():
            logger.info("Already logged in")
            return True

        email_field = self.device.find(**sel.LOGIN_EMAIL)
        if not email_field.exists(timeout=5):
            logger.error("Login screen not found")
            return False

        # Type email
        self.device.type_text(email, email_field)
        random_sleep(0.5, 1.0)

        # Type password
        pwd_field = self.device.find(**sel.LOGIN_PASSWORD)
        self.device.type_text(password, pwd_field)
        random_sleep(0.5, 1.0)

        # Click login
        login_btn = self.device.find(**sel.LOGIN_BUTTON)
        self.device.click_element(login_btn)
        random_sleep(5.0, 8.0)

        success = self.is_logged_in()
        if success:
            logger.info("Login successful")
        else:
            logger.error("Login failed")
        return success

    def scroll_feed(self, session: SessionState, storage: Storage):
        """Scroll feed, like and comment on posts."""
        logger.info(f"Starting feed scroll — {self.scroll_count} scrolls planned")

        for i in range(self.scroll_count):
            if session.any_limit_reached:
                logger.info(f"Session limit reached at scroll {i}")
                break

            # Scroll down
            self.device.swipe_up()
            session.add_scroll()
            random_sleep(2.0, 4.0)  # "read" the post

            # Like
            if chance(self.like_pct) and not session.likes_limit_reached:
                self._try_like(session)

            # Comment
            if chance(self.comment_pct) and not session.comments_limit_reached:
                comments = storage.load_comments()
                if comments:
                    self._try_comment(session, choice(comments))

            # Pause between posts (human-like reading time)
            random_sleep(1.0, 3.0)

        logger.info(f"Feed scroll done — {session.total_scrolls} scrolls, {session.total_likes} likes, {session.total_comments} comments")

    def _try_like(self, session: SessionState):
        """Try to like the current post."""
        like_btn = self.device.find(**sel.LIKE_BUTTON)
        if not like_btn.exists(timeout=2):
            return

        # Check if already liked
        if self.device.exists(**sel.LIKED_BUTTON):
            return

        self.device.click_element(like_btn)
        session.add_like()
        random_sleep(0.5, 1.5)

    def _try_comment(self, session: SessionState, comment_text: str):
        """Try to comment on the current post."""
        comment_btn = self.device.find(**sel.COMMENT_BUTTON)
        if not comment_btn.exists(timeout=2):
            return

        # Open comment section
        self.device.click_element(comment_btn)
        random_sleep(1.5, 3.0)

        # Find input and type
        comment_input = self.device.find(**sel.COMMENT_INPUT)
        if not comment_input.exists(timeout=3):
            self.device.press_back()
            return

        self.device.type_text(comment_text, comment_input)
        random_sleep(0.5, 1.5)

        # Post comment
        post_btn = self.device.find(**sel.COMMENT_POST_BUTTON)
        if post_btn.exists(timeout=2):
            self.device.click_element(post_btn)
            random_sleep(2.0, 4.0)

            # Verify comment posted
            session.add_comment()
            logger.info(f"Commented: {comment_text[:30]}...")
        else:
            logger.warning("Post button not found")

        self.device.press_back()
        random_sleep(1.0, 2.0)

    def run(self, session: SessionState, storage: Storage, credentials: dict) -> bool:
        """Full Facebook engagement session."""
        session.platform = "facebook"

        self.open_app()

        if not self.is_logged_in():
            email = credentials.get("email", "")
            password = credentials.get("password", "")
            if not email or not password:
                logger.error("No credentials provided")
                return False
            if not self.login(email, password):
                return False

        self.scroll_feed(session, storage)

        session.finish()
        storage.save_session(session.to_dict())
        logger.info(session.summary())
        return True
