from __future__ import annotations

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

    return MoralScoreResult(found=bool(summary), url=url, summary=summary)