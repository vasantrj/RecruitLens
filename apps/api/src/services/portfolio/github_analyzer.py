import re
import httpx

from src.config import settings

GITHUB_API_BASE = "https://api.github.com"


def _headers():
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def parse_github_url(url: str) -> dict:
    """
    Returns {"type": "profile", "username": "..."} or
            {"type": "repo", "username": "...", "repo": "..."}
    """
    match = re.match(r"https?://github\.com/([^/]+)/?$", url)
    if match:
        return {"type": "profile", "username": match.group(1)}

    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/?$", url)
    if match:
        return {"type": "repo", "username": match.group(1), "repo": match.group(2)}

    return {"type": "unknown"}


def analyze_github_profile(username: str) -> dict:
    with httpx.Client(timeout=10.0) as client:
        user_resp = client.get(f"{GITHUB_API_BASE}/users/{username}", headers=_headers())
        if user_resp.status_code != 200:
            return {"error": f"GitHub user not found or API error ({user_resp.status_code})"}
        user_data = user_resp.json()

        repos_resp = client.get(
            f"{GITHUB_API_BASE}/users/{username}/repos",
            headers=_headers(),
            params={"sort": "updated", "per_page": 10},
        )
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        language_counts = {}
        total_stars = 0
        for repo in repos:
            if repo.get("fork"):
                continue
            lang = repo.get("language")
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1
            total_stars += repo.get("stargazers_count", 0)

        top_languages = sorted(language_counts.items(), key=lambda x: -x[1])[:5]

        return {
            "username": username,
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "account_created": user_data.get("created_at"),
            "top_languages": [lang for lang, _ in top_languages],
            "total_stars_recent_repos": total_stars,
            "recent_repo_names": [r["name"] for r in repos[:5] if not r.get("fork")],
        }


def analyze_github_repo(username: str, repo: str) -> dict:
    with httpx.Client(timeout=10.0) as client:
        repo_resp = client.get(f"{GITHUB_API_BASE}/repos/{username}/{repo}", headers=_headers())
        if repo_resp.status_code != 200:
            return {"error": f"GitHub repo not found or API error ({repo_resp.status_code})"}
        repo_data = repo_resp.json()

        readme_resp = client.get(f"{GITHUB_API_BASE}/repos/{username}/{repo}/readme", headers=_headers())
        has_readme = readme_resp.status_code == 200

        langs_resp = client.get(f"{GITHUB_API_BASE}/repos/{username}/{repo}/languages", headers=_headers())
        languages = list(langs_resp.json().keys()) if langs_resp.status_code == 200 else []

        return {
            "repo_name": repo_data.get("name"),
            "description": repo_data.get("description"),
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "languages": languages,
            "has_readme": has_readme,
            "last_updated": repo_data.get("updated_at"),
        }


def compute_technical_signal_score(profile_data: dict, repo_analyses: list[dict]) -> dict:
    """
    Turns raw GitHub signals into a normalized 0-100 'technical signal' score.
    Deliberately capped in influence — this is one input among many, not a dominant factor.
    """
    score = 0.0

    if profile_data and not profile_data.get("error"):
        repo_count = profile_data.get("public_repos", 0)
        score += min(repo_count, 10) * 2  # up to 20 pts for repo count

        star_count = profile_data.get("total_stars_recent_repos", 0)
        score += min(star_count, 20) * 1  # up to 20 pts for stars

        lang_diversity = len(profile_data.get("top_languages", []))
        score += min(lang_diversity, 5) * 4  # up to 20 pts for language diversity

    readme_bonus = sum(5 for r in repo_analyses if r.get("has_readme"))
    score += min(readme_bonus, 20)  # up to 20 pts for documented repos

    active_bonus = min(len(repo_analyses) * 4, 20)  # up to 20 pts for having analyzable repos
    score += active_bonus

    return {
        "technical_signal_score": round(min(score, 100), 2),
    }