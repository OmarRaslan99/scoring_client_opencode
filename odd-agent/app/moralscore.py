from __future__ import annotations

import json
import re

import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from app.schemas import MoralScoreResult
from app.utils import clean_text


BASE_URL = "https://moralscore.org/companies"


def company_to_slug(company_name: str) -> str:
    normalized = unidecode(company_name).lower().replace("&", " and ")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-")


def fetch_moralscore(company_name: str, timeout: int = 15) -> MoralScoreResult:
    slug = company_to_slug(company_name)
    url = f"{BASE_URL}/{slug}/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return MoralScoreResult(found=False, url=url, summary=f"Erreur reseau MoralScore: {exc}")

    if response.status_code != 200:
        return MoralScoreResult(
            found=False,
            url=url,
            summary=f"Page MoralScore non trouvee ou inaccessible, statut HTTP {response.status_code}.",
        )

    soup = BeautifulSoup(response.text, "html.parser")

    global_score: int | None = None
    for ld_tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(ld_tag.string or "")
            if isinstance(data, dict) and data.get("@type") == "AggregateRating":
                raw = data.get("ratingValue")
                if raw is not None:
                    global_score = int(float(raw))
                    break
        except (ValueError, TypeError):
            continue

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    meta_description = soup.find("meta", attrs={"name": "description"})
    description = ""
    if meta_description and meta_description.get("content"):
        description = clean_text(str(meta_description["content"]), 1200)

    title = clean_text(soup.title.string if soup.title else "", 300)
    main = soup.find("main") or soup.body or soup
    page_text = clean_text(main.get_text(" ", strip=True), 3500)
    summary = clean_text(" | ".join(part for part in [title, description, page_text] if part), 4500)

    return MoralScoreResult(found=bool(summary), url=url, global_score=global_score, summary=summary)