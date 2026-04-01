"""TikTok Android app UI selectors — based on real dump_hierarchy() from emulator.

Tested on: TikTok latest (APKPure) on Pixel emulator API 34.
Resource IDs are obfuscated (e.g. 'eo8', 'pq_') — use text/description selectors.
"""

# Package
PACKAGE = "com.zhiliaoapp.musically"
PACKAGE_LITE = "com.ss.android.ugc.trill"

# --- Onboarding / First Launch ---
ONBOARD_SKIP = {"text": "Skip"}
ONBOARD_AGE_18 = {"text": "At least 18"}
ONBOARD_AGREE = {"text": "Agree and continue"}
ONBOARD_GOT_IT = {"text": "Got it"}
ONBOARD_SWIPE_UP = {"text": "Swipe up for more"}

# --- Google Credential Manager popup ---
GOOGLE_SIGNIN_CLOSE = {"description": "Close sheet"}
GOOGLE_SIGNIN_CONTINUE = {"text": "Continue"}

# --- Login (Sign Up / Log In page) ---
LOGIN_LINK = {"textContains": "Log in"}
LOGIN_SIGNUP_LINK = {"textContains": "Sign up"}
LOGIN_USE_PHONE_EMAIL = {"text": "Use phone / email / username"}
LOGIN_EMAIL_TAB = {"text": "Email / Username"}
LOGIN_PHONE_TAB = {"text": "Phone"}
LOGIN_CONTINUE_FACEBOOK = {"text": "Continue with Facebook"}
LOGIN_CONTINUE_GOOGLE = {"text": "Continue with Google"}
LOGIN_CONTINUE = {"text": "Continue"}
LOGIN_BACK = {"description": "Back to previous screen"}
LOGIN_REPORT = {"description": "Report a problem"}

# Email/Username input — use className since resource-id is obfuscated
# The first EditText on email login page is the email/username field
# The second (if password page) is the password field
LOGIN_EMAIL_INPUT = {"className": "android.widget.EditText", "instance": 0}
LOGIN_PASSWORD_INPUT = {"className": "android.widget.EditText", "instance": 1}

# --- Feed (For You page) ---
# Navigation bar
NAV_HOME = {"description": "Home"}
NAV_FRIENDS = {"description": "Friends"}
NAV_CREATE = {"description": "Create"}
NAV_INBOX = {"description": "Inbox"}
NAV_PROFILE = {"description": "Profile"}
NAV_FOR_YOU = {"text": "For You"}
NAV_FOLLOWING = {"text": "Following"}
NAV_SEARCH = {"description": "Search"}

# Video description (bottom-left)
VIDEO_DESC = {"resourceId": "com.zhiliaoapp.musically:id/desc"}
VIDEO_AUTHOR = {"descriptionMatches": ".*profile$"}

# --- Engagement buttons (right side) ---
# Like — content-desc includes count, e.g. "Like video. 48.5K likes"
LIKE_BUTTON = {"descriptionContains": "Like video"}
LIKE_BUTTON_ALT = {"descriptionContains": "Like"}
LIKED_INDICATOR = {"descriptionContains": "Liked"}
# Unlike for already-liked state
UNLIKE_BUTTON = {"descriptionContains": "Unlike"}

# Comment — content-desc e.g. "Read or add comments. 470 comments"
COMMENT_BUTTON = {"descriptionContains": "Read or add comments"}
COMMENT_BUTTON_ALT = {"descriptionContains": "comments"}

# Bookmark / Favorites
BOOKMARK_BUTTON = {"descriptionContains": "Favorites"}

# Share — content-desc e.g. "Share video. 378 shares"
SHARE_BUTTON = {"descriptionContains": "Share video"}
SHARE_BUTTON_ALT = {"descriptionContains": "shares"}

# Follow — content-desc e.g. "Follow ronisgoliath"
FOLLOW_BUTTON = {"descriptionContains": "Follow"}

# Sound/Music
SOUND_BUTTON = {"descriptionContains": "Sound:"}

# --- Comment section (after clicking comment button) ---
COMMENT_INPUT = {"textContains": "Add comment"}
COMMENT_INPUT_ALT = {"className": "android.widget.EditText"}
COMMENT_SEND = {"descriptionContains": "Post"}
COMMENT_SEND_ALT = {"descriptionContains": "Send"}

# --- Share sheet ---
SHARE_CLOSE = {"description": "Close"}

# --- Common popups ---
POPUP_ALLOW = {"text": "Allow"}
POPUP_WHILE_USING = {"text": "While using the app"}
POPUP_NOT_NOW = {"textContains": "Not now"}
POPUP_SKIP = {"text": "Skip"}
POPUP_CLOSE = {"description": "Close"}
POPUP_OK = {"text": "OK"}
POPUP_CANCEL = {"text": "Cancel"}
POPUP_GOT_IT = {"text": "Got it"}
POPUP_AGREE = {"text": "Agree and continue"}
POPUP_NOT_INTERESTED = {"text": "Not interested"}

# --- Long press menu ---
LONG_PRESS_LAYOUT = {"resourceId": "com.zhiliaoapp.musically:id/long_press_layout"}
