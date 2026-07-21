import uuid
import json as json_module

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.candidate import Candidate
from src.models.portfolio_link import PortfolioLink
from src.models.user import User
from src.services.extraction.link_extractor import extract_and_classify_links
from src.services.portfolio.website_analyzer import summarize_personal_site
from src.services.portfolio.github_analyzer import (
    parse_github_url,
    analyze_github_profile,
    analyze_github_repo,
    compute_technical_signal_score,
)
from src.deps import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/{candidate_id}/extract-links")
def extract_candidate_links(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    text_links = extract_and_classify_links(candidate.raw_text or "")

    embedded_urls = json_module.loads(candidate.embedded_links) if candidate.embedded_links else []
    embedded_link_dicts = extract_and_classify_links(" ".join(embedded_urls))

    all_links = {link["url"]: link for link in (text_links + embedded_link_dicts)}.values()

    created = []
    for link in all_links:
        summary = None
        if link["type"] in ("personal_site", "blog"):
            result = summarize_personal_site(link["url"])
            summary_parts = []
            if result.get("summary"):
                summary_parts.append(result["summary"])
            if result.get("notable_signals"):
                summary_parts.append("Notable: " + "; ".join(result["notable_signals"]))
            summary = " ".join(summary_parts) if summary_parts else None

        entry = PortfolioLink(
            candidate_id=candidate.id,
            url=link["url"],
            link_type=link["type"],
            summary=summary,
        )
        db.add(entry)
        created.append(entry)

    db.commit()
    for entry in created:
        db.refresh(entry)

    return {
        "candidate_id": candidate.id,
        "links": [
            {"url": e.url, "type": e.link_type, "summary": e.summary}
            for e in created
        ],
    }


@router.post("/{candidate_id}/analyze-github")
def analyze_candidate_github(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    links = db.query(PortfolioLink).filter(
        PortfolioLink.candidate_id == candidate_id,
        PortfolioLink.link_type == "github",
    ).all()

    if not links:
        raise HTTPException(status_code=400, detail="No GitHub links found for this candidate. Run extract-links first.")

    profile_data = None
    repo_analyses = []

    for link in links:
        parsed = parse_github_url(link.url)
        if parsed["type"] == "profile":
            profile_data = analyze_github_profile(parsed["username"])
        elif parsed["type"] == "repo":
            result = analyze_github_repo(parsed["username"], parsed["repo"])
            if not result.get("error"):
                repo_analyses.append(result)

    signal = compute_technical_signal_score(profile_data or {}, repo_analyses)

    candidate.github_signal_score = signal["technical_signal_score"]
    db.commit()

    return {
        "candidate_id": candidate_id,
        "profile": profile_data,
        "repositories": repo_analyses,
        **signal,
    }


@router.get("/{candidate_id}")
def get_candidate_links(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    links = db.query(PortfolioLink).filter(PortfolioLink.candidate_id == candidate_id).all()
    return [
        {"url": l.url, "type": l.link_type, "summary": l.summary}
        for l in links
    ]