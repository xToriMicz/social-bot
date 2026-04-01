"""YouTube engagement — login check, scroll feed, like, comment.

Uses UIAutomator2 via Device facade. All interactions include
human-like delays and jitter from core.utils + core.device.
"""

import logging
from random import choice, uniform

from core.device import Device
from core.session import SessionState
from core.storage import Storage
from core.utils import random_sleep, chance
from platforms.youtube import selectors as sel

logger = logging.getLogger("social-bot.youtube")


class YouTubeBot:
    """YouTube automation via Android app (UIAutomator2)."""

    def __init__(self, device: Device, config: dict):
        self.device = device
        self.config = config.get("platforms", {}).get("youtube", {})
        self.like_pct = self.config.get("like_percentage", 70)
        self.comment_pct = self.config.get("comment_percentage", 10)
        self.subscribe_pct = self.config.get("subscribe_percentage", 5)
        self.scroll_count = self.config.get("scroll_count", 15)
        self.watch_min = self.config.get("watch_min_seconds", 10)
        self.watch_max = self.config.get("watch_max_seconds", 45)

    def open_app(self):
        """Launch YouTube app and dismiss startup dialogs."""
        logger.info("Opening YouTube app")
        self.device.app_start(sel.PACKAGE)
        random_sleep(4.0, 7.0)
        self._dismiss_popups()

    def _dismiss_popups(self):
        """Auto-dismiss common YouTube popups (permissions, updates, etc.)."""
        popup_selectors = [
            sel.POPUP_ALLOW,
            sel.POPUP_AGREE,
            sel.POPUP_NOT_NOW,
            sel.POPUP_NO_THANKS,
            sel.POPUP_SKIP,
            sel.POPUP_GOT_IT,
            sel.POPUP_OK,
        ]
        for _ in range(7):
            dismissed = False
            for popup in popup_selectors:
                btn = self.device.find(**popup)
                if btn.exists(timeout=1):
                    self.device.click_element(btn)
                    random_sleep(1.0, 2.5)
                    dismissed = True
                    break
            if not dismissed:
                break

    def is_logged_in(self) -> bool:
        """Check if YouTube is logged in (account avatar or channel visible)."""
        if self.device.exists(**sel.ACCOUNT_BUTTON):
            return True
        if self.device.exists(**sel.ACCOUNT_AVATAR):
            return True
        # If sign-in button visible, not logged in
        if self.device.exists(**sel.SIGN_IN_BUTTON):
            return False
        # Check if feed is showing (may still be logged out but feed works)
        return self.device.exists(**sel.FEED_RESULTS)

    def login(self, email: str, password: str) -> bool:
        """Login to YouTube via Google account.

        Note: YouTube login goes through Google account sign-in flow.
        Due to Google's security measures, automated login may trigger
        CAPTCHA or 2FA. Manual login on first run is recommended.
        """
        logger.info(f"Attempting login as {email}")

        if self.is_logged_in():
            logger.info("Already logged in")
            return True

        # Tap sign in button
        sign_in = self.device.find(**sel.SIGN_IN_BUTTON)
        if sign_in.exists(timeout=5):
            self.device.click_element(sign_in)
            random_sleep(3.0, 5.0)

        # Google sign-in flow — type email
        email_input = self.device.find(resourceId="identifierId")
        if not email_input.exists(timeout=5):
            email_input = self.device.find(className="android.widget.EditText")
            if not email_input.exists(timeout=5):
                logger.warning("Email input not found — manual login may be required")
                return False

        self.device.type_text(email, email_input)
        random_sleep(0.5, 1.0)

        # Click Next
        next_btn = self.device.find(textContains="Next")
        if next_btn.exists(timeout=3):
            self.device.click_element(next_btn)
            random_sleep(3.0, 5.0)

        # Type password
        pwd_input = self.device.find(className="android.widget.EditText")
        if pwd_input.exists(timeout=5):
            self.device.type_text(password, pwd_input)
            random_sleep(0.5, 1.0)

            next_btn = self.device.find(textContains="Next")
            if next_btn.exists(timeout=3):
                self.device.click_element(next_btn)
                random_sleep(5.0, 10.0)

        # Dismiss any post-login dialogs
        self._dismiss_popups()
        random_sleep(3.0, 5.0)

        success = self.is_logged_in()
        if success:
            logger.info("Login successful")
        else:
            logger.warning("Login may have failed — check for CAPTCHA/2FA")
        return success

    def _go_home(self):
        """Navigate to Home feed."""
        home_btn = self.device.find(**sel.NAV_HOME)
        if home_btn.exists(timeout=3):
            self.device.click_element(home_btn)
            random_sleep(1.5, 3.0)

    def _watch_video(self):
        """Watch current video for a random duration (human-like)."""
        watch_time = uniform(self.watch_min, self.watch_max)
        logger.debug(f"Watching video for {watch_time:.1f}s")
        random_sleep(watch_time, watch_time + 2.0, modulable=False)

    def _tap_video(self) -> bool:
        """Tap on a video from the feed to open it."""
        # Find video title or thumbnail in feed
        title = self.device.find(**sel.VIDEO_TITLE)
        if title.exists(timeout=3):
            self.device.click_element(title)
            random_sleep(3.0, 5.0)
            return True
        thumbnail = self.device.find(**sel.VIDEO_THUMBNAIL)
        if thumbnail.exists(timeout=3):
            self.device.click_element(thumbnail)
            random_sleep(3.0, 5.0)
            return True
        return False

    def _try_like(self, session: SessionState) -> bool:
        """Like the current video."""
        like_btn = self.device.find(**sel.LIKE_BUTTON)
        if not like_btn.exists(timeout=3):
            like_btn = self.device.find(**sel.LIKE_BUTTON_ALT)
            if not like_btn.exists(timeout=2):
                return False

        # Check if already liked (description might say "unlike" or show filled state)
        desc = like_btn.info.get("contentDescription", "")
        if "unlike" in desc.lower() or "liked" in desc.lower():
            return False

        self.device.click_element(like_btn)
        random_sleep(0.5, 1.5)
        session.add_like()
        logger.info("Liked video")
        return True

    def _try_comment(self, session: SessionState, comment_text: str) -> bool:
        """Open comments section, type and post a comment."""
        # Scroll down to find comment section button
        self.device.swipe_up(speed="slow")
        random_sleep(1.0, 2.0)

        comment_btn = self.device.find(**sel.COMMENT_BUTTON)
        if not comment_btn.exists(timeout=3):
            return False

        # Open comments
        self.device.click_element(comment_btn)
        random_sleep(2.0, 4.0)

        # Find comment input
        comment_input = self.device.find(**sel.COMMENT_INPUT)
        if not comment_input.exists(timeout=3):
            comment_input = self.device.find(**sel.COMMENT_INPUT_ALT)
            if not comment_input.exists(timeout=3):
                self.device.press_back()
                return False

        # Tap input to focus
        self.device.click_element(comment_input)
        random_sleep(1.0, 2.0)

        # Type comment
        self.device.type_text(comment_text)
        random_sleep(0.5, 1.5)

        # Send comment
        send_btn = self.device.find(**sel.COMMENT_SEND_BUTTON)
        if not send_btn.exists(timeout=3):
            send_btn = self.device.find(**sel.COMMENT_SEND_ALT)
            if not send_btn.exists(timeout=3):
                self.device.press_back()
                self.device.press_back()
                return False

        self.device.click_element(send_btn)
        random_sleep(2.0, 3.0)
        session.add_comment()
        logger.info(f"Commented: {comment_text[:30]}...")

        # Close comments
        self.device.press_back()
        random_sleep(1.0, 2.0)
        return True

    def _try_subscribe(self, session: SessionState) -> bool:
        """Subscribe to the channel of current video."""
        sub_btn = self.device.find(**sel.SUBSCRIBE_BUTTON)
        if not sub_btn.exists(timeout=3):
            return False

        # Check if already subscribed
        if self.device.exists(**sel.SUBSCRIBED_INDICATOR):
            return False

        self.device.click_element(sub_btn)
        random_sleep(0.5, 1.5)
        session.add_follow()
        logger.info("Subscribed to channel")
        return True

    def scroll_feed(self, session: SessionState, storage: Storage):
        """Scroll Home feed, open and engage with videos."""
        logger.info(f"Starting YouTube feed — {self.scroll_count} videos planned")
        self._go_home()

        comments = storage.load_comments()

        for i in range(self.scroll_count):
            if session.any_limit_reached:
                logger.info(f"Session limit reached at video {i}")
                break

            # Tap a video from the feed
            if not self._tap_video():
                # Scroll feed to find more videos
                self.device.swipe_up()
                random_sleep(1.0, 2.0)
                if not self._tap_video():
                    logger.debug("No video found, scrolling more")
                    self.device.swipe_up()
                    random_sleep(1.0, 2.0)
                    continue

            # Watch the video
            self._watch_video()

            # Like
            if chance(self.like_pct) and not session.likes_limit_reached:
                self._try_like(session)

            # Comment
            if chance(self.comment_pct) and not session.comments_limit_reached:
                if comments:
                    self._try_comment(session, choice(comments))

            # Subscribe
            if chance(self.subscribe_pct) and not session.follows_limit_reached:
                self._try_subscribe(session)

            # Go back to feed
            self.device.press_back()
            random_sleep(1.5, 3.0)
            session.add_scroll()

            # Scroll feed to next videos
            self.device.swipe_up()
            random_sleep(0.5, 1.5)

        logger.info(
            f"Feed done — {session.total_scrolls} videos, "
            f"{session.total_likes} likes, {session.total_comments} comments, "
            f"{session.total_follows} subscriptions"
        )

    def run(self, session: SessionState, storage: Storage, credentials: dict) -> bool:
        """Full YouTube engagement session."""
        session.platform = "youtube"

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
