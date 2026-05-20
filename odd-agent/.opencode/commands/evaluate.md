---
description: Evalue une entreprise selon les 17 ODD avec Tavily, MoralScore et OpenAI.
agent: odd-agent
model: openai/gpt-4.1
---

Execute l'evaluateur ESG/RSE local pour l'entreprise suivante: $ARGUMENTS

Important: dans `opencode run`, la sortie stdout/stderr de l'outil bash est deja affichee dans le terminal.
Tu ne dois donc jamais recopier cette sortie dans ta reponse finale.

Commande exacte a utiliser via l'outil bash:

```bash
uv run evaluate "$ARGUMENTS"
```

Contraintes:
- Utilise EXACTEMENT cette commande, sans la modifier.
- Lance la commande une seule fois.
- Ne reformule pas le JSON produit par Python.
- Si la commande reussit, reponds uniquement: Evaluation terminee.
- Si la commande echoue, reponds uniquement par un court diagnostic, sans recopier toute la sortie terminal.
