# 🚀 QUICKSTART - Google Ads Onboarding System

Ce guide vous permet de démarrer en 10 minutes.

## ⚡ Installation Rapide

### 1. Cloner et Installer

```bash
# Cloner le repository
git clone <your-repo-url>
cd lezardoloris

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration Google Ads API

```bash
# Lancer l'assistant
python google_ads_onboarding.py setup
```

Cela créera `config/google-ads.yaml`. Remplissez-le avec vos credentials :

```yaml
developer_token: VOTRE_TOKEN
client_id: VOTRE_CLIENT_ID.apps.googleusercontent.com
client_secret: VOTRE_SECRET
refresh_token: VOTRE_REFRESH_TOKEN
login_customer_id: VOTRE_MCC_ID
use_proto_plus: True
```

> **Aide:** Consultez [ce guide](https://developers.google.com/google-ads/api/docs/first-call/overview) pour obtenir vos credentials.

### 3. Premier Audit

```bash
# Remplacer 1234567890 par votre vrai Customer ID
python google_ads_onboarding.py full-audit \
  -c config/google-ads.yaml \
  -i 1234567890 \
  --client-name "MonPremierClient"
```

### 4. Consulter les Résultats

```bash
# Voir le résumé exécutif
cat audits/MonPremierClient_*/EXECUTIVE_SUMMARY.txt

# Voir le rapport JSON complet
cat audits/MonPremierClient_*/analysis_report.json | python -m json.tool
```

---

## 📊 Exemples d'Utilisation

### Extraction Simple

```bash
python google_ads_onboarding.py extract \
  -c config/google-ads.yaml \
  -i 1234567890 \
  -d 30 \
  -o data/client1.json
```

### Analyse Seule

```bash
python google_ads_onboarding.py analyze \
  -d data/client1.json \
  -o reports/client1_analysis.json
```

### Recherche Mots-clés

```bash
python google_ads_onboarding.py keyword-research \
  -c config/google-ads.yaml \
  -i 1234567890 \
  -k "produit1,produit2,produit3" \
  -l "france,belgium" \
  -o reports/keywords.json
```

---

## 🎯 Workflow Typique

### Nouveau Client

1. **Appel découverte** (30 min)
   - Comprendre le besoin
   - Demander l'accès au compte Google Ads

2. **Audit complet** (2h)
   ```bash
   python google_ads_onboarding.py full-audit \
     -c config/google-ads.yaml \
     -i CUSTOMER_ID \
     --client-name "NomClient"
   ```

3. **Analyser les résultats** (1h)
   - Ouvrir `audits/NomClient_*/analysis_report.json`
   - Identifier les quick wins
   - Noter les problèmes critiques

4. **Préparer la proposition** (1h)
   - Utiliser `src/templates/proposal_template.md`
   - Remplir avec les données du rapport
   - Calculer le ROI projeté

5. **Présentation client** (45 min)
   - Montrer les findings
   - Présenter le plan d'action
   - Proposer l'engagement

---

## 🔍 Comprendre les Rapports

### Executive Summary

```json
{
  "executive_summary": {
    "current_roas": 1.85,           // ROAS actuel
    "forecasted_roas": 2.89,        // ROAS après optimisation
    "improvement_potential": 56.2,  // % d'amélioration possible
    "total_spend": 15420.50,        // Dépenses analysées
    "total_revenue": 28527.93,      // Revenus générés
    "critical_issues_count": 2      // Problèmes urgents
  }
}
```

### Priority Recommendations

Les recommandations sont classées par priorité :

- **Priority 1** 🔴 : Critique - À faire cette semaine
- **Priority 2** 🟠 : Important - À faire ce mois
- **Priority 3** 🟡 : Optimisation - À faire ce trimestre

Chaque recommandation indique :
- **Action** : Quoi faire
- **Expected Impact** : Impact attendu (High/Medium/Low)
- **Effort** : Effort requis (High/Medium/Low)
- **Timeline** : Quand le faire

---

## 🛠️ Commandes Utiles

### Voir l'aide

```bash
python google_ads_onboarding.py --help
python google_ads_onboarding.py extract --help
python google_ads_onboarding.py analyze --help
```

### Tester la connexion API

```bash
# Extraire juste les campagnes pour tester
python google_ads_onboarding.py extract \
  -c config/google-ads.yaml \
  -i CUSTOMER_ID \
  -d 7 \
  -o test.json
```

### Scripts Python Directs

```bash
# Extraction
python src/extractors/google_ads_extractor.py config/google-ads.yaml CUSTOMER_ID

# Analyse
python src/analyzers/mcp_analyzer.py google_ads_data.json

# Keywords
python src/analyzers/keyword_planner_analyzer.py config/google-ads.yaml CUSTOMER_ID
```

---

## 📋 Checklist Premier Audit

- [ ] Accès Google Ads obtenu (au moins Standard)
- [ ] Customer ID récupéré (10 chiffres)
- [ ] Credentials API configurés dans `config/google-ads.yaml`
- [ ] Test de connexion réussi
- [ ] Audit complet lancé
- [ ] Rapport JSON généré
- [ ] Executive summary consulté
- [ ] Quick wins identifiés
- [ ] Problèmes critiques notés
- [ ] ROAS forecast calculé
- [ ] Proposition préparée

---

## ❓ FAQ Rapide

### Comment obtenir le Customer ID ?

Dans Google Ads, en haut à droite, c'est le numéro à 10 chiffres (ex: 123-456-7890).
**Utilisez-le sans les tirets** : `1234567890`

### Erreur "Developer token not approved" ?

Votre token doit être approuvé par Google. En test, utilisez un compte manager (MCC) avec le token en mode test.

### Erreur "Permission denied" ?

Vérifiez que :
1. Le compte a bien les droits Standard ou Admin
2. Le login_customer_id correspond à votre MCC (si applicable)
3. Le refresh_token est valide

### Combien de temps prend un audit ?

- **Extraction** : 2-5 minutes
- **Analyse** : 30 secondes
- **Total** : ~5 minutes pour un compte typique

### Puis-je analyser plusieurs comptes ?

Oui ! Lancez simplement l'audit pour chaque Customer ID :

```bash
for customer_id in 1111111111 2222222222 3333333333; do
  python google_ads_onboarding.py full-audit \
    -c config/google-ads.yaml \
    -i $customer_id \
    --client-name "Client_$customer_id"
done
```

---

## 🎓 Ressources

- [Documentation Google Ads API](https://developers.google.com/google-ads/api)
- [Guide OAuth2](https://developers.google.com/google-ads/api/docs/oauth/overview)
- [Benchmarks Industrie](https://www.wordstream.com/blog/ws/2023/07/06/google-ads-industry-benchmarks)

---

## 🆘 Besoin d'Aide ?

- 📖 Consultez le [README complet](README.md)
- 🐛 [Signaler un bug](issues)
- 💬 [Poser une question](discussions)

---

**Vous êtes prêt ! 🚀**

Lancez votre premier audit et découvrez les opportunités d'optimisation.
