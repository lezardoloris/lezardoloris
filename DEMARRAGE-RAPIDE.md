# ⚡ Démarrage Ultra-Rapide (5 minutes)

## Prérequis
- ✅ Claude Desktop installé
- ✅ Node.js 18+ installé
- ✅ Un compte Google Ads

---

## 3 Étapes Seulement!

### 1️⃣ Installation (1 min)

```bash
cd /home/user/lezardoloris
npm install
```

---

### 2️⃣ Configuration Google Ads (3 min)

#### Obtenir les 3 credentials nécessaires:

**A. CLIENT_ID et CLIENT_SECRET:**
1. Va sur https://console.cloud.google.com
2. Crée un projet ou utilise un existant
3. Active "Google Ads API"
4. Va dans **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Type: **Desktop app**
6. Ajoute l'URI de redirection: `http://localhost:3001/callback`
7. Note ton **Client ID** et **Client Secret**

**B. DEVELOPER_TOKEN:**
1. Va sur https://ads.google.com
2. **Tools & Settings** → **API Center**
3. Copie ton **Developer Token**

#### Lancer la configuration:
```bash
npm run setup:auth
```

Colle les 3 valeurs quand demandé → Une page web s'ouvre → Approuve → C'est fait!

---

### 3️⃣ Connecter à Claude Desktop (1 min)

#### Option A: Script Automatique (Recommandé)
```bash
npm run build
./scripts/configure-claude-desktop.sh
```

#### Option B: Manuel
```bash
npm run build
```

Édite le fichier de config Claude Desktop:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Copie-colle cette config (en remplaçant les valeurs):

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "node",
      "args": ["/CHEMIN/COMPLET/VERS/lezardoloris/dist/index.js"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "copie_depuis_.env",
        "GOOGLE_ADS_CLIENT_ID": "copie_depuis_.env",
        "GOOGLE_ADS_CLIENT_SECRET": "copie_depuis_.env",
        "GOOGLE_ADS_REFRESH_TOKEN": "copie_depuis_.env",
        "GOOGLE_ADS_CUSTOMER_ID": "copie_depuis_.env"
      }
    }
  }
}
```

Pour copier les valeurs:
```bash
cat .env
```

---

## ✅ C'est Fini!

1. **Ferme complètement Claude Desktop** (Quit, pas juste la fenêtre)
2. **Rouvre Claude Desktop**
3. Regarde en bas → Tu devrais voir 🔌 **google-ads**

---

## 🧪 Tester

Dans Claude Desktop, tape:

```
Show me all my Google Ads campaigns
```

Ou:

```
Analyze my Google Ads performance for the last 30 days
```

Tu devrais voir tes données Google Ads! 🎉

---

## 🆘 Problèmes?

### Le serveur n'apparaît pas dans Claude Desktop
```bash
# Vérifie que le build a marché:
ls -la dist/

# Teste le serveur manuellement:
node dist/index.js
```

### Erreur "Invalid credentials"
```bash
# Vérifie ton .env:
cat .env

# Compare avec la config Claude Desktop
```

### Besoin du chemin complet du projet?
```bash
pwd
# Puis ajoute /dist/index.js à la fin
```

---

## 📚 Plus d'Infos

- Guide détaillé: [GUIDE-FRANCAIS.md](./GUIDE-FRANCAIS.md)
- Exemples de prompts: [EXAMPLES.md](./EXAMPLES.md)
- Documentation complète: [README.md](./README.md)

---

**Besoin d'aide?** Regarde [GUIDE-FRANCAIS.md](./GUIDE-FRANCAIS.md) pour un guide détaillé avec captures d'écran.
