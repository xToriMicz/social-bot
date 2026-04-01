"""Facebook Android app UI selectors — resource IDs and text patterns."""

# Package
PACKAGE = "com.facebook.katana"

# Login
LOGIN_EMAIL = {"resourceId": "com.facebook.katana:id/login_username"}
LOGIN_PASSWORD = {"resourceId": "com.facebook.katana:id/login_password"}
LOGIN_BUTTON = {"resourceId": "com.facebook.katana:id/login_login"}

# Feed
FEED_LIST = {"resourceId": "com.facebook.katana:id/recycler_view"}
FEED_POST_TEXT = {"resourceId": "com.facebook.katana:id/native_text"}

# Reactions
LIKE_BUTTON = {"description": "Like"}
LIKED_BUTTON = {"descriptionContains": "Liked"}

# Comment
COMMENT_BUTTON = {"description": "Comment"}
COMMENT_INPUT = {"resourceId": "com.facebook.katana:id/composer_text_view"}
COMMENT_POST_BUTTON = {"description": "Post"}

# Share
SHARE_BUTTON = {"description": "Share"}

# Navigation
NAV_FEED = {"description": "News Feed"}
NAV_MENU = {"description": "Menu"}
