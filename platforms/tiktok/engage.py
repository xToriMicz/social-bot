"""TikTok engagement — login, scroll feed, like, comment, follow.

Uses UIAutomator2 via Device facade. All interactions include
human-like delays and jitter from core.utils + core.device.

Selectors are content-desc based (resource IDs are obfuscated).
Tested on emulator-5556 with TikTok latest (API 34).
"""

import logging
import os
import subprocess
from datetime import datetime
from random import choice, shuffle, uniform

from core.device import Device
from core.session import SessionState
from core.storage import Storage
from core.utils import random_sleep, chance
from platforms.tiktok import selectors as sel

logger = logging.getLogger("social-bot.tiktok")

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "screenshots")


def _reconnect_device(serial: str) -> Device:
    """Reconnect uiautomator2 — TikTok can cause disconnects."""
    try:
        d = Device(serial)
        d.d.info  # test connection
        return d
    except Exception:
        logger.debug("Reconnecting uiautomator2...")
        import uiautomator2 as u2
        d_raw = u2.connect(serial)
        dev = Device.__new__(Device)
        dev.d = d_raw
        dev.d.implicitly_wait(10)
        return dev


class TikTokBot:
    """TikTok automation via Android app (UIAutomator2)."""

    def __init__(self, device: Device, config: dict, serial: str = "emulator-5556"):
        self.device = device
        self.serial = serial
        self.config = config.get("platforms", {}).get("tiktok", {})
        self.like_pct = self.config.get("like_percentage", 80)
        self.comment_pct = self.config.get("comment_percentage", 10)
        self.follow_pct = self.config.get("follow_percentage", 15)
        self.share_pct = self.config.get("share_percentage", 5)
        self.scroll_count = self.config.get("scroll_count", 20)
        self.watch_min = self.config.get("watch_min_seconds", 3)
        self.watch_max = self.config.get("watch_max_seconds", 15)

    def _checkpoint(self, action: str, detail: str = ""):
        """Screenshot checkpoint — save after every action for debugging."""
        try:
            self._reconnect()
            ts = datetime.now().strftime("%H%M%S")
            label = f"tt_{ts}_{action}"
            if detail:
                label += f"_{detail[:40]}"
            label = label.replace(" ", "_").replace("/", "_").replace(":", "_")
            path = os.path.join(SCREENSHOT_DIR, f"{label}.png")
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            self.device.d.screenshot(path)
            logger.debug(f"Checkpoint: {label}")
        except Exception as e:
            logger.debug(f"Checkpoint failed: {e}")

    def _reconnect(self):
        """Reconnect after u2 disconnect."""
        try:
            self.device.d.info
        except Exception:
            logger.info("u2 disconnected — reconnecting")
            self.device = _reconnect_device(self.serial)

    def _detect_stage(self) -> str:
        """Detect current TikTok stage by checking visible elements."""
        self._reconnect()
        # Video feed — like button visible on right side
        if self.device.d(descriptionContains="Like video").exists(timeout=1):
            return "feed_player"
        # Following tab active
        if self.device.d(text="Following", selected=True).exists(timeout=1):
            return "following"
        # For You tab active
        if self.device.d(text="For You", selected=True).exists(timeout=1):
            return "for_you"
        # Home nav visible
        if self.device.d(description="Home").exists(timeout=1):
            return "home"
        # Login/onboarding
        if self.device.d(textContains="Log in").exists(timeout=1):
            return "login"
        return "unknown"

    def open_app(self):
        """Launch TikTok app and handle onboarding/popups."""
        logger.info("Opening TikTok app")
        self.device.d.app_stop(sel.PACKAGE)
        random_sleep(1.0, 2.0)
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "am", "start",
             "-n", f"{sel.PACKAGE}/com.ss.android.ugc.aweme.splash.SplashActivity"],
            capture_output=True,
        )
        random_sleep(5.0, 8.0)
        self._handle_onboarding()
        self._dismiss_popups()
        self._checkpoint("open_app")

    def _handle_onboarding(self):
        """Handle first-launch onboarding (age, terms, etc.)."""
        # Dismiss Google credential manager
        close = self.device.find(**sel.GOOGLE_SIGNIN_CLOSE)
        if close.exists(timeout=3):
            self.device.click_element(close)
            random_sleep(1.0, 2.0)

        # Dismiss immersive mode notification
        got_it = self.device.find(**sel.ONBOARD_GOT_IT)
        if got_it.exists(timeout=2):
            self.device.click_element(got_it)
            random_sleep(0.5, 1.0)

        # Age selection
        age_btn = self.device.find(**sel.ONBOARD_AGE_18)
        if age_btn.exists(timeout=3):
            self.device.click_element(age_btn)
            logger.info("Selected age: At least 18")
            random_sleep(3.0, 5.0)

        # Terms agreement
        agree = self.device.find(**sel.ONBOARD_AGREE)
        if agree.exists(timeout=3):
            self.device.click_element(agree)
            logger.info("Agreed to terms")
            random_sleep(3.0, 5.0)

    def _dismiss_popups(self):
        """Auto-dismiss common TikTok popups (permissions, updates, etc.)."""
        popup_selectors = [
            sel.POPUP_ALLOW,
            sel.POPUP_WHILE_USING,
            sel.POPUP_GOT_IT,
            sel.POPUP_NOT_NOW,
            sel.POPUP_SKIP,
            sel.POPUP_OK,
            sel.POPUP_NOT_INTERESTED,
            sel.GOOGLE_SIGNIN_CLOSE,
        ]
        for _ in range(8):
            dismissed = False
            for popup in popup_selectors:
                btn = self.device.find(**popup)
                if btn.exists(timeout=1):
                    self.device.click_element(btn)
                    random_sleep(0.5, 1.5)
                    dismissed = True
                    break
            if not dismissed:
                break

    def is_on_feed(self) -> bool:
        """Check if we're on the feed (For You or Following)."""
        return (
            self.device.exists(**sel.NAV_HOME)
            and (self.device.exists(**sel.NAV_FOR_YOU)
                 or self.device.exists(**sel.NAV_FOLLOWING))
        )

    def is_logged_in(self) -> bool:
        """Check if TikTok is logged in."""
        if not self.is_on_feed():
            return False
        return True

    def login(self, email: str, password: str) -> bool:
        """Login to TikTok via email/password. Returns True if successful."""
        logger.info(f"Logging in as {email}")

        if self.is_on_feed():
            profile = self.device.find(**sel.NAV_PROFILE)
            if profile.exists(timeout=3):
                self.device.click_element(profile)
                random_sleep(2.0, 3.0)

        login_link = self.device.find(**sel.LOGIN_LINK)
        if login_link.exists(timeout=5):
            self.device.click_element(login_link)
            random_sleep(2.0, 4.0)

        close = self.device.find(**sel.GOOGLE_SIGNIN_CLOSE)
        if close.exists(timeout=3):
            self.device.click_element(close)
            random_sleep(1.0, 2.0)

        email_btn = self.device.find(**sel.LOGIN_USE_PHONE_EMAIL)
        if email_btn.exists(timeout=5):
            self.device.click_element(email_btn)
            random_sleep(2.0, 3.0)

        email_tab = self.device.find(**sel.LOGIN_EMAIL_TAB)
        if email_tab.exists(timeout=3):
            self.device.click_element(email_tab)
            random_sleep(1.0, 2.0)

        email_input = self.device.find(**sel.LOGIN_EMAIL_INPUT)
        if not email_input.exists(timeout=5):
            logger.error("Email input not found")
            return False

        self.device.type_text(email, email_input)
        random_sleep(0.5, 1.0)

        cont = self.device.find(**sel.LOGIN_CONTINUE)
        if cont.exists(timeout=3):
            self.device.click_element(cont)
            random_sleep(3.0, 5.0)

        pwd_input = self.device.find(**sel.LOGIN_PASSWORD_INPUT)
        if pwd_input.exists(timeout=5):
            self.device.type_text(password, pwd_input)
            random_sleep(0.5, 1.0)

            cont = self.device.find(**sel.LOGIN_CONTINUE)
            if cont.exists(timeout=3):
                self.device.click_element(cont)
                random_sleep(5.0, 10.0)

        self._dismiss_popups()
        random_sleep(3.0, 5.0)

        success = self.is_on_feed()
        if success:
            logger.info("Login successful — on feed")
        else:
            logger.warning("Login may have failed — check for CAPTCHA")
        self._checkpoint("login", "success" if success else "failed")
        return success

    def _go_following(self):
        """Navigate to Following tab — only engage with followed creators."""
        self._reconnect()
        # Tap Home first
        home = self.device.find(**sel.NAV_HOME)
        if home.exists(timeout=3):
            self.device.click_element(home)
            random_sleep(1.0, 2.0)

        # Tap Following tab
        following = self.device.find(**sel.NAV_FOLLOWING)
        if following.exists(timeout=3):
            self.device.click_element(following)
            random_sleep(2.0, 4.0)
            self._checkpoint("go_following")
            logger.info("Switched to Following tab")

    def _ensure_on_feed(self):
        """Make sure we're on the For You feed."""
        if not self.is_on_feed():
            home = self.device.find(**sel.NAV_HOME)
            if home.exists(timeout=3):
                self.device.click_element(home)
                random_sleep(1.0, 2.0)

        fy = self.device.find(**sel.NAV_FOR_YOU)
        if fy.exists(timeout=2):
            self.device.click_element(fy)
            random_sleep(0.5, 1.0)

    def _watch_video(self):
        """Watch current video for a random duration (human-like)."""
        watch_time = uniform(self.watch_min, self.watch_max)
        logger.debug(f"Watching video for {watch_time:.1f}s")
        random_sleep(watch_time, watch_time + 1.0, modulable=False)

    def _try_like(self, session: SessionState) -> bool:
        """Like current video via double-tap on screen center."""
        self._reconnect()
        # Check if already liked
        if self.device.exists(**sel.UNLIKE_BUTTON):
            return False

        # Double-tap center of screen (most natural TikTok like)
        w, h = self.device.screen_size
        cx = int(w * uniform(0.35, 0.65))
        cy = int(h * uniform(0.35, 0.55))
        self.device.d.double_click(cx, cy, duration=0.1)
        random_sleep(0.8, 1.5)

        self._checkpoint("like", "double_tap")
        session.add_like()
        return True

    def _try_like_button(self, session: SessionState) -> bool:
        """Like via the heart icon button (fallback method)."""
        self._reconnect()
        if self.device.exists(**sel.UNLIKE_BUTTON):
            return False

        like_btn = self.device.find(**sel.LIKE_BUTTON)
        if not like_btn.exists(timeout=2):
            like_btn = self.device.find(**sel.LIKE_BUTTON_ALT)
            if not like_btn.exists(timeout=2):
                return False

        self.device.click_element(like_btn)
        random_sleep(0.5, 1.2)
        self._checkpoint("like", "button")
        session.add_like()
        return True

    def _try_comment(self, session: SessionState, comment_text: str) -> bool:
        """Open comment section, type and post a comment."""
        self._reconnect()
        comment_btn = self.device.find(**sel.COMMENT_BUTTON)
        if not comment_btn.exists(timeout=2):
            comment_btn = self.device.find(**sel.COMMENT_BUTTON_ALT)
            if not comment_btn.exists(timeout=2):
                return False

        # Open comments
        self.device.click_element(comment_btn)
        random_sleep(2.0, 3.5)
        self._checkpoint("comment", "sheet_open")

        self._reconnect()

        # Find input field
        comment_input = self.device.find(**sel.COMMENT_INPUT)
        if not comment_input.exists(timeout=3):
            comment_input = self.device.find(**sel.COMMENT_INPUT_ALT)
            if not comment_input.exists(timeout=3):
                logger.warning("Comment input not found")
                self.device.press_back()
                return False

        # Tap input to activate it
        self.device.click_element(comment_input)
        random_sleep(0.5, 1.0)

        # Type comment
        self.device.type_text(comment_text)
        random_sleep(0.5, 1.5)

        # Post comment
        post_btn = self.device.find(**sel.COMMENT_SEND)
        if not post_btn.exists(timeout=2):
            post_btn = self.device.find(**sel.COMMENT_SEND_ALT)
            if not post_btn.exists(timeout=2):
                self.device.d.send_action("send")
                random_sleep(1.0, 2.0)
                session.add_comment()
                logger.info(f"Commented (keyboard send): {comment_text[:30]}...")
                self._checkpoint("comment", "after_send_keyboard")
                self.device.press_back()
                random_sleep(0.5, 1.0)
                self.device.press_back()
                return True

        self.device.click_element(post_btn)
        random_sleep(2.0, 3.0)
        session.add_comment()
        logger.info(f"Commented: {comment_text[:30]}...")
        self._checkpoint("comment", "after_send")

        # Close comment section
        self.device.press_back()
        random_sleep(0.5, 1.0)
        self.device.press_back()
        random_sleep(0.5, 1.0)
        return True

    def _try_follow(self, session: SessionState) -> bool:
        """Follow the video creator via the + button on avatar."""
        self._reconnect()
        follow_btn = self.device.find(**sel.FOLLOW_BUTTON)
        if not follow_btn.exists(timeout=2):
            return False

        self.device.click_element(follow_btn)
        random_sleep(0.5, 1.5)
        self._checkpoint("follow")
        session.add_follow()
        return True

    def scroll_feed(self, session: SessionState, storage: Storage):
        """Scroll For You feed, engaging with videos."""
        logger.info(f"Starting TikTok feed — {self.scroll_count} videos planned")

        self._ensure_on_feed()

        # Wait for content — stage detection instead of fixed wait
        for _ in range(10):
            stage = self._detect_stage()
            logger.debug(f"Stage: {stage}")
            if stage in ("feed_player", "for_you", "following"):
                break
            random_sleep(1.0, 2.0)

        # Dismiss "Swipe up for more" if visible
        swipe_hint = self.device.find(**sel.ONBOARD_SWIPE_UP)
        if swipe_hint.exists(timeout=2):
            self.device.swipe_up()
            random_sleep(1.0, 2.0)

        # Shuffle comments to avoid duplicates
        comments = storage.load_comments()
        comment_queue = list(comments) if comments else []
        shuffle(comment_queue)
        comment_idx = 0

        for i in range(self.scroll_count):
            if session.any_limit_reached:
                logger.info(f"Session limit reached at video {i}")
                break

            self._reconnect()

            # Watch the video
            self._watch_video()

            # Like (double-tap 70% / button 30%)
            if chance(self.like_pct) and not session.likes_limit_reached:
                if chance(70):
                    self._try_like(session)
                else:
                    self._try_like_button(session)

            # Comment — use queue to avoid duplicates
            if chance(self.comment_pct) and not session.comments_limit_reached:
                if comment_queue:
                    if comment_idx >= len(comment_queue):
                        shuffle(comment_queue)
                        comment_idx = 0
                    self._try_comment(session, comment_queue[comment_idx])
                    comment_idx += 1

            # Follow
            if chance(self.follow_pct) and not session.follows_limit_reached:
                self._try_follow(session)

            # Swipe to next video
            self.device.swipe_up()
            session.add_scroll()
            random_sleep(0.5, 1.5)

        self._checkpoint("feed_done")
        logger.info(
            f"Feed done — {session.total_scrolls} videos, "
            f"{session.total_likes} likes, {session.total_comments} comments, "
            f"{session.total_follows} follows"
        )

    def run(self, session: SessionState, storage: Storage, credentials: dict) -> bool:
        """Full TikTok engagement session."""
        session.platform = "tiktok"

        self.open_app()

        # Login if credentials provided
        if credentials.get("email") and credentials.get("password"):
            if not self.is_on_feed():
                self.login(credentials["email"], credentials["password"])
        else:
            logger.info("No credentials — browsing without login")

        self.scroll_feed(session, storage)

        # Close TikTok app after session
        self._reconnect()
        self.device.d.app_stop(sel.PACKAGE)
        random_sleep(1.0, 2.0)

        session.finish()
        storage.save_session(session.to_dict())
        logger.info(session.summary())
        return True
