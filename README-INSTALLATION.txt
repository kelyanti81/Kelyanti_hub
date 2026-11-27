# Mise à jour mobile de Kelyanti Hub

## Installation dans GitHub
Dans ton dépôt, remplace les fichiers/dossiers avec ceux de cette archive :
- `app.py`
- `templates/base.html`
- `templates/login.html`
- `static/style.css`
- ajoute `static/manifest.json`
- ajoute `static/icon.svg`
- ajoute `static/apple-touch-icon.png`
- ajoute `static/app.js`
- ajoute `static/service-worker.js`

Les liens des onglets utilisent des adresses distinctes (`/minecraft`, `/arduino`, `/settings`, etc.). L'adresse change quand tu changes de rubrique, et tu peux partager un lien direct vers une rubrique.

## Installation sur iPhone
Après le déploiement Render :
1. Ouvre le site dans Safari.
2. Appuie sur le bouton Partager.
3. Choisis « Sur l'écran d'accueil ».
4. Appuie sur « Ajouter ».

Kelyanti Hub s'ouvrira alors dans sa propre fenêtre, avec son icône, comme une application.

Le service worker ne met en cache que les fichiers visuels (CSS, JavaScript, icônes). Il ne met pas en cache les pages privées ni les données de connexion.
