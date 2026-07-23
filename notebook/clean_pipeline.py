"""
Pipeline de nettoyage AfriMarket — prototype validé en script avant intégration au notebook.
Logique basée sur l'audit initial (PowerShell) :
- 100 doublons stricts
- Villes : "Kinshassa" -> "Kinshasa"
- Catégories : "electronique" -> "Électronique"
- Statuts : casse incohérente (Livrée / retournée / Annulée)
- 614 remises négatives (min -0.1)
- 632 prix_unitaire <= 0 (min -50)
- 608 quantite == 0
- Pas de colonne de coût produit -> marge estimée via hypothèse de taux de marge par catégorie
"""
import pandas as pd
import numpy as np

RAW_PATH = "../data/afrimarket_dataset_senior.csv"
CLEAN_PATH = "../data/df_clean.csv"

df = pd.read_csv(RAW_PATH)
n_raw = len(df)

# 1. Doublons stricts
n_dup = df.duplicated().sum()
df = df.drop_duplicates()

# 2. Dates
df["date_commande"] = pd.to_datetime(df["date_commande"], format="%Y-%m-%d")

# 3. Villes : correction orthographe
ville_map = {"Kinshassa": "Kinshasa"}
df["ville"] = df["ville"].replace(ville_map)

# 4. Catégories : casse / accents
categorie_map = {"electronique": "Électronique"}
df["categorie"] = df["categorie"].replace(categorie_map)

# 5. Statuts : normaliser la casse (Title Case sur mots, accents conservés)
df["statut_commande"] = df["statut_commande"].str.strip().str.capitalize()

# 6. Remises négatives -> erreur de saisie (signe), on prend la valeur absolue puis on plafonne à 0.5
df["remise"] = df["remise"].abs().clip(upper=0.5)

# 7. Prix aberrants (<=0) -> traités comme valeurs manquantes puis imputés par la médiane du produit
df.loc[df["prix_unitaire"] <= 0, "prix_unitaire"] = np.nan
df["prix_unitaire"] = df.groupby("nom_produit")["prix_unitaire"].transform(
    lambda s: s.fillna(s.median())
)
# fallback si un produit n'a aucune valeur valide : médiane de la catégorie
df["prix_unitaire"] = df.groupby("categorie")["prix_unitaire"].transform(
    lambda s: s.fillna(s.median())
)

# 8. Quantités nulles -> suppression (une commande à 0 article n'est pas une vente réelle)
n_qty_zero = (df["quantite"] == 0).sum()
df = df[df["quantite"] > 0]

# 9. Types numériques (cout_marketing / cout_livraison lus comme string à cause du "0" en tête -> cast propre)
df["cout_marketing"] = df["cout_marketing"].astype(float)
df["cout_livraison"] = df["cout_livraison"].astype(float)

df = df.reset_index(drop=True)

print(f"Lignes brutes        : {n_raw}")
print(f"Doublons supprimés    : {n_dup}")
print(f"Quantités nulles suppr: {n_qty_zero}")
print(f"Lignes après nettoyage: {len(df)}")
print(df.dtypes)
print(df.describe(include='all').T)

df.to_csv(CLEAN_PATH, index=False)
print(f"df_clean sauvegardé -> {CLEAN_PATH}")
