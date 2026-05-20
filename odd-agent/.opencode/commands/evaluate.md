---
description: Evalue une entreprise selon les 17 ODD avec Tavily, MoralScore et OpenAI.
agent: odd-agent
model: openai/gpt-4.1
---

Execute l'evaluateur ESG/RSE local pour l'entreprise suivante: $ARGUMENTS

Commande exacte a utiliser via l'outil bash:

```bash
uv run --env-file .env python -m app.main "$ARGUMENTS"
```

Contraintes:
- Utilise uniquement la commande exacte ci-dessus.
- Lance la commande une seule fois.
- Ne reformule pas le JSON produit par Python.
- Retourne uniquement la sortie terminal produite par la commande, sans bloc Markdown, sans commentaire et sans reformulation.
