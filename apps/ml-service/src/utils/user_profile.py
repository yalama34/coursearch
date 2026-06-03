def build_user_profile_text(tags: list[str], description: str | None) -> str:
    parts: list[str] = []
    if tags:
        parts.append(" ".join(tags))
    if description and description.strip():
        parts.append(description.strip())
    return " ".join(parts).strip()
