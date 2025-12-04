import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore
import os
import numpy as np

# CONFIGURATION

st.set_page_config(page_title="Économie - Beyond GDP", page_icon="💰", layout="wide")

# CHEMINS D’ACCÈS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data_dashboard_BeyondGDP.csv")
IMG_PATH = os.path.join(BASE_DIR, "images")

# CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Country Name": "country",
        "Indicator Name": "indicator",
        "Year": "year",
        "Value": "value"
    })
    df = df.dropna(subset=["value"])
    df["year"] = df["year"].astype(int)
    return df

df = load_data()

# ========================
# INDICATEURS SÉLECTIONNÉS
# ========================
indicators = {
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "NE.GDI.TOTL.ZS": "Gross capital formation (% of GDP)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)"
}

df_econ = df[df["indicator"].isin(indicators.values())]

# ================
# TITRE AVEC IMAGE
# ================

# Convertit l'image en base64
import base64

image_path = os.path.join(IMG_PATH, "RubanEconomie.png")

with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-top:20px; margin-bottom:10px;">
        <img src="data:image/png;base64,{img_base64}" style="height:55px;">
        <h1 style="margin:0; padding:0;">Le PIB face aux indicateurs d'économie</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ===========================
# DÉFINITIONS DES INDICATEURS
# ===========================
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='text-align: center;'>Formation brute de capital (% du PIB)</h3>", unsafe_allow_html=True)
    st.markdown("Mesure l'ensemble des investissements réalisés dans un pays pour développer ou renouveler ses infrastructures, ses équipements et ses capacités de production. Exprimée en pourcentage du PIB, elle indique la part de la richesse nationale consacrée à l'investissement productif. Un niveau élevé reflète généralement un effort d'investissement important, favorisant la croissance future et le développement économique.")

with col2:
    st.markdown("<h3 style='text-align: center;'>Inflation (variation annuelle des prix à la consommation)</h3>", unsafe_allow_html=True)
    st.markdown("Correspond à l'augmentation moyenne des prix des biens et services consommés par les ménages sur une année. Exprimée en taux annuel, elle mesure la perte de pouvoir d'achat de la monnaie. Un niveau d'inflation modéré accompagne généralement une économie dynamique, tandis qu'une inflation trop élevée ou trop faible peut signaler des déséquilibres économiques.")

st.markdown("---")

# ===============================
# IMPORTANCE DE LA CONFRONTATION
# ===============================
st.markdown("<h3 style='text-align: center;'>Pourquoi confronter le PIB à ces deux indicateurs ?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Le PIB mesure ce q'un pays produit, mais il ne dit rien sur la façon dont il prépare son avenir, ni sur la stabilité des prix auxquels vivent ses habitants. La formation brute de capital montre la capacité d'un pays à investir pour se développer demain, tandis que l'inflation révèle si les ménages peuvent réellement profiter de cette richesse. Un PIB élevé peut donc cacher une économie qui n'investit pas assez ou un pouvoir d'achat qui s'effondre. C'est en confrontant le PIB à ces deux indicateurs qu'on comprend si la croissance est solide, durable et réellement bénéfique pour la population.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# GRAPHIQUE D'ÉVOLUTION COMPARATIVE (NORMALISÉ)
# ===============================
st.markdown("<h3 style='text-align: center;'>Évolution comparée du PIB, de l'inflation et de l'investissement</h3>", unsafe_allow_html=True)

countries = sorted(df_econ["country"].unique())
selected_country = st.selectbox(
    "Sélectionner un pays :",
    countries,
    index=countries.index("France") if "France" in countries else 0
)

# Filtrer les données du pays sélectionné
df_sel = df_econ[df_econ["country"] == selected_country].copy()

# Normalisation min-max pour rendre les échelles comparables
df_sel["value_norm"] = df_sel.groupby("indicator")["value"].transform(
    lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0
)

# Graphique normalisé
fig_line = px.line(
    df_sel,
    x="year",
    y="value_norm",
    color="indicator",
    labels={
        "value_norm": "Valeur normalisée (0-1)",
        "year": "Année",
        "indicator": "Indicateur"
    }
)

# Palette personnalisée
color_map = {
    "GDP per capita (current US$)": "red",
    "Gross capital formation (% of GDP)": "steelblue",
    "Inflation, consumer prices (annual %)": "orange"
}
for trace in fig_line.data:
    trace.line.color = color_map.get(trace.name, None)

# Mise en forme du graphique
fig_line.update_layout(
    title=dict(
        text=f"Évolution temporelle normalisée des indicateurs économiques - {selected_country}",
        x=0.5,
        xanchor="center",
        xref="paper",
        font=dict(size=16)
    ),
    legend_title_text="",
    margin=dict(t=80, b=30)
)

st.plotly_chart(fig_line, use_container_width=True)
st.markdown("---")

# ===============================
# DOUBLE VISUEL : MATRICE + STACKED BAR CHART
# ===============================
st.markdown("<h3 style='text-align: center;'>Relations entre les indicateurs économiques</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Colonne gauche : Matrice de corrélation
with col1:

    st.markdown("<h4 style='text-align: center;'>Matrice de corrélation</h4>", unsafe_allow_html=True)

    # Mapping des noms simplifiés
    rename_dict = {
        "GDP per capita (current US$)": "PIB",
        "Gross capital formation (% of GDP)": "Formation brute de capital",
        "Inflation, consumer prices (annual %)": "Inflation"
    }

    # Préparation matrice
    pivot = df_sel.pivot(index="year", columns="indicator", values="value")
    corr = pivot.corr().round(2)

    # Renommage des colonnes et lignes
    corr = corr.rename(index=rename_dict, columns=rename_dict)

    # Garder le triangle inférieur
    mask = np.tril(np.ones_like(corr, dtype=bool))
    corr_tri = corr.where(mask)

    # Heatmap
    fig = px.imshow(
        corr_tri,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto"
    )

    # Mise en forme
    fig.update_layout(
        title=dict(
        text=f"{selected_country}",
        x=0.5,
        xanchor="center",
        font=dict(size=18)
    ),

    # Supprimer complètement les labels "indicator"
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(len(corr.columns))),
        ticktext=corr.columns,
        tickangle=45,
        side="top",
        title=None,          # ← supprime "indicator"
        automargin=True
    ),
    yaxis=dict(
        tickmode="array",
        tickvals=list(range(len(corr.index))),
        ticktext=corr.index,
        title=None           # ← supprime "indicator"
    ),

    margin=dict(l=20, r=20, t=110, b=20),   # ↑ titre plus haut
    coloraxis_showscale=True
)
    st.plotly_chart(fig, use_container_width=True)

