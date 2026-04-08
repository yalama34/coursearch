from enum import Enum


class ActionType(str, Enum):
    VIEW = "view"
    CLICK = "click"
    LIKE = "like"
    EXPLICIT = "explicit"
