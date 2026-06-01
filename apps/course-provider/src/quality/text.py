import re

from bs4 import BeautifulSoup


def strip_html(text: str | None) -> str | None:
    if text is None:
        return None

    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text(separator=" ", strip=True)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned or None
