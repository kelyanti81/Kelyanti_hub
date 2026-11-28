KELYANTI HUB — PACK DE MISE À JOUR

FICHIERS À REMPLACER :
- app.py
- templates/base.html
- templates/section.html
- templates/members.html
- static/style.css
- static/app.js

NOUVEAU FICHIER :
- templates/admin_settings.html

AGENT DELL :
- dossier dell_agent/

AVANT DE COMMENCER :
1. Fais une sauvegarde de ton dépôt GitHub actuel.
2. Ne supprime pas la base Neon et ne change pas DATABASE_URL.
3. Ne remplace pas HUB_USERNAME ni HUB_PASSWORD.
4. Ajoute seulement DELL_AGENT_TOKEN dans Render Environment.

INSTALLATION :
1. Remplace chaque fichier indiqué par celui du pack, en gardant exactement les dossiers.
2. Ajoute templates/admin_settings.html.
3. Commit/push sur GitHub : Render déploiera automatiquement.
4. Ajoute DELL_AGENT_TOKEN dans Render.
5. Configure puis démarre l'agent sur le Dell avec le README du dossier dell_agent.

DONNÉES :
- Le code conserve la table members et les colonnes existantes.
- Il ajoute seulement members.last_seen et la table dell_status.
- Les mots de passe et comptes existants ne sont pas supprimés.
- Les réglages admin sont conservés dans settings.
- Les membres ne peuvent pas consulter l'API de présence des autres membres.

À SAVOIR :
- Un membre est en ligne s'il a envoyé un signal dans les 100 dernières secondes.
- Le Dell est considéré en ligne si son agent a envoyé un signal dans les 110 dernières secondes.
- La surveillance Minecraft contrôle la session tmux nommée kelyanti-mc.
- Ce pack n'a pas été déployé sur ton GitHub ou Render : tu dois importer les fichiers toi-même.
