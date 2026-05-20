from __future__ import annotations

import json

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas import MoralScoreResult, ODDScoreResponse, WebSearchResult
from app.utils import require_env


class LLMError(RuntimeError):
    """Raised when the LLM response cannot be generated or validated."""


def evaluate_odd_scores(
    company_name: str,
    web_results: list[WebSearchResult],
    moralscore: MoralScoreResult,
) -> ODDScoreResponse:
    api_key = require_env("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(company_name, web_results, moralscore),
                },
            ],
        )
    except OpenAIError as exc:
        raise LLMError(f"Erreur OpenAI: {exc}") from exc

    content = completion.choices[0].message.content or ""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMError(f"Reponse OpenAI non JSON: {exc}") from exc

    try:
        return ODDScoreResponse.model_validate(payload)
    except ValidationError as exc:
        raise LLMError(f"JSON OpenAI invalide selon le schema ODD: {exc}") from exc