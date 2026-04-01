"""Device facade — wraps uiautomator2 with human-like interactions."""

import uiautomator2 as u2
from random import uniform, randint
from core.utils import random_sleep


class Device:
    """Android device wrapper with human-like touch/swipe."""

    def __init__(self, serial: str | None = None):
        if serial:
            self.d = u2.connect(serial)
        else:
            self.d = u2.connect()  # auto-detect
        self.d.implicitly_wait(10)

    @property
    def info(self) -> dict:
        return self.d.info

    @property
    def screen_size(self) -> tuple[int, int]:
        info = self.d.info
        return info["displayWidth"], info["displayHeight"]

    def find(self, **kwargs):
        """Find UI element — same API as uiautomator2."""
        return self.d(**kwargs)

    def click(self, x: int, y: int):
        """Tap with slight random offset (human-like)."""
        jitter_x = randint(-3, 3)
        jitter_y = randint(-3, 3)
        self.d.click(x + jitter_x, y + jitter_y)
        random_sleep(0.2, 0.5)

    def click_element(self, element):
        """Click a UI element with random delay."""
        bounds = element.info["bounds"]
        cx = randint(bounds["left"] + 5, bounds["right"] - 5)
        cy = randint(bounds["top"] + 5, bounds["bottom"] - 5)
        self.click(cx, cy)

    def swipe_up(self, speed: str = "normal"):
        """Scroll up (swipe from bottom to top) with human-like jitter."""
        w, h = self.screen_size
        sx = int(w * uniform(0.4, 0.6))
        sy = int(h * uniform(0.7, 0.85))
        ex = int(sx + w * uniform(-0.05, 0.05))
        ey = int(h * uniform(0.2, 0.35))
        duration = uniform(0.3, 0.6) if speed == "normal" else uniform(0.15, 0.3)
        self.d.swipe(sx, sy, ex, ey, duration=duration)
        random_sleep(0.5, 1.5)

    def swipe_down(self, speed: str = "normal"):
        """Scroll down (swipe from top to bottom)."""
        w, h = self.screen_size
        sx = int(w * uniform(0.4, 0.6))
        sy = int(h * uniform(0.2, 0.35))
        ex = int(sx + w * uniform(-0.05, 0.05))
        ey = int(h * uniform(0.7, 0.85))
        duration = uniform(0.3, 0.6) if speed == "normal" else uniform(0.15, 0.3)
        self.d.swipe(sx, sy, ex, ey, duration=duration)
        random_sleep(0.5, 1.5)

    def type_text(self, text: str, element=None, typing_delay: tuple = (0.05, 0.15)):
        """Type text character by character with random delay (human-like)."""
        if element:
            element.click()
            random_sleep(0.3, 0.8)
        self.d.clear_text()
        for char in text:
            self.d.send_keys(char)
            random_sleep(typing_delay[0], typing_delay[1])

    def press_back(self):
        """Press back button."""
        self.d.press("back")
        random_sleep(0.3, 0.8)

    def press_home(self):
        """Press home button."""
        self.d.press("home")
        random_sleep(0.3, 0.5)

    def screenshot(self, filename: str = "screenshot.png"):
        """Take screenshot."""
        self.d.screenshot(filename)

    def app_start(self, package: str):
        """Start an app by package name."""
        self.d.app_start(package)
        random_sleep(2.0, 4.0)

    def app_stop(self, package: str):
        """Stop an app."""
        self.d.app_stop(package)

    def current_app(self) -> dict:
        """Get current foreground app info."""
        return self.d.app_current()

    def wait_activity(self, activity: str, timeout: float = 10.0) -> bool:
        """Wait for a specific activity to appear."""
        return self.d.wait_activity(activity, timeout=timeout)

    def exists(self, **kwargs) -> bool:
        """Check if element exists on screen."""
        return self.d(**kwargs).exists(timeout=3)
