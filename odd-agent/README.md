# ODD Agent

POC Python/OpenCode pour evaluer automatiquement une entreprise selon les 17 Objectifs de Developpement Durable (ODD) de l'ONU.

Le workflow cible est:

```bash
opencode run "/evaluate BNP Paribas"
```

La commande affiche directement dans le terminal:

- les resultats Tavily,
- le resultat MoralScore,
- le JSON final des scores ODD.

## Architecture

```text
odd-agent/
├── .opencode/
│   ├── commands/
│   │   └── evaluate.md
│   ├── skills/
│   │   ├── odd-analysis.md
│   │   ├── moralscore.md
│   │   ├── web-research.md
│   │   ├── odd-analysis/SKILL.md
│   │   ├── moralscore/SKILL.md
│   │   └── web-research/SKILL.md
│   └── agents/
│       └── odd-agent.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── llm.py
│   ├── prompts.py
│   ├── schemas.py
│   ├── web_search.py
│   ├── moralscore.py
│   └── utils.py
├── .env
├── .python-version
├── opencode.json
├── pyproject.toml
└── README.md
```

Les fichiers `skills/*.md` gardent la structure demandee pour le POC. Les dossiers `skills/*/SKILL.md` rendent aussi les skills compatibles avec la decouverte OpenCode actuelle.

## Installation uv

`uv` est le gestionnaire Python du projet.

Installation si necessaire:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Initialisation deja effectuee dans ce projet:

```bash
uv init odd-agent --python 3.11
cd odd-agent
uv add openai tavily-python beautifulsoup4 requests pydantic python-dotenv unidecode
```

Verifier l'environnement:

```bash
uv run python --version
uv run python -m app.main --help
uv run odd-agent --help
```

## Installation OpenCode

Installation du CLI OpenCode:

```bash
npm install -g opencode-ai
opencode --version
```

Ce projet contient `opencode.json` avec:

- fournisseur OpenAI,
- modele principal `openai/gpt-4.1`,
- agent par defaut `odd-agent`,
- commande projet `/evaluate`.

OpenCode doit voir `OPENAI_API_KEY` dans l'environnement du shell. Charge `.env` avant de lancer `opencode run`:

```bash
set -a
source .env
set +a
```

Alternative: utiliser `/connect` dans le TUI OpenCode et selectionner OpenAI, puis entrer la cle API.

## Configuration .env

Modifier `.env`:

```bash
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

`python-dotenv` charge automatiquement ces variables pour l'application Python. Le `source .env` reste necessaire pour OpenCode lui-meme quand il appelle OpenAI.

## Lancement direct Python

Depuis `odd-agent/`:

```bash
uv run --env-file .env python -m app.main "Airbus"
```

Equivalent via le script console Python du projet:

```bash
uv run --env-file .env odd-agent "Airbus"
```

Wrapper de compatibilite OpenCode, utile si l'agent tente d'appeler `main.py evaluate`:

```bash
uv run --env-file .env main.py evaluate "Airbus"
```

Autre wrapper de compatibilite OpenCode, utile si l'agent tente d'appeler `evaluate.py`:

```bash
uv run --env-file .env evaluate.py "Airbus"
```

## Lancement via OpenCode

Depuis `odd-agent/`:

```bash
set -a
source .env
set +a
opencode run "/evaluate Airbus"
```

Exemple de sortie:

```text
** Resultat Tavily :
	* resultat 1 :
		* titre : ...
		* url : ...
		* contenu/snippet : ...
-------------------------------------
** Resultat MoralScore :
	* found : true
	* url : https://moralscore.org/companies/airbus/
	* summary : ...
-------------------------------------
** Scores ODD :
{
	"scores": [
		{"odd_number": 1, "score": 0, "confidence": 95},
		{"odd_number": 2, "score": 0, "confidence": 95},
		{"odd_number": 3, "score": 0, "confidence": 90}
	]
}
```

Le JSON reel contient toujours exactement 17 entrees, une par ODD.

## Comportement de scoring

- Modele OpenAI: `gpt-4.1`.
- Recherche web: Tavily, limitee a 5 resultats.
- Verification complementaire: scraping simple MoralScore.
- Validation: Pydantic impose exactement 17 ODD, score entier de -1 a 3, confidence de 0 a 100.
- Sortie: aucun fichier genere, affichage terminal uniquement.

## Erreurs courantes

Si `OPENAI_API_KEY` ou `TAVILY_API_KEY` manque, la commande affiche une erreur explicite.

Si MoralScore ne trouve pas l'entreprise, l'analyse continue avec:

```text
found : false
```

Si OpenAI retourne un JSON invalide, l'application s'arrete avec une erreur de validation Pydantic.
