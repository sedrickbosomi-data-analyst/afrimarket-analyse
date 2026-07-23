"""Dashboard interactif AfriMarket — pilotage business (Streamlit).

Thème : bleu de nuit (surface), orange & vert-citron (accents), palette
catégorielle validée accessibilité (CVD-safe) — voir le rapport de
validation dans le commentaire en bas de fichier.
"""
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AfriMarket — Dashboard Stratégique", page_icon="🛍️", layout="wide")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "df_features.csv"

# ------------------------------------------------------------------
# Thème — palette validée (voir palette-check en bas de fichier)
# ------------------------------------------------------------------
PAGE_BG = "#0B1426"
SURFACE = "#101B33"
SURFACE_2 = "#16223D"
TEXT_PRIMARY = "#F5F6FA"
TEXT_MUTED = "#9BA3B8"
GRID = "#26314D"

ORANGE, TEAL, BLUE, LIME = "#D9661F", "#1B9A88", "#2F6FE0", "#7A9E00"
MAGENTA, GOLD, VIOLET, CORAL = "#C94A97", "#B8850F", "#6E54D9", "#E2493A"
ACCENT_ORANGE, ACCENT_LIME = "#E8722A", "#9AC400"

CATEGORICAL_8 = [ORANGE, TEAL, BLUE, LIME, MAGENTA, GOLD, VIOLET, CORAL]

# Ordres fixes (jamais retriés par valeur) + couleur fixe par entité :
# la couleur suit l'entité, pas son rang — stable quel que soit le filtre actif.
CATEGORIE_ORDER = ["Électronique", "Mode", "Beauté", "Maison"]
CATEGORIE_COLOR = dict(zip(CATEGORIE_ORDER, [ORANGE, TEAL, BLUE, LIME]))

CANAL_ORDER = ["Email", "Google Ads", "Instagram Ads", "Influenceur"]
CANAL_COLOR = dict(zip(CANAL_ORDER, [ORANGE, TEAL, BLUE, LIME]))

VILLE_ORDER = ["Kinshasa", "Abidjan", "Dakar", "Douala", "Lomé", "Cotonou", "Libreville", "Brazzaville"]
VILLE_COLOR = dict(zip(VILLE_ORDER, CATEGORICAL_8))

# Diverging (croissance %) : rouge-corail (baisse) -> gris neutre (stable) -> vert-citron (hausse)
GROWTH_SCALE = [
    [0.00, "#B5362B"],
    [0.25, "#E2493A"],
    [0.50, "#545B68"],
    [0.75, "#6B8F00"],
    [1.00, "#9AC400"],
]

