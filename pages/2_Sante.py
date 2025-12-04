import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore
import os
import numpy as np

# CONFIGURATION

st.set_page_config(page_title="Santé - Beyond GDP", page_icon="💉", layout="wide")

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
    "SP.DYN.LE00.IN": "Life expectancy at birth (years)",
    "SH.XPD.CHEX.GD.ZS": "Current health expenditure (% of GDP)",
    "SH.DYN.MORT": "Mortality rate, under-5 (per 1,000 live births)"
}

df_health = df[df["indicator"].isin(indicators.values())]

# ================
# TITRE AVEC IMAGE
# ================

# Convertit l'image en base64
import base64

image_path = os.path.join(IMG_PATH, "RubanSante.png")

with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-top:20px; margin-bottom:10px;">
        <img src="data:image/png;base64,{img_base64}" style="height:55px;">
        <h1 style="margin:0; padding:0;">Le PIB face aux indicateurs de santé</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ===========================
# DÉFINITIONS DES INDICATEURS
# ===========================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<h4 style='text-align: center;'>Espérance de vie à la naissance (années)</h4>", unsafe_allow_html=True)
    st.markdown("Représente le nombre moyen d’années qu’un nouveau-né peut espérer vivre, compte tenu des conditions de mortalité observées au moment de sa naissance. Cet indicateur reflète l’état général de santé d’une population, ainsi que la qualité de son système sanitaire, social et environnemental.")

with col2:
    st.markdown("<h4 style='text-align: center;'>Dépenses courantes de santé (% du PIB)</h4>", unsafe_allow_html=True)
    st.markdown("Regroupent l’ensemble des ressources consacrées chaque année aux services médicaux, aux médicaments, à la prévention et au fonctionnement du système de santé. Exprimées en pourcentage du PIB, elles indiquent la part de la richesse nationale dédiée au financement de la santé et reflètent l’effort d’un pays pour assurer l’accès aux soins et améliorer le bien-être de sa population.")

with col3:
    st.markdown("<h4 style='text-align: center;'>Taux de mortalité des enfants de moins de 5 ans</h4>", unsafe_allow_html=True)
    st.markdown("Mesure le nombre de décès pour 1 000 naissances vivantes avant l’âge de cinq ans. Il reflète les conditions de vie, l’accès aux soins, la qualité de la nutrition et l’efficacité des systèmes de santé. Un taux faible est un indicateur majeur du développement humain et du bien-être des populations.")

st.markdown("---")

# ===============================
# IMPORTANCE DE LA CONFRONTATION
# ===============================
st.markdown("<h3 style='text-align: center;'>Pourquoi confronter le PIB à ces indicateurs de santé ?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Le PIB mesure la valeur de ce qu’un pays produit, mais il ne suffit plus à expliquer la réalité économique d’une société moderne.Une économie n’est solide que si sa population est en bonne santé, vit longtemps et a accès à des soins efficaces. Des dépenses de santé insuffisantes, une espérance de vie faible ou une mortalité infantile élevée affaiblissent directement la productivité, le capital humain et la capacité d’un pays à se développer. Confronter ces indicateurs de santé au PIB permet donc de comprendre si la richesse créée repose sur une population réellement capable de travailler, d’innover et de vivre dans de bonnes conditions, ou si l’économie s’appuie sur des fondations fragiles.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# GRAPHIQUE D'ÉVOLUTION COMPARATIVE (NORMALISÉ)
# ===============================
st.markdown("<h3 style='text-align: center;'>Évolution comparée du PIB et des indicateurs de santé</h3>", unsafe_allow_html=True)

countries = sorted(df_health["country"].unique())
selected_country = st.selectbox(
    "Sélectionner un pays :",
    countries,
    index=countries.index("France") if "France" in countries else 0
)

df_sel = df_health[df_health["country"] == selected_country].copy()

# Normalisation min-max
df_sel["value_norm"] = df_sel.groupby("indicator")["value"].transform(
    lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0
)

# Graphique normalisé
fig_line = px.line(
    df_sel,
    x="year",
    y="value_norm",
    color="indicator",
    labels={"value_norm": "Valeur normalisée (0–1)", "year": "Année", "indicator": "Indicateur"}
)

color_map = {
    "GDP per capita (current US$)": "red",
    "Life expectancy at birth (years)": "green",
    "Current health expenditure (% of GDP)": "steelblue",
    "Mortality rate, under-5 (per 1,000 live births)": "orange"
}
for trace in fig_line.data:
    trace.line.color = color_map.get(trace.name, None)

# Mise en forme du graphique
fig_line.update_layout(
    title=dict(
        text=f"Évolution temporelle normalisée des indicateurs économiques – {selected_country}",
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
# DOUBLE VISUEL : MATRICE + SCATTER
# ===============================
st.markdown("<h3 style='text-align: center;'>Relations entre santé et performance économique</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Colonne gauche : Matrice de corrélation
with col1:

    st.markdown("<h4 style='text-align: center;'>Matrice de corrélation</h4>", unsafe_allow_html=True)

    # Renommage
    rename_dict = {
        "GDP per capita (current US$)": "PIB",
        "Life expectancy at birth (years)": "Espérance de vie",
        "Current health expenditure (% of GDP)": "Dépenses de santé",
        "Mortality rate, under-5 (per 1,000 live births)": "Mortalité <5 ans"
    }

    # Préparation matrice
    pivot = df_sel.pivot(index="year", columns="indicator", values="value")
    corr = pivot.corr().round(2)

    # Renommage
    corr = corr.rename(index=rename_dict, columns=rename_dict)

    # Réordonner pour mettre PIB en premier
    new_order = ["PIB", "Espérance de vie", "Dépenses de santé", "Mortalité <5 ans"]
    corr = corr.loc[new_order, new_order]

    # Garder uniquement le triangle inférieur
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

    # Mise en forme unifiée
    fig.update_layout(
        title=dict(
            text=f"{selected_country}",
            x=0.5,
            xanchor="center",
            font=dict(size=18)
        ),

        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(corr.columns))),
            ticktext=corr.columns,
            tickangle=45,
            side="top",
            title=None,
            automargin=True
        ),

        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(corr.index))),
            ticktext=corr.index,
            title=None
        ),

        margin=dict(l=20, r=20, t=110, b=20),
        coloraxis_showscale=True
    )

    st.plotly_chart(fig, use_container_width=True)

