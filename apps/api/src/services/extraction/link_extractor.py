import re

URL_PATTERN = re.compile(
    r'(https?://[^\s,;)"\'<>]+|www\.[^\s,;)"\'<>]+)',
    re.IGNORECASE,
)


def extract_links(text: str) -> list[str]:
    if not text:
        return []
    raw_matches = URL_PATTERN.findall(text)
    cleaned = []
    for match in raw_matches:
        url = match.rstrip(".,;:)")
        if not url.startswith("http"):
            url = "https://" + url
        cleaned.append(url)
    return list(dict.fromkeys(cleaned))  # dedupe, preserve order


def classify_link(url: str) -> str:
    lowered = url.lower()
    if "github.com" in lowered:
        return "github"
    if "linkedin.com" in lowered:
        return "linkedin"
    if "behance.net" in lowered:
        return "behance"
    if any(domain in lowered for domain in ["medium.com", "dev.to", "hashnode.com"]):
        return "blog"
    return "personal_site"


def extract_and_classify_links(text: str) -> list[dict]:
    links = extract_links(text)
    return [{"url": url, "type": classify_link(url)} for url in links]