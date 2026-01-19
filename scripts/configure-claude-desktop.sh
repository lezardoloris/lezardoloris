#!/bin/bash

# Script pour configurer automatiquement Claude Desktop avec le serveur MCP Google Ads

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Configuration de Claude Desktop pour Google Ads MCP    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier que .env existe
if [ ! -f .env ]; then
    echo "❌ Erreur: Le fichier .env n'existe pas!"
    echo ""
    echo "Lance d'abord: npm run setup:auth"
    exit 1
fi

# Charger les variables d'environnement
source .env

# Obtenir le chemin absolu du projet
PROJECT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Détecter l'OS et définir le chemin de config
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    CONFIG_PATH="$APPDATA/Claude/claude_desktop_config.json"
else
    echo "❌ Système d'exploitation non reconnu: $OSTYPE"
    exit 1
fi

echo "📁 Chemin de config détecté: $CONFIG_PATH"
echo "📁 Chemin du projet: $PROJECT_PATH"
echo ""

# Créer le répertoire de config s'il n'existe pas
mkdir -p "$(dirname "$CONFIG_PATH")"

# Vérifier si le fichier de config existe déjà
if [ -f "$CONFIG_PATH" ]; then
    echo "⚠️  Le fichier de configuration existe déjà!"
    echo ""
    read -p "Voulez-vous créer une sauvegarde? (o/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        cp "$CONFIG_PATH" "$CONFIG_PATH.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✅ Sauvegarde créée: $CONFIG_PATH.backup.*"
    fi
    echo ""
fi

# Créer la configuration
cat > "$CONFIG_PATH" << EOF
{
  "mcpServers": {
    "google-ads": {
      "command": "node",
      "args": ["$PROJECT_PATH/dist/index.js"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "$GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID": "$GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET": "$GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN": "$GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID": "$GOOGLE_ADS_CUSTOMER_ID"
      }
    }
  }
}
EOF

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ CONFIGURATION TERMINÉE!                ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Le fichier de configuration Claude Desktop est créé:     ║"
echo "║  $CONFIG_PATH"
echo "║                                                            ║"
echo "║  Prochaines étapes:                                        ║"
echo "║                                                            ║"
echo "║  1. Ferme complètement Claude Desktop (Quit)               ║"
echo "║  2. Rouvre Claude Desktop                                  ║"
echo "║  3. Vérifie l'icône 🔌 en bas à droite                     ║"
echo "║  4. Demande à Claude: \"Show me my Google Ads campaigns\"    ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Pour voir la config:"
echo "  cat \"$CONFIG_PATH\""
echo ""
