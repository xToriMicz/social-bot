"""YouTube Android app UI selectors — resource IDs and content descriptions.

YouTube package: com.google.android.youtube
These selectors target YouTube on Android 14 (API 34).
Selectors may break when YouTube updates — verify with `d.dump_hierarchy()`.
"""

# Package
PACKAGE = "com.google.android.youtube"
MAIN_ACTIVITY = "com.google.android.apps.youtube.app.watchwhile.WatchWhileActivity"

# Navigation bar
NAV_HOME = {"description": "Home"}
NAV_SHORTS = {"description": "Shorts"}
NAV_SUBSCRIPTIONS = {"description": "Subscriptions"}
NAV_LIBRARY = {"description": "Library"}

# Toolbar
SEARCH_BUTTON = {"description": "Search"}
MORE_OPTIONS = {"description": "More options"}
YOUTUBE_LOGO = {"resourceId": "com.google.android.youtube:id/youtube_logo"}

# Feed
FEED_RESULTS = {"resourceId": "com.google.android.youtube:id/results"}
VIDEO_TITLE = {"resourceId": "com.google.android.youtube:id/title"}
VIDEO_THUMBNAIL = {"resourceId": "com.google.android.youtube:id/thumbnail"}
VIDEO_BODY = {"resourceId": "com.google.android.youtube:id/body_text"}

# Video player (when watching a video)
LIKE_BUTTON = {"descriptionContains": "like this video"}
LIKE_BUTTON_ALT = {"descriptionContains": "Like"}
DISLIKE_BUTTON = {"descriptionContains": "Dislike"}
SHARE_BUTTON = {"descriptionContains": "Share"}
COMMENT_BUTTON = {"descriptionContains": "Comments"}
SUBSCRIBE_BUTTON = {"textContains": "Subscribe"}
SUBSCRIBED_INDICATOR = {"textContains": "Subscribed"}

# Comment section
COMMENT_INPUT = {"textContains": "Add a comment"}
COMMENT_INPUT_ALT = {"resourceId": "com.google.android.youtube:id/comment_create_edit_text"}
COMMENT_SEND_BUTTON = {"descriptionContains": "Send"}
COMMENT_SEND_ALT = {"resourceId": "com.google.android.youtube:id/send_button"}
COMMENT_SORT = {"descriptionContains": "Sort comments"}

# Login
SIGN_IN_BUTTON = {"textContains": "Sign in"}
ACCOUNT_BUTTON = {"descriptionContains": "Account"}
ACCOUNT_AVATAR = {"descriptionContains": "Go to your channel"}

# Shorts player
SHORTS_LIKE = {"descriptionContains": "Like"}
SHORTS_COMMENT = {"descriptionContains": "Comment"}
SHORTS_SHARE = {"descriptionContains": "Share"}

# Dialogs / popups
POPUP_ALLOW = {"text": "Allow"}
POPUP_NOT_NOW = {"textContains": "Not now"}
POPUP_SKIP = {"textContains": "Skip"}
POPUP_OK = {"text": "OK"}
POPUP_AGREE = {"textContains": "I agree"}
POPUP_NO_THANKS = {"textContains": "No thanks"}
POPUP_UPDATE = {"textContains": "Update"}
POPUP_GOT_IT = {"textContains": "Got it"}
