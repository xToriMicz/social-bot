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

logger = logging.getLogger("social-bot")


def load_config(path: str = "config/default.json") -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    setup_logging("INFO")
    logger.info("Social Bot starting...")

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

        # YouTube (placeholder)
        yt_config = config.get("platforms", {}).get("youtube", {})
        if yt_config.get("enabled"):
            logger.info("YouTube: not implemented yet")

        # TikTok (placeholder)
        tt_config = config.get("platforms", {}).get("tiktok", {})
        if tt_config.get("enabled"):
            logger.info("TikTok: not implemented yet")

        # Repeat or exit
        if "--once" in sys.argv:
            break

        logger.info(f"Next session in {repeat_delay} minutes")
        sleep(repeat_delay * 60)


if __name__ == "__main__":
    main()
