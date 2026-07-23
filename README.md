# AfriMarket — Analyse Stratégique des Données

Étude Data Analyst complète sur 6 mois d'activité (juillet–décembre 2025) d'AfriMarket,
une entreprise e-commerce panafricaine (Électronique, Mode, Beauté, Maison). Dataset brut
volontairement bruité (doublons, incohérences, valeurs aberrantes) pour simuler un cas réel.

**🔗 Dashboard en ligne :** https://afrimarket-analyse.streamlit.app/

## Livrables

| Livrable | Emplacement |
|---|---|
| Notebook d'analyse (audit → cleaning → feature engineering → 5 analyses) | [`notebook/analyse_afrimarket.ipynb`](notebook/analyse_afrimarket.ipynb) |
| Export HTML du notebook (lisible sans Jupyter) | [`notebook/analyse_afrimarket.html`](notebook/analyse_afrimarket.html) |
| Dashboard interactif Streamlit | [`dashboard/app.py`](dashboard/app.py) |
| Résumé exécutif + 5 recommandations + conclusion | [`reports/resume_executif_afrimarket.docx`](reports/resume_executif_afrimarket.docx) |

## Résultats clés

- **CA total** : 2 500 434 · **Profit net estimé** : 410 380 · **Taux de retour** : 8,1 % · **Taux d'annulation** : 1,9 %
- Électronique génère 75 % du CA mais concentre le plus faible taux de marge (15 %) et le plus fort taux de retour (14 %) — catégorie à optimiser plutôt qu'à accélérer telle quelle.
- **Douala** affiche un taux d'annulation de 13 %, stable chaque mois, contre ~0 % partout ailleurs — signal opérationnel local, pas un problème de demande.
- Le canal **Email** a de loin le meilleur ROI marketing (224) pour un coût quasi nul — levier rentable sous-exploité.
- 31,6 % des clients génèrent 80 % du chiffre d'affaires (Pareto) ; 74 % de clients récurrents.

Détail complet des 5 recommandations stratégiques dans le résumé exécutif.

## Structure du dépôt

```
data/                   datasets bruts, nettoyés et enrichis (features)
notebook/               notebook d'analyse + export HTML
dashboard/              application Streamlit
reports/                résumé exécutif (.docx)
requirements.txt        dépendances du dashboard (déploiement)
```

## Lancer le dashboard en local

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

## Reproduire l'analyse (notebook)

Dépendances supplémentaires pour exécuter le notebook et régénérer le résumé exécutif :

```bash
pip install matplotlib seaborn nbformat nbconvert jupyter ipykernel python-docx
jupyter nbconvert --to notebook --execute --inplace notebook/analyse_afrimarket.ipynb
```

## Méthodologie — hypothèses documentées

Le dataset ne fournit aucun coût produit : la marge brute est estimée via un taux de marge
par catégorie (Électronique 15 %, Mode 45 %, Beauté 55 %, Maison 35 %), détaillé et justifié
dans le notebook. Une commande *Annulée* ne génère aucun chiffre d'affaires ; une commande
*Retournée* est comptée dans le CA mais signalée comme risque qualité.
