import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore
import os

# CONFIGURATION DE LA PAGE

st.set_page_config(
    page_title="Page principale - PIB",
    page_icon="🌍",
    layout="wide"
)

# CHEMINS DYNAMIQUES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)  # Remonte d’un dossier
DATA_PATH = os.path.join(BASE_DIR, "data_dashboard_BeyondGDP.csv")
IMG_PATH = os.path.join(BASE_DIR, "images")
if not os.path.exists(IMG_PATH):
    IMG_PATH = os.path.join(BASE_DIR, "DataVisualisation", "images")

# IMPORTATION ET NETTOYAGE

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

    # Filtrer uniquement le PIB
    df_gdp = df[df["indicator"] == "GDP per capita (current US$)"].copy()
    df_gdp = df_gdp.dropna(subset=["value"])
    df_gdp["year"] = df_gdp["year"].astype(int)
    return df_gdp

df = load_data()

# =================
# TITRE ET BANNIÈRE
# =================
st.markdown("<h1 style='text-align: center;'>🌍 Beyond GDP : Le PIB ne suffit plus</h1>", unsafe_allow_html=True)
st.image(os.path.join(IMG_PATH, "beyond_gdp_header.png"), use_container_width=True)
st.markdown("---")

# ===================================
# SECTION 1 : "LE PIB, C’EST QUOI ?"
# ===================================
st.markdown("<h2 style='text-align: center;'>💬 Le PIB, c’est quoi ?</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    Le **Produit Intérieur Brut (PIB)** désigne la valeur monétaire totale de l’ensemble des biens et services finaux produits
    à l’intérieur des frontières d’un pays au cours d’une période donnée, généralement une année.  
    Il constitue la mesure la plus couramment utilisée pour évaluer la **performance économique globale** d’une nation.

    Calculé selon trois approches complémentaires — **la production**, **le revenu** et **la dépense** —,
    le PIB synthétise l’activité de tous les agents économiques (ménages, entreprises, administrations publiques)
    en un seul indicateur agrégé.

    Il sert de **référence centrale pour la comparaison internationale** des niveaux de vie,
    la formulation des politiques économiques et l’analyse des cycles de croissance.  
    Son évolution est généralement interprétée comme un signal de l’**expansion** ou du **ralentissement** d’une économie.
    """)

with col2:
    st.image(
        os.path.join(IMG_PATH, "mapGDP.png"),
        caption="Source : Wikipedia - Carte des économies mondiales selon la taille du PIB (nominal, en dollars américains) en 2024",
        use_container_width=True
    )

# ===================================
# SECTION 2 : LIMITES DU PIB ET SOLUTIONS
# ===================================
st.markdown("<h2 style='text-align: center;'>🔍 Au-delà de la mesure économique</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style='text-align: center;'>
    <h3>Les limites du PIB</h3>
    Bien qu’il soit l’un des indicateurs les plus utilisés pour évaluer la performance économique d’un pays,  
    le <strong>PIB ne permet pas de rendre compte de l’ensemble des dimensions du développement</strong>.  
    En se concentrant exclusivement sur la production marchande, il ignore les contributions non marchandes,
    le bien-être social ou encore la durabilité environnementale.  
    De plus, sa croissance peut coexister avec des inégalités fortes ou une dégradation du capital naturel,
    ce qui interroge sa capacité à refléter le progrès réel d’une société.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center;'>
    <h3>Les solutions étudiées</h3>
    Conscientes de ces limites, les <strong>Nations Unies</strong> et plusieurs institutions internationales
    (notamment la <strong>CNUCED</strong>, l’<strong>OCDE</strong> et le <strong>PNUD</strong>) ont initié des travaux visant à <strong>compléter le PIB</strong>
    par des indicateurs plus représentatifs du développement humain et durable.  
    Parmi eux figurent :
    - Le <strong>Indice de Développement Humain (IDH)</strong>, centré sur la santé, l’éducation et le niveau de vie.  
    - Les <strong>indicateurs environnementaux</strong> (émissions de CO₂, empreinte écologique, énergie renouvelable).  
    - Les <strong>indicateurs sociaux et d’inégalités</strong> (indice de Gini, pauvreté multidimensionnelle).  
    Ces approches constituent le socle de la réflexion contemporaine dite <em>“Beyond GDP”</em>, 
    qui vise à <strong>repenser la manière de mesurer le progrès</strong> à l’échelle mondiale.
    </div>
    """, unsafe_allow_html=True)

# ===================================
# IMAGE Objectifs de Developpement Durable 
# ===================================
st.markdown("---")
st.image(
    os.path.join(IMG_PATH, "ODD.jpg"),
    use_container_width=True,
    caption="Les 17 Objectifs de Développement Durable (ONU)"
)

# ===================================
# SECTION 3 : CARTE MONDIALE DU PIB PAR HABITANT
# ===================================
st.markdown("---")
st.subheader("🌐 Carte mondiale du PIB par habitant")

years = sorted(df["year"].unique())
year_selected = st.slider("Choisir une année :", int(min(years)), int(max(years)), 2020)

df_year = df[df["year"] == year_selected]

fig_map = px.choropleth(
    df_year,
    locations="country",
    locationmode="country names",
    color="value",
    hover_name="country",
    color_continuous_scale="Plasma",  
    title=f"PIB par habitant (USD courants) en {year_selected}",
    projection="natural earth"
)
st.plotly_chart(fig_map, use_container_width=True)

# ===================================
# SECTION 4 : ÉVOLUTION TEMPORELLE DU PIB
# ===================================
st.markdown("---")
st.subheader("📈 Évolution temporelle du PIB par habitant")

countries = sorted(df["country"].unique())
selected_countries = st.multiselect(
    "Sélectionner un ou plusieurs pays :",
    countries,
    default=["France", "United States", "China"]
)

df_sel = df[df["country"].isin(selected_countries)]

fig_line = px.line(
    df_sel,
    x="year",
    y="value",
    color="country",
    labels={"value": "PIB par habitant (USD courants)", "year": "Année"},
    title="Évolution du PIB par habitant dans le temps"
)
st.plotly_chart(fig_line, use_container_width=True)

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
