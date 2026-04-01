"""Social Bot — main entry point."""

import json
import logging
import sys
from time import sleep

from core.device import Device
from core.session import SessionState
from core.storage import Storage
from core.utils import setup_logging, set_speed_multiplier
from platforms.facebook.engage import FacebookBot
from platforms.tiktok.engage import TikTokBot
from platforms.youtube.engage import YouTubeBot

logger = logging.getLogger("social-bot")


def load_config(path: str = "config/default.json") -> dict:
    with open(path) as f:
        return json.load(f)


def parse_mode():
    """Parse run mode from arguments: --shorts, --feed, or both (default)."""
    if "--shorts" in sys.argv:
        return "shorts"
    if "--feed" in sys.argv:
        return "feed"
    return "both"


def main():
    setup_logging("INFO")
    mode = parse_mode()
    logger.info(f"Social Bot starting... (mode: {mode})")

    config = load_config()
    delay_cfg = config.get("delay", {})
    set_speed_multiplier(delay_cfg.get("speed_multiplier", 1.0))

    # Connect to device
    serial = config.get("device", {}).get("serial")
    device = Device(serial)
    logger.info(f"Connected to device: {device.info.get('productName', '?')}")

    # Session loop
    session_cfg = config.get("session", {})
    repeat_delay = session_cfg.get("repeat_delay_minutes", 120)

    while True:
        # Facebook
        fb_config = config.get("platforms", {}).get("facebook", {})
        if fb_config.get("enabled"):
            session = SessionState(config)
            storage = Storage("default", "facebook")

            # Load credentials from accounts/default/facebook/credentials.json
            creds_path = storage.account_dir / "credentials.json"
            credentials = {}
            if creds_path.exists():
                with open(creds_path) as f:
                    credentials = json.load(f)

            fb_bot = FacebookBot(device, config)
            fb_bot.run(session, storage, credentials)

        # YouTube
        yt_config = config.get("platforms", {}).get("youtube", {})
        if yt_config.get("enabled"):
            session = SessionState(config)
            storage = Storage("default", "youtube")

            creds_path = storage.account_dir / "credentials.json"
            credentials = {}
            if creds_path.exists():
                with open(creds_path) as f:
                    credentials = json.load(f)

            yt_bot = YouTubeBot(device, config)
            yt_bot.run(session, storage, credentials, mode=mode)

        # TikTok
        tt_config = config.get("platforms", {}).get("tiktok", {})
        if tt_config.get("enabled"):
            session = SessionState(config)
            storage = Storage("default", "tiktok")

            creds_path = storage.account_dir / "credentials.json"
            credentials = {}
            if creds_path.exists():
                with open(creds_path) as f:
                    credentials = json.load(f)

            tt_bot = TikTokBot(device, config)
            tt_bot.run(session, storage, credentials)

        # Repeat or exit
        if "--once" in sys.argv:
            break

        logger.info(f"Next session in {repeat_delay} minutes")
        sleep(repeat_delay * 60)


if __name__ == "__main__":
    main()
