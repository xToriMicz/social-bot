"""YouTube Android app UI selectors — verified on emulator-5556.

YouTube package: com.google.android.youtube
Verified on: Pixel 8 AVD, API 34, YouTube latest (Apr 2026)
Selectors may break when YouTube updates — verify with `d.dump_hierarchy()`.
"""

# Package
PACKAGE = "com.google.android.youtube"
HOME_ACTIVITY = ".HomeActivity"  # verified — not WatchWhileActivity

# Navigation bar (bottom)
NAV_HOME = {"description": "Home"}
NAV_SHORTS = {"description": "Shorts"}
NAV_SUBSCRIPTIONS = {"descriptionContains": "Subscriptions"}  # may have ": New content is available" suffix
NAV_YOU = {"description": "You"}

# Toolbar
SEARCH_BUTTON = {"description": "Search"}
CAST_BUTTON = {"description": "Cast"}
CREATE_BUTTON = {"description": "Create"}
NOTIFICATIONS_BUTTON = {"description": "Notifications"}
YOUTUBE_LOGO = {"resourceId": "com.google.android.youtube:id/youtube_logo"}

# Feed (home/subscriptions)
FEED_RESULTS = {"resourceId": "com.google.android.youtube:id/results"}
VIDEO_IN_FEED = {"descriptionMatches": ".*\\d+ minutes?.*seconds?.*"}  # videos show duration in desc
VIDEO_THUMBNAIL = {"resourceId": "com.google.android.youtube:id/thumbnail_layout"}
ACTION_MENU = {"description": "Action menu"}

# Mini player — YouTube opens videos in mini player by default
MINI_PLAYER = {"description": "Expand Mini Player"}

# Video player (full watch mode — after expanding mini player)
LIKE_BUTTON = {"descriptionContains": "like this video"}  # "like this video along with N other people"
LIKE_BUTTON_ACTIVE = {"descriptionContains": "Remove like"}  # may not appear — YouTube keeps same desc after like
DISLIKE_BUTTON = {"descriptionContains": "I dislike this"}
VIDEO_PLAYER = {"description": "Video player"}
PAUSE_BUTTON = {"description": "Pause video"}
NEXT_BUTTON = {"description": "Next video"}
PREVIOUS_BUTTON = {"description": "Previous video"}
FULLSCREEN_BUTTON = {"description": "Enter fullscreen"}
MINIMIZE_BUTTON = {"description": "Minimize"}
CAPTIONS_BUTTON = {"description": "Captions"}
AUTOPLAY_BUTTON = {"descriptionContains": "Autoplay"}
CHANNEL_LINK = {"descriptionContains": "Go to channel"}

# Engagement row (below player — need to scroll down)
SHARE_BUTTON = {"descriptionContains": "Share"}
SUBSCRIBE_BUTTON = {"textContains": "Subscribe"}
SUBSCRIBED_INDICATOR = {"textContains": "Subscribed"}

# Comment section — click comment preview to open, not scroll to "Comments"
COMMENT_SECTION = {"textContains": "Comments"}  # fallback
COMMENT_PREVIEW = {"className": "android.widget.EditText"}  # comment preview area with placeholder
COMMENT_INPUT = {"className": "android.widget.EditText"}  # same element, click to type
COMMENT_INPUT_ALT = {"descriptionContains": "Add a comment"}
COMMENT_SEND_BUTTON = {"description": "Send comment"}  # verified — red arrow button
COMMENT_CLOSE = {"description": "Close"}  # close comment sheet
COMMENT_SORT = {"descriptionContains": "Sort comments"}

# Close minimized player
CLOSE_MINI_PLAYER = {"description": "Close minimized player"}

# Login
SIGN_IN_BUTTON = {"textContains": "Sign in"}
ACCOUNT_BUTTON = {"descriptionContains": "Account"}

# Subscriptions page
SUBS_FILTER_ALL = {"description": "All Selected"}
SUBS_FILTER_ALL_ALT = {"text": "All"}
SUBS_TODAY = {"text": "Today"}
SUBS_VIDEOS = {"text": "Videos"}

# Dialogs / popups (verified on first launch)
POPUP_ALLOW = {"text": "Allow"}
POPUP_DISMISS = {"text": "Dismiss"}
POPUP_NOT_NOW = {"textContains": "Not now"}
POPUP_NO_THANKS = {"textContains": "No thanks"}
POPUP_SKIP = {"textContains": "Skip"}
POPUP_OK = {"text": "OK"}
POPUP_AGREE = {"textContains": "I agree"}
POPUP_GOT_IT = {"textContains": "Got it"}
POPUP_CONTINUE = {"text": "Continue"}