# Colonne droite : Scatter plot 3 dimensions 
with col2:

    st.markdown("<h4 style='text-align: center;'>Scatter plot International</h4>", unsafe_allow_html=True)

    # Sélection de plusieurs pays
    selected_countries_health = st.multiselect(
        "Comparer plusieurs pays :",
        countries,
        default=["France", "Japan", "United States"],
        max_selections=6
    )

    df_health = df_health[df_health["country"].isin(selected_countries_health)].copy()

    # Filtrer la dernière année disponible
    last_year = int(df_health["year"].max())
    df_health = df_health[df_health["year"] == last_year]

    # Pivot avec seulement les indicateurs utiles
    pivot_health = df_health.pivot(
        index="country",
        columns="indicator",
        values="value"
    ).reset_index()

    # Renommage propre
    pivot_health = pivot_health.rename(columns={
        "GDP per capita (current US$)": "PIB par hab.",
        "Life expectancy at birth (years)": "Espérance de vie",
        "Mortality rate, under-5 (per 1,000 live births)": "Mortalité <5 ans"
    })

    # Supprimer les lignes incomplètes (rare, mais sécurité)
    pivot_health = pivot_health.dropna(subset=["PIB par hab.", "Espérance de vie", "Mortalité <5 ans"])

    # Scatter robuste : PIB vs Espérance de vie
    fig_scatter = px.scatter(
        pivot_health,
        x="PIB par hab.",
        y="Espérance de vie",
        color="Mortalité <5 ans",
        hover_name="country",
        title=f"Comparaison internationale — {last_year}",
        color_continuous_scale="Viridis",
        labels={
            "PIB par hab.": "PIB par habitant (USD)",
            "Espérance de vie": "Espérance de vie (années)",
            "Mortalité <5 ans": "Mortalité des moins de 5 ans (‰)"
        }
    )

    fig_scatter.update_layout(
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        margin=dict(t=70, b=40)
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

# ==========
# CONCLUSION
# ==========
st.markdown("<h3 style='text-align: center;'>Ce que révèle l’analyse sanitaire</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; max-width: 900px; margin: auto;'>
    
    <p>
    La comparaison du PIB avec les indicateurs de santé montre une réalité incontournable :
    <strong>la performance économique d’un pays n’a de sens que si elle se traduit par de meilleures conditions de vie pour sa population.</strong>
    </p><br>

    <p>
    Là où l’espérance de vie progresse et où la mortalité infantile diminue, on observe généralement un investissement public soutenu
    et une gouvernance sanitaire solide. À l’inverse, des dépenses de santé insuffisantes freinent directement le développement humain,
    même lorsque le PIB par habitant est élevé.
    </p><br>

    <p>
    L’analyse met ainsi en évidence un point crucial :
    <strong>la santé n’est pas une conséquence automatique de la croissance, mais un pilier essentiel qui la conditionne.</strong>
    Une population en bonne santé est plus productive, plus résiliente et mieux à même de bénéficier des opportunités économiques.
    </p><br>

    <p>
    Confronter le PIB à ces indicateurs permet de mesurer non seulement la richesse créée, mais surtout
    <strong>la qualité de vie qu’un pays parvient réellement à garantir à ses citoyens.</strong>
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
