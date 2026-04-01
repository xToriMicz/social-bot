"""TikTok Android app UI selectors — resource IDs and content descriptions.

TikTok package: com.zhiliaoapp.musically (international)
These selectors target TikTok v35+ on Android 14 (API 34).
Selectors may break when TikTok updates — verify with `d.dump_hierarchy()`.
"""

# Package
PACKAGE = "com.zhiliaoapp.musically"
PACKAGE_LITE = "com.ss.android.ugc.trill"

# Login
LOGIN_ME_TAB = {"description": "Profile"}
LOGIN_BUTTON = {"textContains": "Log in"}
LOGIN_USE_EMAIL = {"textContains": "Use phone / email"}
LOGIN_EMAIL_TAB = {"textContains": "Email"}
LOGIN_EMAIL_INPUT = {"resourceId": "com.zhiliaoapp.musically:id/et_login_email"}
LOGIN_PASSWORD_INPUT = {"resourceId": "com.zhiliaoapp.musically:id/et_login_password"}
LOGIN_SUBMIT = {"resourceId": "com.zhiliaoapp.musically:id/btn_login"}

# Feed — For You page
FEED_CONTAINER = {"resourceId": "com.zhiliaoapp.musically:id/view_pager"}
VIDEO_DESCRIPTION = {"resourceId": "com.zhiliaoapp.musically:id/title"}
VIDEO_AUTHOR = {"resourceId": "com.zhiliaoapp.musically:id/user_info"}

# Engagement buttons (right side panel)
LIKE_BUTTON = {"resourceId": "com.zhiliaoapp.musically:id/like_icon"}
LIKE_BUTTON_ALT = {"descriptionContains": "Like"}
LIKED_INDICATOR = {"descriptionContains": "Liked"}

COMMENT_BUTTON = {"resourceId": "com.zhiliaoapp.musically:id/comment_icon"}
COMMENT_BUTTON_ALT = {"descriptionContains": "Comment"}

SHARE_BUTTON = {"resourceId": "com.zhiliaoapp.musically:id/share_icon"}
SHARE_BUTTON_ALT = {"descriptionContains": "Share"}

FOLLOW_BUTTON = {"resourceId": "com.zhiliaoapp.musically:id/follow_icon"}
FOLLOW_BUTTON_ALT = {"descriptionContains": "Follow"}

# Comment section
COMMENT_INPUT = {"resourceId": "com.zhiliaoapp.musically:id/comment_edit"}
COMMENT_INPUT_ALT = {"textContains": "Add comment"}
COMMENT_POST_BUTTON = {"resourceId": "com.zhiliaoapp.musically:id/comment_send"}
COMMENT_POST_ALT = {"descriptionContains": "Post"}

# Navigation
NAV_HOME = {"description": "Home"}
NAV_DISCOVER = {"description": "Discover"}
NAV_INBOX = {"description": "Inbox"}
NAV_PROFILE = {"description": "Profile"}

# Dialogs / popups
POPUP_ALLOW = {"text": "Allow"}
POPUP_NOT_NOW = {"textContains": "Not now"}
POPUP_SKIP = {"textContains": "Skip"}
POPUP_CLOSE = {"descriptionContains": "Close"}
POPUP_OK = {"text": "OK"}
POPUP_CANCEL = {"text": "Cancel"}
