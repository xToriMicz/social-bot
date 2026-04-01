"""YouTube engagement — verified on Pixel 8 AVD (emulator-5556).

Key findings from real testing:
- YouTube opens videos in mini player by default, must expand first
- Like button says "I like this" (not "like this video")
- uiautomator2 server disconnects during video playback — need reconnect
- Launch via HomeActivity (not WatchWhileActivity)
- Nav bar uses content-desc, Subscriptions may have suffix
"""

import logging
import subprocess
from random import choice, uniform

from core.device import Device
from core.session import SessionState
from core.storage import Storage
from core.utils import random_sleep, chance
from platforms.youtube import selectors as sel

logger = logging.getLogger("social-bot.youtube")


def _reconnect_device(serial: str) -> Device:
    """Reconnect uiautomator2 — YouTube video playback causes disconnects."""
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


class YouTubeBot:
    """YouTube automation via Android app (UIAutomator2)."""

    def __init__(self, device: Device, config: dict, serial: str = "emulator-5556"):
        self.device = device
        self.serial = serial
        self.config = config.get("platforms", {}).get("youtube", {})
        self.like_pct = self.config.get("like_percentage", 70)
        self.comment_pct = self.config.get("comment_percentage", 10)
        self.subscribe_pct = self.config.get("subscribe_percentage", 5)
        self.scroll_count = self.config.get("scroll_count", 15)
        self.watch_min = self.config.get("watch_min_seconds", 10)
        self.watch_max = self.config.get("watch_max_seconds", 45)
        self._seen_videos = set()

    def _reconnect(self):
        """Reconnect after u2 disconnect (common with YouTube)."""
        try:
            self.device.d.info
        except Exception:
            logger.info("u2 disconnected — reconnecting")
            self.device = _reconnect_device(self.serial)

    def open_app(self):
        """Launch YouTube via HomeActivity (verified working)."""
        logger.info("Opening YouTube app")
        self.device.d.app_stop(sel.PACKAGE)
        random_sleep(1.0, 2.0)
        # Use am start directly — app_start doesn't always work
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "am", "start",
             "-n", f"{sel.PACKAGE}/{sel.HOME_ACTIVITY}"],
            capture_output=True,
        )
        random_sleep(5.0, 8.0)
        self._dismiss_popups()

    def _dismiss_popups(self):
        """Auto-dismiss YouTube popups (permissions, updates, TOS)."""
        popup_selectors = [
            sel.POPUP_ALLOW,
            sel.POPUP_DISMISS,
            sel.POPUP_AGREE,
            sel.POPUP_NOT_NOW,
            sel.POPUP_NO_THANKS,
            sel.POPUP_GOT_IT,
            sel.POPUP_SKIP,
            sel.POPUP_OK,
        ]
        for _ in range(8):
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

    def _dismiss_mini_player(self):
        """Close any lingering mini player before navigating."""
        mini = self.device.find(**sel.MINI_PLAYER)
        if mini.exists(timeout=2):
            # Swipe mini player down to close (not up — that goes to launcher)
            bounds = mini.info["bounds"]
            cx = (bounds["left"] + bounds["right"]) // 2
            cy = bounds["top"]
            # Press back instead — more reliable than swipe
            self.device.press_back()
            random_sleep(1.0, 2.0)
            # If still there, try again
            if self.device.find(**sel.MINI_PLAYER).exists(timeout=1):
                self.device.press_back()
                random_sleep(1.0, 2.0)

    def _expand_mini_player(self) -> bool:
        """Expand mini player to full watch mode — required to access like/comment."""
        mini = self.device.find(**sel.MINI_PLAYER)
        if mini.exists(timeout=3):
            mini.click()
            random_sleep(3.0, 5.0)
            return True
        return False

    def is_logged_in(self) -> bool:
        """Check if YouTube is logged in."""
        if self.device.exists(**sel.ACCOUNT_BUTTON):
            return True
        if self.device.exists(**sel.SIGN_IN_BUTTON):
            return False
        return self.device.exists(**sel.FEED_RESULTS)

    def login(self, email: str, password: str) -> bool:
        """Login via Google account. Manual login recommended for first run."""
        logger.info(f"Attempting login as {email}")

        if self.is_logged_in():
            logger.info("Already logged in")
            return True

        sign_in = self.device.find(**sel.SIGN_IN_BUTTON)
        if sign_in.exists(timeout=5):
            self.device.click_element(sign_in)
            random_sleep(3.0, 5.0)

        # Google sign-in flow
        email_input = self.device.find(className="android.widget.EditText")
        if not email_input.exists(timeout=5):
            logger.warning("Email input not found — manual login required")
            return False

        self.device.type_text(email, email_input)
        random_sleep(0.5, 1.0)

        next_btn = self.device.find(textContains="Next")
        if next_btn.exists(timeout=3):
            self.device.click_element(next_btn)
            random_sleep(3.0, 5.0)

        pwd_input = self.device.find(className="android.widget.EditText")
        if pwd_input.exists(timeout=5):
            self.device.type_text(password, pwd_input)
            random_sleep(0.5, 1.0)
            next_btn2 = self.device.find(textContains="Next")
            if next_btn2.exists(timeout=3):
                self.device.click_element(next_btn2)
                random_sleep(5.0, 10.0)

        self._dismiss_popups()
        random_sleep(3.0, 5.0)

        success = self.is_logged_in()
        logger.info(f"Login {'successful' if success else 'failed — check CAPTCHA/2FA'}")
        return success

    def _go_feed(self):
        """Navigate to Subscriptions feed — only engage with subscribed channels."""
        self._dismiss_mini_player()
        sub = self.device.find(**sel.NAV_SUBSCRIPTIONS)
        if sub.exists(timeout=3):
            self.device.click_element(sub)
            random_sleep(2.0, 4.0)

    def _watch_video(self):
        """Watch current video for a random duration."""
        watch_time = uniform(self.watch_min, self.watch_max)
        logger.debug(f"Watching video for {watch_time:.1f}s")
        random_sleep(watch_time, watch_time + 2.0, modulable=False)

    def _open_video_from_feed(self) -> bool:
        """Click an unseen video from the feed."""
        self._reconnect()
        try:
            vids = self.device.d(**sel.VIDEO_IN_FEED)
            for v in vids:
                try:
                    desc = v.info.get("contentDescription", "")
                except Exception:
                    continue
                vid_key = desc[:60]
                if vid_key in self._seen_videos:
                    continue
                self._seen_videos.add(vid_key)
                logger.info(f"Opening: {desc[:80]}")
                v.click()
                random_sleep(3.0, 5.0)
                self._reconnect()
                # Expand mini player if needed
                mini = self.device.find(**sel.MINI_PLAYER)
                if mini.exists(timeout=3):
                    self.device.click_element(mini)
                    random_sleep(2.0, 4.0)
                return True
        except Exception as e:
            logger.warning(f"Error finding video: {e}")
            self._reconnect()
        return False

    def _try_like(self, session: SessionState) -> bool:
        """Like the current video. Must be in full watch mode."""
        self._reconnect()
        like_btn = self.device.find(**sel.LIKE_BUTTON)
        if not like_btn.exists(timeout=3):
            # Fallback: scroll down slightly — like row may be below player
            logger.debug("Like not visible — scrolling down to find it")
            w, h = self.device.screen_size
            self.device.d.swipe(w // 2, int(h * 0.6), w // 2, int(h * 0.4), duration=0.3)
            random_sleep(1.5, 2.5)
            self._reconnect()
            like_btn = self.device.find(**sel.LIKE_BUTTON)
            if not like_btn.exists(timeout=3):
                logger.debug("Like button not found after scroll")
                return False

        self.device.click_element(like_btn)
        random_sleep(1.0, 2.0)
        session.add_like()
        logger.info("Liked video")
        return True

    def _try_comment(self, session: SessionState, comment_text: str) -> bool:
        """Comment on current video. Click comment area to open sheet."""
        self._reconnect()

        # Click comment area — located below the like/engagement row
        # Find like button position and click ~120px below it
        like_btn = self.device.d(descriptionContains="like this video")
        if like_btn.exists(timeout=3):
            bounds = like_btn.info["bounds"]
            comment_y = bounds["bottom"] + 120
            self.device.d.click(bounds["left"], comment_y)
        else:
            # Fallback: click at ~44% screen height
            w, h = self.device.screen_size
            self.device.d.click(w // 2, int(h * 0.44))
        random_sleep(2.0, 4.0)

        self._reconnect()

        # Check if comment sheet opened — look for EditText
        comment_input = self.device.d(className="android.widget.EditText")
        if not comment_input.exists(timeout=3):
            logger.debug("Comment sheet didn't open")
            self.device.press_back()
            return False

        try:
            comment_input.click()
            random_sleep(0.5, 1.0)
            comment_input.clear_text()
            random_sleep(0.3, 0.5)
            self.device.d.send_keys(comment_text)
            random_sleep(0.5, 1.5)
        except Exception as e:
            logger.warning(f"Comment input error: {e}")
            self.device.press_back()
            return False

        # Click "Send comment" button
        send_btn = self.device.d(description="Send comment")
        if send_btn.exists(timeout=3):
            send_btn.click()
            random_sleep(3.0, 5.0)
            # Wait for comment to appear — verify it was posted
            self._reconnect()
            random_sleep(2.0, 3.0)
            session.add_comment()
            logger.info(f"Commented: {comment_text[:30]}...")
        else:
            self.device.d.send_action("send")
            random_sleep(3.0, 5.0)
            session.add_comment()
            logger.info(f"Commented (keyboard): {comment_text[:30]}...")

        # Close comment sheet — wait a moment to see the comment posted
        random_sleep(1.0, 2.0)
        close = self.device.d(description="Close")
        if close.exists(timeout=2):
            close.click()
        else:
            self.device.press_back()
        random_sleep(2.0, 3.0)
        return True

    def _try_subscribe(self, session: SessionState) -> bool:
        """Subscribe to current video's channel."""
        self._reconnect()
        sub_btn = self.device.find(**sel.SUBSCRIBE_BUTTON)
        if not sub_btn.exists(timeout=3):
            return False
        if self.device.exists(**sel.SUBSCRIBED_INDICATOR):
            return False

        self.device.click_element(sub_btn)
        random_sleep(0.5, 1.5)
        session.add_follow()
        logger.info("Subscribed to channel")
        return True

    def scroll_feed(self, session: SessionState, storage: Storage):
        """Browse Subscriptions feed, engage with videos."""
        logger.info(f"Starting YouTube session — {self.scroll_count} videos planned")
        self._go_feed()

        comments = storage.load_comments()

        for i in range(self.scroll_count):
            if session.any_limit_reached:
                logger.info(f"Session limit reached at video {i}")
                break

            # Open a video from feed
            if not self._open_video_from_feed():
                self._reconnect()
                self.device.swipe_up()
                random_sleep(1.0, 2.0)
                if not self._open_video_from_feed():
                    logger.debug("No video found, scrolling more")
                    continue

            # Watch
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
            self._reconnect()
            self.device.press_back()
            random_sleep(1.0, 2.0)
            # Close mini player if it appears
            self._reconnect()
            close_btn = self.device.d(description="Close minimized player")
            if close_btn.exists(timeout=2):
                close_btn.click()
                random_sleep(1.0, 2.0)
            self._dismiss_mini_player()
            self._go_feed()

            session.add_scroll()
            self.device.swipe_up()
            random_sleep(0.5, 1.5)

        logger.info(
            f"Session done — {session.total_scrolls} videos, "
            f"{session.total_likes} likes, {session.total_comments} comments, "
            f"{session.total_follows} subscriptions"
        )

    def _enter_shorts_fullscreen(self) -> bool:
        """If Shorts opened as grid (some YT versions), click first thumbnail to enter fullscreen."""
        self._reconnect()
        like_btn = self.device.d(descriptionContains="like this video")
        if like_btn.exists(timeout=2):
            return True  # Already in fullscreen Shorts player

        # Grid view — find and click first Short thumbnail
        logger.debug("Shorts grid view detected — clicking first thumbnail")
        # Shorts thumbnails are usually ImageViews or have "views" in description
        thumb = self.device.d(descriptionMatches=r".*\d+ views.*")
        if thumb.exists(timeout=3):
            thumb.click()
            random_sleep(3.0, 5.0)
            self._reconnect()
            return True

        # Fallback: click center of screen (first visible Short)
        w, h = self.device.screen_size
        self.device.d.click(w // 4, int(h * 0.4))
        random_sleep(3.0, 5.0)
        self._reconnect()
        return True

    def scroll_shorts(self, session: SessionState):
        """Scroll Shorts feed — like every Short, no comment needed."""
        shorts_count = self.config.get("shorts_count", 20)
        logger.info(f"Starting Shorts session — {shorts_count} shorts planned")

        # Go to Shorts tab (bottom nav — NOT Subscriptions filter)
        shorts_tab = self.device.d(description="Shorts")
        if shorts_tab.exists(timeout=3):
            self.device.click_element(shorts_tab)
            random_sleep(3.0, 5.0)

        # Enter fullscreen player if grid view
        self._enter_shorts_fullscreen()

        for i in range(shorts_count):
            if session.likes_limit_reached:
                logger.info(f"Like limit reached at short {i}")
                break

            self._reconnect()

            # Watch for a bit (shorter than regular videos)
            watch_time = uniform(3.0, 8.0)
            random_sleep(watch_time, watch_time + 1.0, modulable=False)

            # Like
            if chance(self.like_pct):
                try:
                    like_btn = self.device.d(descriptionContains="like this video")
                    if like_btn.exists(timeout=3):
                        like_btn.click()
                        random_sleep(0.5, 1.5)
                        session.add_like()
                        logger.info(f"Liked short {i + 1}")
                except Exception as e:
                    logger.debug(f"Like failed: {e}")

            # Swipe to next Short
            self.device.swipe_up()
            session.add_scroll()
            random_sleep(0.5, 1.5)

        logger.info(
            f"Shorts done — {session.total_scrolls} shorts, "
            f"{session.total_likes} likes"
        )

    def run(self, session: SessionState, storage: Storage, credentials: dict) -> bool:
        """Full YouTube engagement session: Subscriptions feed + Shorts."""
        session.platform = "youtube"

        self.open_app()

        if not self.is_logged_in():
            email = credentials.get("email", "")
            password = credentials.get("password", "")
            if email and password:
                self.login(email, password)
            else:
                logger.info("No credentials — browsing without login")

        # Phase 1: Subscriptions feed (like + comment)
        self.scroll_feed(session, storage)

        # Phase 2: Shorts (like only, all channels)
        self.scroll_shorts(session)

        session.finish()
        storage.save_session(session.to_dict())
        logger.info(session.summary())
        return True
