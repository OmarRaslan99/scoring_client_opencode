from __future__ import annotations

import argparse
import json
import sys

from app.llm import LLMError, evaluate_odd_scores
from app.moralscore import fetch_moralscore
from app.schemas import MoralScoreResult, ODDScoreResponse, WebSearchResult
from app.utils import ConfigError, load_environment
from app.web_search import search_company


SEPARATOR = "-------------------------------------"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score une entreprise selon les 17 ODD de l'ONU.")
    parser.add_argument("company", nargs="+", help="Nom de l'entreprise a evaluer")
    return parser


def print_tavily_results(results: list[WebSearchResult]) -> None:
    print("** Resultat Tavily :")
    if not results:
        print("  Aucun resultat Tavily exploitable.")
    for index, result in enumerate(results, start=1):
        print(f"  * resultat {index} :")
        print(f"    * titre : {result.title}")
        print(f"    * url : {result.url}")
        print(f"    * contenu/snippet : {result.content}")
    print(SEPARATOR)


def print_moralscore_result(result: MoralScoreResult) -> None:
    print("** Resultat MoralScore :")
    print(f"  * found : {str(result.found).lower()}")
    print(f"  * url : {result.url}")
    if result.global_score is not None:
        print(f"  * note globale : {result.global_score}/100")
    print(f"  * summary : {result.summary}")
    print(SEPARATOR)


def print_scores(scores: ODDScoreResponse) -> None:
    print("** Scores ODD :")
    print(json.dumps(scores.model_dump(exclude_none=True), ensure_ascii=False, indent=2))


def run(company_name: str) -> int:
    load_environment()
    web_results = search_company(company_name)
    moralscore = fetch_moralscore(company_name)
    scores = evaluate_odd_scores(company_name, web_results, moralscore)

    print_tavily_results(web_results)
    print_moralscore_result(moralscore)
    print_scores(scores)
    return 0


def cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    company_name = " ".join(args.company).strip()
    if not company_name:
        parser.error("Le nom de l'entreprise est obligatoire.")

    try:
        return run(company_name)
    except (ConfigError, LLMError, RuntimeError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())