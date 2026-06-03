import re
from collections import Counter
from re import Pattern

from src.quality.constants import MIN_TITLE_LEN, MIN_DESCRIPTION_LEN


_REPEATED_CHAR: Pattern[str] = re.compile(r"(.)\1{5,}")
_REPEATED_CHUNK: Pattern[str] = re.compile(r"(.{2,20}?)\1{3,}")
_ONLY_DIGITS: Pattern[str] = re.compile(r"^\d+$")
_WORD: Pattern[str] = re.compile(r"\w+", re.UNICODE)

def _dominant_word_ratio(text: str) -> float:
    words = _WORD.findall(text.lower())
    if len(words) < 4:
        return 0.0
    return Counter(words).most_common(1)[0][1] / len(words)

def _unique_char_ratio(text: str) -> float:
    compact = re.sub(r"\s+", "", text)
    if len(compact) < 20:
        return 1.0
    return len(set(compact)) / len(compact)

def is_spammy_text(text: str) -> bool:
    text = text.strip()
    if not text:
        return True
    if _REPEATED_CHAR.search(text):
        return True
    if _REPEATED_CHUNK.search(text.replace(" ", "")):
        return True
    if _ONLY_DIGITS.match(text):
        return True
    if _dominant_word_ratio(text) > 0.5:
        return True
    if _unique_char_ratio(text) < 0.15:
        return True
    return False

def is_spammy_course(name: str, description: str | None) -> bool:
    title = (name or "").strip()
    desc = (description or "").strip()

    if len(title) < MIN_TITLE_LEN:
        return True
    if is_spammy_text(title):
        return True
    if not desc or len(desc) < MIN_DESCRIPTION_LEN:
        return True
    if is_spammy_text(desc):
        return True
    return False
