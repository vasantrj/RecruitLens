from src.services.taxonomy.skill_normalizer import normalize_skill_list
from src.services.matching.embeddings import cosine_similarity
from src.services.matching.reranker import rerank_score


def compute_skill_overlap(candidate_skills: list[str], required_skills: list[str], nice_to_have_skills: list[str]) -> dict:
    candidate_set = normalize_skill_list(candidate_skills)
    required_set = normalize_skill_list(required_skills)
    nice_set = normalize_skill_list(nice_to_have_skills)

    matched_required = candidate_set & required_set
    missing_required = required_set - candidate_set
    matched_nice = candidate_set & nice_set

    required_score = len(matched_required) / len(required_set) if required_set else 1.0
    nice_bonus = (len(matched_nice) / len(nice_set)) if nice_set else 0.0

    return {
        "score": round(min(1.0, required_score + 0.1 * nice_bonus), 4),
        "matched_required": sorted(matched_required),
        "missing_required": sorted(missing_required),
        "matched_nice_to_have": sorted(matched_nice),
    }


def compute_experience_match(candidate_years: float, min_years_required: float) -> float:
    if min_years_required <= 0:
        return 1.0
    if candidate_years >= min_years_required:
        return 1.0
    return round(max(0.0, candidate_years / min_years_required), 4)


def compute_title_similarity(candidate_titles: list[str], role_title: str) -> float:
    if not candidate_titles or not role_title:
        return 0.0
    best = max(cosine_similarity(title, role_title) for title in candidate_titles)
    return round(best, 4)


def compute_match_score(
    candidate_data: dict,
    job_data: dict,
    candidate_raw_text: str,
    jd_raw_text: str,
    github_signal_score: float = None,
) -> dict:
    """
    candidate_data: parsed candidate JSON (skills, years_experience, titles_held, summary)
    job_data: parsed job JSON (required_skills, nice_to_have_skills, min_years_experience, role_title)
    github_signal_score: optional 0-100 cached GitHub technical signal score
    """
    skill_result = compute_skill_overlap(
        candidate_data.get("skills", []),
        job_data.get("required_skills", []),
        job_data.get("nice_to_have_skills", []),
    )

    experience_score = compute_experience_match(
        candidate_data.get("years_experience", 0) or 0,
        job_data.get("min_years_experience", 0) or 0,
    )

    title_score = compute_title_similarity(
        candidate_data.get("titles_held", []),
        job_data.get("role_title", ""),
    )

    reranker_score_value = rerank_score(jd_raw_text, candidate_raw_text)

    weights = {
        "skills": 0.38,
        "experience": 0.18,
        "title": 0.14,
        "reranker": 0.22,
    }

    base_score = (
        weights["skills"] * skill_result["score"]
        + weights["experience"] * experience_score
        + weights["title"] * title_score
        + weights["reranker"] * reranker_score_value
    ) * 100

    github_bonus = 0.0
    if github_signal_score is not None:
        # Up to 8 points bonus, scaled by how strong the GitHub signal is.
        # Absence of GitHub data adds nothing and does not penalize the candidate.
        github_bonus = round((github_signal_score / 100) * 8, 2)

    final_score = min(100.0, base_score + github_bonus)

    return {
        "final_score": round(final_score, 2),
        "breakdown": {
            "skill_match_pct": round(skill_result["score"] * 100, 2),
            "experience_match_pct": round(experience_score * 100, 2),
            "title_similarity_pct": round(title_score * 100, 2),
            "reranker_score_pct": round(reranker_score_value * 100, 2),
            "github_bonus_points": github_bonus,
        },
        "matched_required_skills": skill_result["matched_required"],
        "missing_required_skills": skill_result["missing_required"],
        "matched_nice_to_have_skills": skill_result["matched_nice_to_have"],
    }