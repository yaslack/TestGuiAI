# TestGuiAI

Application FastAPI qui expose une interface web permettant de lister les modèles disponibles sur un serveur [LM Studio](https://lmstudio.ai/) et d'en sélectionner un.

## Prérequis

- Python 3.10 ou plus récent
- Un serveur LM Studio accessible via HTTP (par défaut `http://localhost:1234`)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement du serveur

Avant de démarrer l'application, vous pouvez définir la variable d'environnement `LM_STUDIO_URL` pour indiquer l'URL de base de votre serveur LM Studio :

```bash
export LM_STUDIO_URL="http://localhost:1234"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ensuite, ouvrez votre navigateur et rendez-vous sur [http://localhost:8000](http://localhost:8000). L'interface permet d'actualiser la liste des modèles puis d'activer celui que vous souhaitez utiliser.

## Personnalisation

- **LM_STUDIO_URL** : URL du serveur LM Studio à interroger.
- Les styles de l'interface se trouvent dans `app/static/styles.css` et peuvent être adaptés.

## Développement

Pour lancer le serveur en mode développement avec rechargement automatique :

```bash
uvicorn app.main:app --reload
```

Les requêtes envoyées à LM Studio sont effectuées via `app/lmstudio.py`. Vous pouvez adapter ce fichier si l'API de LM Studio change ou si vous souhaitez ajouter d'autres opérations (par exemple le téléchargement de modèles).
