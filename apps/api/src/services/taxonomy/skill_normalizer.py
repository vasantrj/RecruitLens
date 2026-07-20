from src.services.taxonomy.taxonomy_data import ALIAS_TO_CANONICAL


def normalize_skill(raw_skill: str) -> str:
    """
    Maps a raw skill string to its canonical taxonomy name.
    If not found in the taxonomy, returns the cleaned original (title-cased).
    """
    key = raw_skill.strip().lower()
    if key in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[key]
    return raw_skill.strip().title()


def normalize_skill_list(raw_skills: list[str]) -> set[str]:
    """
    Normalizes a list of raw skills into a deduplicated set of canonical skill names.
    """
    return {normalize_skill(skill) for skill in raw_skills if skill and skill.strip()}