# Colonne droite : Comparatif PIB / Investissement
with col2:
    st.markdown("<h4 style='text-align: center;'>Stacked Bar Chart International</h4>", unsafe_allow_html=True)

    # Sélection de plusieurs pays à comparer
    selected_countries_bar = st.multiselect(
        "Comparer jusqu'à 3 pays :",
        countries,
        default=["France", "United States", "China"],
        max_selections=3
    )

    df_bar = df_econ[df_econ["country"].isin(selected_countries_bar)].copy()
    df_bar = df_bar[df_bar["indicator"].isin([
        "GDP per capita (current US$)",
        "Gross capital formation (% of GDP)"
    ])]

    # Filtrer la dernière année disponible
    last_year = int(df_bar["year"].max())
    df_bar = df_bar[df_bar["year"] == last_year]

    # Pivot pour faciliter la lecture
    pivot_bar = df_bar.pivot(index="country", columns="indicator", values="value").reset_index()

    # Calcul du montant investi par habitant (USD)
    pivot_bar["Investment (USD per capita)"] = (
        pivot_bar["GDP per capita (current US$)"] *
        pivot_bar["Gross capital formation (% of GDP)"] / 100
    )

    # Calcul du reste du PIB (non investi)
    pivot_bar["Remaining GDP (USD per capita)"] = (
        pivot_bar["GDP per capita (current US$)"] - pivot_bar["Investment (USD per capita)"]
    )

    # Préparer les données au format long
    df_long = pivot_bar.melt(
        id_vars="country",
        value_vars=["Investment (USD per capita)", "Remaining GDP (USD per capita)"],
        var_name="Component",
        value_name="Value"
    )

    # Graphique en barres empilées
    fig_bar = px.bar(
        df_long,
        x="country",
        y="Value",
        color="Component",
        barmode="stack",
        title=f"Structure du PIB et part investie - {last_year}",
        labels={"Value": "PIB par habitant (USD)", "country": "Pays"},
        color_discrete_map={
            "Investment (USD per capita)": "steelblue",
            "Remaining GDP (USD per capita)": "lightgray"
        }
    )

    # Amélioration visuelle
    fig_bar.update_layout(
        title=dict(
            x=0.5,
            xanchor="center",
            xref="paper",
            font=dict(size=14)
        ),
        legend_title_text="Composantes du PIB",
        yaxis_title="PIB par habitant (USD)",
        xaxis_title="",
        margin=dict(t=70, b=40)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ==========
# CONCLUSION
# ==========
st.markdown("<h3 style='text-align: center;'>Ce que révèle l'analyse économique</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; max-width: 900px; margin: auto;'>
    
    <p>
    L’observation croisée du PIB, de l’inflation et de l’investissement rappelle une évidence trop souvent négligée :
    la croissance ne dit rien, à elle seule, de la solidité d’une économie. Deux pays peuvent afficher un PIB similaire
    tout en suivant des trajectoires radicalement différentes selon leur capacité à investir, maîtriser leurs prix ou
    préparer leur avenir productif.
    </p><br>

    <p>
    Il est évident que ces indicateurs ne progressent pas toujours en synchronisation. Un PIB en progression peut masquer
    un effort d’investissement insuffisant, tandis qu’une inflation mal contenue peut effacer les gains économiques
    apparents. Ces divergences révèlent la nature profondément structurelle des dynamiques économiques : elles dépendent
    des choix politiques, des institutions et des vulnérabilités propres à chaque pays.
    </p><br>

    <p>
    C’est pourquoi il est indispensable de dépasser une lecture centrée sur la seule production de richesse.
    Le PIB indique ce qu’un pays crée. L’investissement montre ce qu’il prépare.
    L’inflation révèle ce que sa population peut réellement en tirer.
    </p><br>

    <p>
    Regarder ces indicateurs ensemble, c’est comprendre non pas seulement la croissance, mais la soutenabilité,
    la stabilité et la qualité réelle du développement. Une lecture indispensable pour appréhender le monde
    économique contemporain.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)

# Bannière bas de page

st.markdown(
    """
    <div style="
        width: 100%;
        background-color: #009EDB;
        padding: 22px 0;
        margin-top: 50px;
        text-align: center;
        color: white;
        font-size: 15px;
        font-weight: 500;
    ">
        Analyse réalisée dans une démarche pédagogique inspirée des travaux de l’UNCTAD —
        <a href="https://unctad.org" target="_blank" style="color: white; text-decoration: underline;">
            www.unctad.org
        </a>
        <br>
        <span style="font-size: 14px; font-weight: 400;">
            Contact — clarapierreuse@outlook.fr
        </span>
    </div>
    """,
    unsafe_allow_html=True
)





