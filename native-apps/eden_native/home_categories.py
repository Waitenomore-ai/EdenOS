"""Approved iMac home-screen routes for native desktop staging.

Only activities currently implemented by the cross-platform prototype appear here.
The original iMac catalogue remains the authority for the complete release.
"""
HOME_CATEGORIES = {
    "play": ("story-garden", "puzzle-pond", "nature-explorer", "feelings"),
    "learn": ("number-meadow", "word-woodland", "my-day"),
    "create": ("art-studio",),
}


def activities_in_category(category):
    return HOME_CATEGORIES.get(category, ())
