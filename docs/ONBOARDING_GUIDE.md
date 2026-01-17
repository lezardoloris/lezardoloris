# 🚀 Google Ads Expert Onboarding System (SAS)
## Freelance & Agency Edition

Guide complet d'onboarding pour consultants Google Ads freelance et agences.

---

## 📋 Table des Matières

1. [Phase 1: Diagnostic Client](#phase-1--diagnostic-client)
2. [Phase 2: Audit Google Ads](#phase-2--audit-google-ads)
3. [Phase 3: Audit Merchant Center](#phase-3--audit-merchant-center)
4. [Phase 4: Analyse Marché & Volume Recherche](#phase-4--analyse-marché--volume-recherche)
5. [Phase 5: Rapport & Recommandations](#phase-5--rapport--recommandations)
6. [Intégration MCP Data Analysis](#intégration-mcp-data-analysis)

---

## PHASE 1: Diagnostic Client

### 1.1 Collecte d'Informations Préalable

**Avant la première réunion:**

```
📝 Checklist Information Client

Métadonnées Compte:
□ URLs Google Ads / Google Merchant Center
□ Accès au compte Analytics / GA4
□ Accès Merchant Center (si existant)
□ Périmètre eCommerce (produits, catégories, prix)
□ Localisations géographiques principales

Performance Actuelle:
□ Budget mensuel actuel (€/mois)
□ Durée de fonctionnement (mois)
□ Historique ROAS / ROI (3-6 mois)
□ Nombre de campagnes actives
□ Volume de ventes moyen mensuel (€)
□ Coût moyen d'acquisition (CAC)

Objectifs Stratégiques:
□ Objectif ROAS cible
□ Budget mensuel prévu
□ Marché principal (geo targeting)
□ Produits vedettes vs. produits de remplissage
□ Saison / périodes clés
□ Concurrents principaux identifiés
```

### 1.2 Questionnaire Stratégique Initial

**Évaluer:**

```
SCORE DIAG INITIAL (1-5)

Maturité Technique:
- Intégration GA4: ____/5
- Feed produits quality: ____/5
- Tracking conversions: ____/5
- Attribution setup: ____/5
→ Diagnostic: ________

Business Model:
- Comprend ROI vs. ROAS: ____/5
- Segmentation produits: ____/5
- Données historiques: ____/5
→ Potentiel: ________

Problématiques Actuelles (ranking):
1. ________________________
2. ________________________
3. ________________________
```

---

## PHASE 2: Audit Google Ads

### 2.1 Analyse Technique Système

**Utilisation du système:**

```bash
# Extraction complète des données
python google_ads_onboarding.py extract \
  -c config/google-ads.yaml \
  -i CUSTOMER_ID \
  -d 30 \
  -o data/client_data.json
```

**Checklist automatique:**

Le système extrait et analyse automatiquement :
- ✅ Structure campagnes et naming convention
- ✅ Segmentation (géo / type produit / funnel stage)
- ✅ Conversion tracking setup
- ✅ Shopping setup et Merchant Center link
- ✅ Product feed quality
- ✅ Performance metrics (ROAS, CTR, CPC, etc.)

### 2.2 Analyse Données (30 jours)

**Le système génère automatiquement:**

```json
{
  "campaigns": [
    {
      "name": "Shopping - Best Sellers",
      "impressions": 50000,
      "clicks": 2000,
      "ctr": 0.04,
      "avg_cpc": 1.25,
      "cost": 2500,
      "conversions": 125,
      "conversion_value": 6250,
      "roas": 2.5
    }
  ],
  "keywords": [...],
  "products": [...],
  "search_terms": [...]
}
```

### 2.3 Diagnostic Rapide

Le système classe automatiquement les campagnes :

- 🏆 **Excellent** (ROAS ≥ 4.0)
- ✅ **Bon** (ROAS ≥ 2.5)
- 🔶 **Moyen** (ROAS ≥ 1.5)
- ⚠️ **Faible** (ROAS ≥ 0.8)
- 🚨 **Critique** (ROAS < 0.8)

---

## PHASE 3: Audit Merchant Center

### 3.1 Analyse Feed Produits

**Extraction automatique:**

```bash
# L'extraction inclut les données Shopping
python google_ads_onboarding.py extract ...
```

**Le système analyse:**

```
PRODUCT FEED HEALTH SCORE

Données extraites:
- Total produits trackés
- Performance par catégorie
- Produits faible ROAS
- Produits haute performance
- Dépenses par catégorie
```

### 3.2 Optimization Levers

Le rapport JSON inclut :

```json
{
  "shopping": {
    "summary": {
      "total_products_tracked": 450,
      "overall_roas": 2.15
    },
    "by_category_l1": {
      "Chaussures": {
        "count": 120,
        "total_spend": 5000,
        "avg_roas": 3.2
      }
    },
    "low_roas_products": [...],
    "high_roas_products": [...]
  }
}
```

---

## PHASE 4: Analyse Marché & Volume Recherche

### 4.1 Recherche Mots-clés Stratégique

**Utilisation du Keyword Planner:**

```bash
python google_ads_onboarding.py keyword-research \
  -c config/google-ads.yaml \
  -i CUSTOMER_ID \
  -k "mot-clé1,mot-clé2,mot-clé3" \
  -l "france,belgium" \
  -o keyword_analysis.json
```

**Résultat:**

```json
{
  "summary": {
    "total_monthly_searches": 125000,
    "weighted_avg_cpc": 1.85,
    "market_opportunity_monthly_eur": 9250,
    "market_opportunity_annual_eur": 111000
  },
  "top_keywords": [
    {
      "keyword": "chaussures running",
      "avg_monthly_searches": 18000,
      "competition": "MEDIUM",
      "avg_cpc_eur": 1.95
    }
  ]
}
```

### 4.2 Analyse Concurrentielle

**Via Keyword Planner - URL seed:**

```python
# Utiliser la fonction competitor_keyword_research
analyzer.competitor_keyword_research(
    competitor_domains=["competitor1.com", "competitor2.com"],
    location_names=["france"]
)
```

### 4.3 Market Sizing Calculation

Le système calcule automatiquement le TAM (Total Addressable Market) :

```json
{
  "market_opportunity_monthly_eur": 9250,
  "market_opportunity_annual_eur": 111000,
  "estimated_monthly_clicks": 5000
}
```

---

## PHASE 5: Rapport & Recommandations

### 5.1 Executive Summary

**Génération automatique:**

```bash
python google_ads_onboarding.py full-audit \
  -c config/google-ads.yaml \
  -i CUSTOMER_ID \
  --client-name "ClientName"
```

**Produit automatiquement:**

- 📄 `google_ads_data.json` - Données brutes
- 📊 `analysis_report.json` - Analyse complète
- 📋 `EXECUTIVE_SUMMARY.txt` - Résumé exécutif

### 5.2 Utilisation des Templates

**Templates disponibles:**

1. **Diagnostic** : `src/templates/diagnostic_template.md`
   - À remplir avec les données du rapport JSON
   - Variables : `{CLIENT_NAME}`, `{CURRENT_ROAS}`, etc.

2. **Proposition** : `src/templates/proposal_template.md`
   - Modèle complet de proposition commerciale
   - Inclut options de pricing

**Exemple de remplissage:**

```python
import json

# Charger le rapport
with open('analysis_report.json') as f:
    report = json.load(f)

# Extraire les variables
current_roas = report['executive_summary']['current_roas']
forecasted_roas = report['executive_summary']['forecasted_roas']
# etc.

# Remplacer dans le template
with open('src/templates/diagnostic_template.md') as f:
    template = f.read()

template = template.replace('{CURRENT_ROAS}', str(current_roas))
template = template.replace('{FORECASTED_ROAS}', str(forecasted_roas))
# etc.
```

### 5.3 Recommandations Priorisées

Le système génère automatiquement des recommandations classées par priorité :

```json
{
  "priority_recommendations": [
    {
      "priority": 1,
      "category": "Keyword Optimization",
      "action": "Add 23 negative keywords to stop waste (€847.50)",
      "expected_impact": "High",
      "effort": "Low",
      "timeline": "Week 1"
    }
  ]
}
```

---

## INTÉGRATION MCP DATA ANALYSIS

### Configuration

Le système MCP est intégré nativement dans l'analyzer :

```python
from analyzers.mcp_analyzer import GoogleAdsAnalyzer

analyzer = GoogleAdsAnalyzer('google_ads_data.json')
report = analyzer.generate_full_report()
```

### Fonctionnalités MCP

**1. Analyse Campagnes**
```python
campaign_analysis = analyzer.analyze_campaigns()
```

**2. Analyse Mots-clés**
```python
keyword_analysis = analyzer.analyze_keywords()
```

**3. Analyse Shopping**
```python
shopping_analysis = analyzer.analyze_shopping_feed()
```

**4. Forecast ROAS**
```python
forecast = analyzer.forecast_roas(
    current_roas=1.85,
    interventions=[
        'quality_score_optimization',
        'keyword_cleanup',
        'bid_strategy_optimization'
    ]
)
# Retourne: forecasted_roas, improvement_pct, confidence
```

### Interventions Disponibles

| Intervention | Impact ROAS |
|--------------|-------------|
| quality_score_optimization | +15% |
| feed_enhancement | +10% |
| keyword_cleanup | +12% |
| bid_strategy_optimization | +20% |
| negative_keywords | +8% |
| seasonal_budgeting | +18% |
| campaign_restructure | +25% |
| shopping_feed_optimization | +15% |
| landing_page_optimization | +20% |
| audience_targeting | +12% |

---

## 🎯 WORKFLOW COMPLET

### Workflow Recommandé (6 étapes)

#### 1️⃣ CLIENT INITIAL CALL (30 min)
- Utiliser la checklist Phase 1
- Remplir le questionnaire stratégique
- Obtenir accès au compte

#### 2️⃣ TECHNICAL AUDIT (2-3 hours)

```bash
# Lancer l'audit complet
python google_ads_onboarding.py full-audit \
  -c config/google-ads.yaml \
  -i CUSTOMER_ID \
  --client-name "ClientName"
```

#### 3️⃣ MARKET RESEARCH (1-2 hours)

```bash
# Analyser le marché
python google_ads_onboarding.py keyword-research \
  -c config/google-ads.yaml \
  -i CUSTOMER_ID \
  -k "seed,keywords,list" \
  -l "france" \
  -o market_analysis.json
```

#### 4️⃣ PROPOSAL MEETING (45 min)
- Présenter le rapport
- Utiliser `EXECUTIVE_SUMMARY.txt`
- Montrer les quick wins
- Discuter le forecast ROAS

#### 5️⃣ PROPOSAL DELIVERY
- Remplir `proposal_template.md`
- Envoyer sous 24-48h
- Inclure les données du rapport

#### 6️⃣ IMPLEMENTATION KICKOFF
- Suivre la roadmap 90 jours
- Semaine 1 : Quick wins
- Semaines 2-4 : Structure
- Semaines 4-8 : Optimisation
- Semaines 9-12 : Scaling

---

## 📊 ENGAGEMENT PRICING FRAMEWORK

### Option A: Pure Management
**€2,500-3,500/mois**
- Gestion complète
- ROAS > 2.0
- Predictable cost

### Option B: Hybrid Performance
**€1,500 + 15% commission**
- Revenus additionnels
- ROAS < 2.0
- Aligned incentives

### Option C: Sprint Project
**€4,500-7,500 (4 semaines)**
- Intensive optimization
- Team training
- ROI 150-300%

### Option D: Retainer Light
**€800-1,200/mois**
- Weekly monitoring
- In-house team support
- Crisis management

---

## ✅ QUALITY CHECKLIST

Avant d'envoyer la proposition :

- [ ] Audit complet exécuté avec succès
- [ ] Rapport JSON généré et vérifié
- [ ] Executive summary consulté
- [ ] Quick wins identifiés (minimum 3)
- [ ] Problèmes critiques listés
- [ ] ROAS forecast calculé et justifié
- [ ] Recherche mots-clés complétée
- [ ] Market opportunity quantifié
- [ ] Template proposition rempli
- [ ] Pricing aligné avec objectifs client
- [ ] Timeline 90 jours documentée
- [ ] Métriques de succès définies

---

## 🔧 TROUBLESHOOTING

### Erreur d'extraction

```bash
# Vérifier la connexion
python src/extractors/google_ads_extractor.py \
  config/google-ads.yaml \
  CUSTOMER_ID
```

### Rapport incomplet

```bash
# Ré-analyser les données
python src/analyzers/mcp_analyzer.py google_ads_data.json
```

### Pas de données Shopping

C'est normal si le compte n'a pas de campagnes Shopping actives.

---

## 📞 SUPPORT

- 📖 [README complet](../README.md)
- 🚀 [Quick Start](../QUICKSTART.md)
- 📝 [Templates](../src/templates/)
- 🔍 [Examples](../examples/)

---

**Version:** 1.0.0
**Dernière mise à jour:** Janvier 2026
**Auteur:** Google Ads Expert SAS
