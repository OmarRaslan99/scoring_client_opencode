from __future__ import annotations

import json

from app.schemas import MoralScoreResult, WebSearchResult


ODD_LABELS = {
    1: "Pas de pauvrete",
    2: "Faim zero",
    3: "Bonne sante et bien-etre",
    4: "Education de qualite",
    5: "Egalite entre les sexes",
    6: "Eau propre et assainissement",
    7: "Energie propre et d'un cout abordable",
    8: "Travail decent et croissance economique",
    9: "Industrie, innovation et infrastructure",
    10: "Inegalites reduites",
    11: "Villes et communautes durables",
    12: "Consommation et production responsables",
    13: "Mesures relatives a la lutte contre les changements climatiques",
    14: "Vie aquatique",
    15: "Vie terrestre",
    16: "Paix, justice et institutions efficaces",
    17: "Partenariats pour la realisation des objectifs",
}


SYSTEM_PROMPT = """
Tu es un analyste ESG/RSE senior charge d'evaluer une entreprise selon les 17 Objectifs de Developpement Durable de l'ONU.

Objectif: produire uniquement un JSON strict, valide et exploitable par machine.

Regles de scoring par ODD:
- -1: impact negatif documente, controverse significative ou risque majeur directement lie a l'ODD.
- 0: aucune preuve materielle suffisante, contribution neutre, non applicable, ou information trop faible.
- 1: contribution positive limitee, indirecte ou peu documentee.
- 2: contribution positive materielle, coherente avec l'activite ou des preuves publiques solides.
- 3: contribution forte, centrale dans le modele d'affaires, mesurable, recente et bien documentee.

Regles de confiance:
- confidence est un entier de 0 a 100.
- Augmente la confiance si plusieurs sources recentes et coherentes convergent.
- Diminue la confiance si les sources sont faibles, anciennes, marketing ou contradictoires.
- Une note de 0 peut avoir une confiance elevee si l'absence de preuve materielle est claire.

Contraintes anti-hallucination:
- Ne jamais inventer d'initiatives, chiffres, controverses, certifications ou partenariats.
- Prioriser les resultats web fournis et MoralScore.
- MoralScore est une source complementaire: l'utiliser pour confirmer ou nuancer, pas comme unique preuve automatique.
- Rester conservateur: en cas de doute, choisir 0 plutot qu'un score positif eleve.
- Les scores doivent refleter l'impact de l'entreprise, pas seulement ses promesses de communication.
- Les controverses serieuses peuvent justifier -1 sur les ODD concernes meme si l'entreprise communique positivement ailleurs.

Contraintes JSON obligatoires:
- Retourne exactement un objet JSON avec la cle "scores".
- "scores" contient exactement 17 objets, un par ODD de 1 a 17.
- Chaque objet contient odd_number, score et confidence.
- Si score est different de 0, ajoute explanation avec une justification courte en une phrase.
- Si score est 0, n'inclus pas explanation.
- N'ajoute aucune cle racine autre que "scores".
- N'ajoute aucun markdown, aucun commentaire, aucun texte avant ou apres le JSON.
""".strip()


def build_user_prompt(
    company_name: str,
    web_results: list[WebSearchResult],
    moralscore: MoralScoreResult,
) -> str:
    payload = {
        "company_name": company_name,
        "odd_labels": ODD_LABELS,
        "web_results": [result.model_dump() for result in web_results],
        "moralscore": moralscore.model_dump(),
        "required_json_shape": {
            "scores": [
                {"odd_number": index, "score": 0, "confidence": 90}
                for index in range(1, 18)
            ]
        },
    }
    return (
        "Evalue l'entreprise ci-dessous selon les 17 ODD. "
        "Utilise les donnees JSON fournies comme seules sources factuelles. "
        "Retourne uniquement le JSON final strict.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )