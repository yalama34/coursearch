from enum import Enum


class ActionType(str, Enum):
    VIEW = "view"
    CLICK_LINK = "click_link"
    LIKE = "like"
    FEEDBACK = "feedback"