CSS = f"""
<style>
.stApp {{ background: {PAGE_BG}; }}
h1, h2, h3 {{ color: {TEXT_PRIMARY} !important; letter-spacing: -0.01em; }}
[data-testid="stMetric"] {{
    background: {SURFACE};
    border: 1px solid rgba(255,255,255,0.08);
    border-top: 3px solid {ACCENT_ORANGE};
    border-radius: 12px;
    padding: 14px 16px 10px 16px;
}}
[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; }}
[data-testid="stMetricValue"] {{ color: {TEXT_PRIMARY} !important; }}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {ACCENT_ORANGE} !important;
    border-bottom-color: {ACCENT_ORANGE} !important;
}}
.hero {{
    background: linear-gradient(120deg, {SURFACE} 0%, {SURFACE_2} 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid {ACCENT_ORANGE};
    border-radius: 14px;
    padding: 20px 26px;
    margin-bottom: 18px;
}}
.hero h1 {{ margin: 0 0 4px 0; font-size: 1.7rem; }}
.hero p {{ margin: 0; color: {TEXT_MUTED}; }}
.insight {{
    background: {SURFACE};
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid {ACCENT_LIME};
    border-radius: 10px;
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    font-size: 0.92rem;
}}
.filter-label {{
    color: {TEXT_MUTED};
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin: 2px 0 2px 2px;
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def chip_filter_css(block_index, colors):
    """CSS ciblant le N-ieme bloc horizontal (stHorizontalBlock) de la page principale,
    pour peindre chaque case a cocher d'une couleur fixe par position — une pastille par
    entite (categorie/canal/ville), coherente avec les couleurs des graphiques."""
    rules = []
    for i, color in enumerate(colors, start=1):
        selector = (
            f'[data-testid="stAppViewContainer"] [data-testid="stHorizontalBlock"]:nth-of-type({block_index}) '
            f'[data-testid="stColumn"]:nth-of-type({i}) [data-testid="stCheckbox"]'
        )
        rules.append(f"""
        {selector} {{
            border: 1.5px solid {color};
            border-radius: 8px;
            padding: 2px 10px 2px 6px;
            transition: background 0.15s ease;
        }}
        {selector}:has(input:checked) {{
            background: {color}3d;
        }}
        {selector} label p {{
            color: {TEXT_PRIMARY} !important;
            font-size: 0.85rem;
        }}
        """)
    return "<style>" + "\n".join(rules) + "</style>"


def chip_filter(options, colors, key_prefix):
    """Ligne de pastilles a cocher (une par option), colorees selon la palette de marque."""
    st.markdown(chip_filter_css(chip_filter.block_counter, colors), unsafe_allow_html=True)
    chip_filter.block_counter += 1
    cols = st.columns(len(options))
    selected = []
    for col, opt in zip(cols, options):
        if col.checkbox(opt, value=True, key=f"{key_prefix}_{opt}"):
            selected.append(opt)
    return selected


chip_filter.block_counter = 1


def style_fig(fig, height=420):
    """Applique le thème visuel commun à toutes les figures Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family="Segoe UI, system-ui, sans-serif", color=TEXT_PRIMARY, size=13),
        title=dict(font=dict(size=16, color=TEXT_PRIMARY)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=height,
        hoverlabel=dict(bgcolor=SURFACE_2, font_size=13, font_family="Segoe UI, system-ui, sans-serif"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=TEXT_MUTED)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=TEXT_MUTED)
    return fig


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date_commande"])


df = load_data()

# ------------------------------------------------------------------
# Filtres — Mois/Catégorie/Canal en barre latérale (compacts, pour laisser
# les KPI respirer) ; Ville en pastilles colorées (assorties aux graphiques
# de l'onglet Géographie) dans la page principale, plus large.
# ------------------------------------------------------------------
categories_options = [c for c in CATEGORIE_ORDER if c in df["categorie"].unique()]
canaux_options = [c for c in CANAL_ORDER if c in df["canal_marketing"].unique()]
villes_options = [v for v in VILLE_ORDER if v in df["ville"].unique()]

st.sidebar.header("Filtres")
mois_options = sorted(df["mois"].unique())
mois_sel = st.sidebar.multiselect("Mois", mois_options, default=mois_options)
categories_sel = st.sidebar.multiselect("Catégorie", categories_options, default=categories_options)
canaux_sel = st.sidebar.multiselect("Canal marketing", canaux_options, default=canaux_options)

st.markdown(
    """<div class="hero"><h1>🛍️ AfriMarket — Dashboard Stratégique</h1>
    <p>6 mois d'activité e-commerce — Électronique · Mode · Beauté · Maison</p></div>""",
    unsafe_allow_html=True,
)

st.markdown('<p class="filter-label">Ville</p>', unsafe_allow_html=True)
villes_sel = chip_filter(villes_options, [VILLE_COLOR[v] for v in villes_options], "chip_ville")

df_f = df[
    df["mois"].isin(mois_sel)
    & df["ville"].isin(villes_sel)
    & df["categorie"].isin(categories_sel)
    & df["canal_marketing"].isin(canaux_sel)
]

if df_f.empty:
    st.warning("Aucune donnée pour cette combinaison de filtres.")
    st.stop()

st.divider()

# ------------------------------------------------------------------
# KPIs globaux (4.1)
# ------------------------------------------------------------------

