# 🚀 Guide Ultra-Simple - Claude Desktop + Google Ads

## Étape 1: Préparer le projet (2 min)

Ouvre un terminal et va dans le dossier du projet:

```bash
cd /home/user/lezardoloris
npm install
```

Attends que toutes les dépendances s'installent...

---

## Étape 2: Obtenir les credentials Google (5 min)

Tu as besoin de 3 infos de Google Cloud. Voici comment les obtenir:

### A. Va sur Google Cloud Console
👉 [https://console.cloud.google.com](https://console.cloud.google.com)

### B. Crée un projet (si tu n'en as pas)
1. Clique sur le nom du projet en haut
2. Clique "Nouveau projet"
3. Donne un nom (ex: "Google Ads MCP")
4. Clique "Créer"

### C. Active l'API Google Ads
1. Dans la barre de recherche, tape "Google Ads API"
2. Clique sur "Google Ads API"
3. Clique "Activer"

### D. Crée les credentials OAuth
1. Va dans **APIs & Services** → **Credentials** (dans le menu à gauche)
2. Clique **+ Create Credentials** → **OAuth 2.0 Client ID**
3. Si demandé, configure l'écran de consentement:
   - User Type: **External**
   - Nom de l'app: "Google Ads MCP"
   - Email: ton email
   - Clique "Enregistrer"
4. De retour dans Credentials:
   - Application type: **Desktop app**
   - Nom: "Google Ads MCP Desktop"
   - Clique **Create**
5. **IMPORTANT**: Note ton **Client ID** et **Client Secret**
6. Clique sur le credential que tu viens de créer
7. Ajoute l'URI de redirection: `http://localhost:3001/callback`
8. Clique "Save"

### E. Obtiens le Developer Token
1. Va sur [Google Ads](https://ads.google.com)
2. Clique sur **Tools & Settings** (icône clé à molette)
3. Sous "Setup", clique **API Center**
4. Copie ton **Developer Token**
   - Si tu n'en as pas, clique "Apply for access" (peut prendre 24h d'approbation)
   - Mais tu peux l'utiliser immédiatement en mode test!

---

## Étape 3: Configuration automatique (1 min)

Maintenant, lance la configuration automatique:

```bash
npm run setup:auth
```

Le script va te demander:
1. **CLIENT_ID** → Colle la valeur de l'étape 2.D
2. **CLIENT_SECRET** → Colle la valeur de l'étape 2.D
3. **DEVELOPER_TOKEN** → Colle la valeur de l'étape 2.E

Ensuite:
- Une page web va s'ouvrir automatiquement
- Connecte-toi avec ton compte Google Ads
- Clique "Autoriser"
- Reviens au terminal → Tout est configuré! ✅

Un fichier `.env` a été créé avec tous tes credentials.

---

## Étape 4: Construire le serveur (30 secondes)

```bash
npm run build
```

Attends que la compilation TypeScript se termine...

---

## Étape 5: Configurer Claude Desktop (2 min)

### Sur macOS:
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Sur Windows:
```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

### Sur Linux:
```bash
code ~/.config/Claude/claude_desktop_config.json
```

**Ajoute cette configuration:**

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "node",
      "args": ["/home/user/lezardoloris/dist/index.js"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "ton_developer_token",
        "GOOGLE_ADS_CLIENT_ID": "ton_client_id.apps.googleusercontent.com",
        "GOOGLE_ADS_CLIENT_SECRET": "ton_client_secret",
        "GOOGLE_ADS_REFRESH_TOKEN": "ton_refresh_token",
        "GOOGLE_ADS_CUSTOMER_ID": "1234567890"
      }
    }
  }
}
```

**💡 ASTUCE**: Copie les valeurs directement depuis ton fichier `.env`:

```bash
cat .env
```

Remplace `ton_developer_token`, `ton_client_id`, etc. par les vraies valeurs.

⚠️ **IMPORTANT**: Change `/home/user/lezardoloris/dist/index.js` par le chemin COMPLET vers ton projet!

Pour obtenir le chemin complet:
```bash
pwd
```
Puis ajoute `/dist/index.js` à la fin.

---

## Étape 6: Redémarrer Claude Desktop

1. **Ferme complètement Claude Desktop** (Quit, pas juste fermer la fenêtre)
2. **Rouvre Claude Desktop**
3. Regarde en bas à droite → Tu devrais voir une icône 🔌 avec "google-ads"

---

## ✅ Tester que ça marche

Dans Claude Desktop, tape:

```
Show me all my Google Ads campaigns from the last 30 days
```

Ou:

```
What's my Google Ads account information?
```

Si ça marche, tu verras les données de ton compte Google Ads! 🎉

---

## 🐛 Dépannage

### "MCP server not found"
- Vérifie que le chemin dans `claude_desktop_config.json` est correct (chemin ABSOLU)
- Vérifie que tu as bien fait `npm run build`

### "Invalid credentials"
- Vérifie les valeurs dans `claude_desktop_config.json`
- Compare avec ton fichier `.env`

### "Port 3001 already in use"
Un autre programme utilise le port 3001. Tue-le ou change le port dans `scripts/setup-oauth.ts`.

### Le serveur ne démarre pas
```bash
# Teste manuellement:
node dist/index.js
```

Si tu vois des erreurs, partage-les!

---

## 🎯 Résumé des commandes

```bash
# 1. Installation
cd /home/user/lezardoloris
npm install

# 2. Configuration automatique
npm run setup:auth

# 3. Build
npm run build

# 4. Éditer la config Claude Desktop
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 5. Redémarrer Claude Desktop et c'est parti!
```

---

**Besoin d'aide?** Dis-moi à quelle étape tu bloques! 🚀
