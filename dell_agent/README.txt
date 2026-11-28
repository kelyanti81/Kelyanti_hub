INSTALLATION DE L'AGENT DELL

1. Sur Render, ouvre ton service Kelyanti Hub > Environment.
2. Ajoute une variable :
   DELL_AGENT_TOKEN = une longue valeur secrète aléatoire.
   Ne la partage pas et ne la mets jamais dans GitHub.
3. Enregistre et attends le redémarrage de Render.

Sur le Dell Ubuntu, installe les dépendances :
   sudo apt update
   sudo apt install python3-psutil tmux -y

Place dell_agent.py dans un dossier privé, puis définis les variables dans le terminal :
   export HUB_URL="https://TON-SERVICE.onrender.com"
   export DELL_AGENT_TOKEN="LA_MEME_VALEUR_QUE_SUR_RENDER"
   export MINECRAFT_TMUX_SESSION="kelyanti-mc"

Lance :
   python3 dell_agent.py

Garde le terminal ouvert pour le test. Le site affichera le Dell comme hors ligne si aucun signal n'arrive depuis environ 110 secondes.

IMPORTANT :
- Remplace TON-SERVICE par l'adresse réelle de ton site Render.
- Ne publie jamais le token.
- Aucun port entrant du Dell n'est nécessaire.
- L'agent vérifie la session tmux nommée kelyanti-mc. Si ton serveur utilise un autre nom, change MINECRAFT_TMUX_SESSION.
- Le plan gratuit Render peut mettre le site en veille ; ce système ne garantit pas une disponibilité permanente.