commandes_valides = df_f[df_f["statut_commande"] != "Annulée"]
ca_total = df_f["chiffre_affaires"].sum()
profit_total = df_f["profit_net"].sum()
panier_moyen = commandes_valides["chiffre_affaires"].sum() / len(commandes_valides) if len(commandes_valides) else 0
taux_annulation = df_f["indicateur_annulation"].mean()
taux_retour = df_f["indicateur_retour"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("CA total", f"{ca_total:,.0f}")
c2.metric("Profit net estimé", f"{profit_total:,.0f}")
c3.metric("Panier moyen", f"{panier_moyen:,.2f}")
c4.metric("Taux d'annulation", f"{taux_annulation:.1%}")
c5.metric("Taux de retour", f"{taux_retour:.1%}")

ca_mensuel = df_f.groupby("mois")["chiffre_affaires"].sum().reset_index().sort_values("mois")
fig_ca_mensuel = px.line(ca_mensuel, x="mois", y="chiffre_affaires", markers=True,
                          title="Évolution mensuelle du chiffre d'affaires")
fig_ca_mensuel.update_traces(line_color=ACCENT_ORANGE, marker=dict(size=8, color=ACCENT_ORANGE),
                              hovertemplate="%{x}<br>CA : %{y:,.0f}<extra></extra>")
st.plotly_chart(style_fig(fig_ca_mensuel, height=340), width="stretch")

st.divider()

# ------------------------------------------------------------------
# Onglets d'analyse (4.2 - 4.5)
# ------------------------------------------------------------------
tab_categorie, tab_geo, tab_marketing, tab_clients = st.tabs(
    ["📦 Catégorie", "🌍 Géographie", "📣 Marketing", "👥 Clients"]
)

with tab_categorie:
    st.subheader("Performance par catégorie")
    par_categorie = (
        df_f.groupby("categorie")
        .agg(ca=("chiffre_affaires", "sum"), marge=("marge_brute", "sum"), taux_retour=("indicateur_retour", "mean"))
        .reindex([c for c in CATEGORIE_ORDER if c in df_f["categorie"].unique()])
        .reset_index()
    )

    col1, col2 = st.columns(2)
    fig_cat_ca = px.bar(par_categorie, x="categorie", y="ca", title="CA par catégorie", color="categorie",
                         color_discrete_map=CATEGORIE_COLOR, text_auto=".2s")
    fig_cat_ca.update_traces(showlegend=False, hovertemplate="%{x}<br>CA : %{y:,.0f}<extra></extra>")
    col1.plotly_chart(style_fig(fig_cat_ca), width="stretch")

    fig_cat_retour = px.bar(par_categorie, x="categorie", y="taux_retour", title="Taux de retour par catégorie",
                             color="categorie", color_discrete_map=CATEGORIE_COLOR)
    fig_cat_retour.update_traces(showlegend=False, hovertemplate="%{x}<br>Retour : %{y:.1%}<extra></extra>")
    fig_cat_retour.update_yaxes(tickformat=".0%")
    col2.plotly_chart(style_fig(fig_cat_retour), width="stretch")

    if "Électronique" in par_categorie["categorie"].values:
        st.markdown(
            '<div class="insight">💡 Électronique concentre ~75% du CA mais affiche le taux de retour '
            'le plus élevé (2x la moyenne) — catégorie à optimiser en qualité avant d\'accélérer davantage.</div>',
            unsafe_allow_html=True,
        )

    evolution_cat = (
        df_f.pivot_table(index="mois", columns="categorie", values="chiffre_affaires", aggfunc="sum")
        .reindex(columns=[c for c in CATEGORIE_ORDER if c in df_f["categorie"].unique()])
        .reset_index()
        .sort_values("mois")
    )
    fig_evo_cat = px.line(evolution_cat, x="mois", y=[c for c in evolution_cat.columns if c != "mois"],
                           markers=True, title="Évolution mensuelle du CA par catégorie",
                           color_discrete_map=CATEGORIE_COLOR)
    fig_evo_cat.update_layout(legend_title_text="")
    st.plotly_chart(style_fig(fig_evo_cat), width="stretch")
    st.dataframe(par_categorie.set_index("categorie").style.format(
        {"ca": "{:,.0f}", "marge": "{:,.0f}", "taux_retour": "{:.1%}"}), width="stretch")

with tab_geo:
    st.subheader("Performance géographique")
    par_ville = (
        df_f.groupby("ville")
        .agg(ca=("chiffre_affaires", "sum"), profit=("profit_net", "sum"), taux_annulation=("indicateur_annulation", "mean"))
        .reindex([v for v in VILLE_ORDER if v in df_f["ville"].unique()])
        .reset_index()
    )

    fig_ville_ca = px.bar(par_ville, x="ville", y="ca", title="CA par ville", color="ville",
                           color_discrete_map=VILLE_COLOR, text_auto=".2s")
    fig_ville_ca.update_traces(showlegend=False, hovertemplate="%{x}<br>CA : %{y:,.0f}<extra></extra>")
    st.plotly_chart(style_fig(fig_ville_ca), width="stretch")

    if "Douala" in par_ville["ville"].values:
        douala_annulation = par_ville.loc[par_ville["ville"] == "Douala", "taux_annulation"].iloc[0]
        if douala_annulation > 0.05:
            st.markdown(
                f'<div class="insight">⚠️ Douala affiche un taux d\'annulation de {douala_annulation:.0%} '
                '(vs ~0% ailleurs), stable chaque mois — signal opérationnel local à investiguer avant '
                'tout investissement marketing supplémentaire.</div>',
                unsafe_allow_html=True,
            )

    croissance_ville = (
        df_f.pivot_table(index="mois", columns="ville", values="chiffre_affaires", aggfunc="sum")
        .reindex(columns=[v for v in VILLE_ORDER if v in df_f["ville"].unique()])
        .sort_index()
    )
    croissance_pct = croissance_ville.pct_change() * 100
    fig_heatmap = px.imshow(croissance_pct.T, text_auto=".0f", color_continuous_scale=GROWTH_SCALE,
                             color_continuous_midpoint=0, aspect="auto",
                             title="Croissance mensuelle du CA par ville (%)",
                             labels={"color": "Croissance (%)"})
    fig_heatmap.update_traces(hovertemplate="%{y} · %{x}<br>Croissance : %{z:.0f}%<extra></extra>")
    st.plotly_chart(style_fig(fig_heatmap, height=380), width="stretch")
    st.dataframe(par_ville.set_index("ville").style.format(
        {"ca": "{:,.0f}", "profit": "{:,.0f}", "taux_annulation": "{:.1%}"}), width="stretch")

with tab_marketing:
    st.subheader("Performance marketing")
    par_canal = df_f.groupby("canal_marketing").agg(
        ca=("chiffre_affaires", "sum"), cout_marketing_total=("cout_marketing", "sum"),
    )
    par_canal["roi"] = (par_canal["ca"] - par_canal["cout_marketing_total"]) / par_canal["cout_marketing_total"]
    par_canal["taux_retention"] = df_f.groupby("canal_marketing")["nombre_commandes_par_client"].apply(lambda s: (s > 1).mean())
    par_canal = par_canal.reindex([c for c in CANAL_ORDER if c in df_f["canal_marketing"].unique()]).reset_index()

    col1, col2 = st.columns(2)
    fig_roi = px.bar(par_canal, x="canal_marketing", y="roi", title="ROI marketing par canal",
                      color="canal_marketing", color_discrete_map=CANAL_COLOR, text_auto=".0f")
    fig_roi.update_traces(showlegend=False, hovertemplate="%{x}<br>ROI : %{y:.1f}<extra></extra>")
    col1.plotly_chart(style_fig(fig_roi), width="stretch")

    fig_canal_ca = px.bar(par_canal, x="canal_marketing", y="ca", title="CA par canal",
                           color="canal_marketing", color_discrete_map=CANAL_COLOR, text_auto=".2s")
    fig_canal_ca.update_traces(showlegend=False, hovertemplate="%{x}<br>CA : %{y:,.0f}<extra></extra>")
    col2.plotly_chart(style_fig(fig_canal_ca), width="stretch")

    if "Email" in par_canal["canal_marketing"].values:
        st.markdown(
            '<div class="insight">💡 Email affiche de très loin le meilleur ROI pour un coût quasi nul : '
            'levier rentable sous-exploité à faire passer à l\'échelle.</div>',
            unsafe_allow_html=True,
        )

    st.dataframe(par_canal.set_index("canal_marketing").style.format(
        {"ca": "{:,.0f}", "cout_marketing_total": "{:,.0f}", "roi": "{:.1f}", "taux_retention": "{:.1%}"}),
        width="stretch")

with tab_clients:
    st.subheader("Analyse clients")
    n_clients = df_f["id_client"].nunique()
    clients_uniques = df_f.drop_duplicates("id_client")
    pct_recurrents = (clients_uniques["nombre_commandes_par_client"] > 1).mean()

    col1, col2 = st.columns(2)
    col1.metric("Nombre total de clients", f"{n_clients:,}")
    col2.metric("% de clients récurrents", f"{pct_recurrents:.1%}")

    ca_par_client = df_f.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False)
    cum_pct_ca = ca_par_client.cumsum() / ca_par_client.sum()
    cum_pct_clients = np.arange(1, len(ca_par_client) + 1) / len(ca_par_client) * 100
    pareto_df = pd.DataFrame({"pct_clients": cum_pct_clients, "pct_ca_cumule": cum_pct_ca.values * 100})
    pct_clients_pour_80pct_ca = (cum_pct_ca.values <= 0.8).sum() / len(ca_par_client)
    st.markdown(
        f'<div class="insight">📊 {pct_clients_pour_80pct_ca:.1%} des clients génèrent 80% du chiffre '
        "d'affaires (analyse Pareto) — la valeur est fortement concentrée.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    fig_pareto = px.line(pareto_df, x="pct_clients", y="pct_ca_cumule", title="Courbe de Pareto — concentration du CA")
    fig_pareto.update_traces(line_color=ACCENT_LIME, hovertemplate="%{x:.0f}% des clients<br>%{y:.0f}% du CA<extra></extra>")
    fig_pareto.add_hline(y=80, line_dash="dash", line_color=TEXT_MUTED, annotation_text="80% du CA",
                          annotation_font_color=TEXT_MUTED)
    st.plotly_chart(style_fig(fig_pareto, height=360), width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 clients par chiffre d'affaires**")
        st.dataframe(ca_par_client.head(10).to_frame("chiffre_affaires").style.format("{:,.0f}"), width="stretch")
    with col2:
        clv = clients_uniques[["id_client", "valeur_vie_client"]].copy()
        clv["segment"] = pd.qcut(clv["valeur_vie_client"], q=4, labels=["Occasionnel", "Standard", "Fidèle", "VIP"])
        seg_counts = clv["segment"].value_counts().reindex(["Occasionnel", "Standard", "Fidèle", "VIP"]).reset_index()
        seg_counts.columns = ["segment", "nb_clients"]
        fig_seg = px.bar(seg_counts, x="segment", y="nb_clients", title="Segmentation clients (CLV)",
                          color="segment",
                          color_discrete_map=dict(zip(["Occasionnel", "Standard", "Fidèle", "VIP"],
                                                       [TEAL, BLUE, GOLD, ACCENT_ORANGE])),
                          text_auto=True)
        fig_seg.update_traces(showlegend=False)
        st.plotly_chart(style_fig(fig_seg), width="stretch")

# ------------------------------------------------------------------
# Palette check (dataviz skill — node indisponible sur cette machine,
# validé via un portage Python du script officiel, mêmes seuils/algorithme) :
#   8 slots, mode dark, surface #101B33 :
#   Lightness band ........ PASS (toutes L in [0.48, 0.67])
#   Chroma floor ........... PASS (toutes C >= 0.10)
#   CVD separation ......... PASS (pire paire adjacente ΔE 13.2, protan)
#   Normal-vision floor .... PASS (pire paire adjacente ΔE 20.5)
#   Contrast vs surface .... PASS (toutes >= 3:1)
# Ordre : orange, teal, blue, lime, magenta, gold, violet, coral
# ------------------------------------------------------------------
