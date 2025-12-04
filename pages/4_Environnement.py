import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore
import os
import numpy as np

# CONFIGURATION

st.set_page_config(page_title="Environnement - Beyond GDP", page_icon="🌱", layout="wide")

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
    "EN.GHG.CO2.PC.CE.AR5": "CO₂ emissions per capita (t/person, AR5)",
    "EG.FEC.RNEW.ZS": "Renewable energy consumption (% of total final energy)",
    "EN.ATM.PM25.MC.M3": "PM2.5 air pollution (µg/m³)"
}

df_env = df[df["indicator"].isin(indicators.values())]

# ================
# TITRE AVEC IMAGE
# ================

# Convertit l'image en base64
import base64

image_path = os.path.join(IMG_PATH, "RubanEnv.png")

with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin-top: 20px;
        margin-bottom: 10px;
        flex-wrap: wrap;
        text-align: center;
    ">
        <img src="data:image/png;base64,{img_base64}" style="height:55px;">
        <h1 style="margin:0; padding:0; flex: 1 1 100%; text-align: center;">
            Le PIB face aux indicateurs d'environnement
        </h1>
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
    st.markdown("<h4 style='text-align: center;'>émissions de CO₂ par habitant (t/personne, AR5)</h4>", unsafe_allow_html=True)
    st.markdown("Correspondent à la quantité moyenne de dioxyde de carbone rejetée chaque année par un individu, en tenant compte des émissions produites par l’activité économique et énergétique d’un pays. Exprimé en tonnes par personne, cet indicateur permet de mesurer l’empreinte carbone moyenne de la population et d’évaluer la pression exercée sur le climat.")

with col2:
    st.markdown("<h4 style='text-align: center;'>Part des énergies renouvelables (% consommation finale)</h4>", unsafe_allow_html=True)
    st.markdown("Indique la proportion de la consommation finale d’énergie provenant de sources renouvelables, telles que le solaire, l’éolien, l’hydraulique ou la biomasse. Exprimé en pourcentage, cet indicateur reflète la transition énergétique d’un pays et sa capacité à réduire sa dépendance aux combustibles fossiles.")

with col3:
    st.markdown("<h4 style='text-align: center;'>Pollution de l’air PM2.5 (µg/m³)</h4>", unsafe_allow_html=True)
    st.markdown("Mesure la concentration de particules fines de diamètre inférieur à 2,5 micromètres présentes dans l’air. Exprimé en microgrammes par mètre cube, cet indicateur renseigne sur la qualité de l’air et sur les risques pour la santé humaine. Des niveaux élevés de PM2.5 sont associés à des maladies respiratoires, cardiovasculaires et à une mortalité accrue.")

st.markdown("---")

# ===============================
# IMPORTANCE DE LA CONFRONTATION
# ===============================
st.markdown("<h3 style='text-align: center;'>Pourquoi confronter le PIB à ces indicateurs environnementaux ?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Le PIB mesure la quantité de richesse produite, mais il ne dit rien sur son coût pour l’environnement ni sur sa soutenabilité. Un pays peut avoir une croissance élevée tout en détruisant ses ressources, en émettant trop de CO₂ ou en exposant sa population à une pollution dangereuse. Les émissions de CO₂, la part d’énergies renouvelables et la pollution de l’air révèlent la qualité énergétique d’un pays, son impact sur le climat et les risques qu’il fait peser sur la santé. Confronter ces indicateurs au PIB permet donc de savoir si la croissance repose sur un modèle durable — ou si elle se construit au détriment du climat, de la qualité de vie et, à terme, de la stabilité économique elle-même.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# GRAPHIQUE D'ÉVOLUTION COMPARATIVE (NORMALISÉE)
# ===============================
st.markdown("<h3 style='text-align: center;'>Évolution comparée du PIB et des indicateurs environnementaux</h3>", unsafe_allow_html=True)

countries = sorted(df_env["country"].unique())
selected_country = st.selectbox(
    "Sélectionner un pays :",
    countries,
    index=countries.index("France") if "France" in countries else 0
)

df_sel = df_env[df_env["country"] == selected_country].copy()

# Normalisation min-max
df_sel["value_norm"] = df_sel.groupby("indicator")["value"].transform(
    lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0
)

# Courbes normalisées
fig_line = px.line(
    df_sel,
    x="year",
    y="value_norm",
    color="indicator",
    labels={"value_norm": "Valeur normalisée (0–1)", "year": "Année"}
)

color_map = {
    "GDP per capita (current US$)": "red",
    "EN.GHG.CO2.PC.CE.AR5": "CO₂ emissions per capita (t/person, AR5)",
    "Renewable energy consumption (% of total final energy)": "seagreen",
    "PM2.5 air pollution (µg/m³)": "orange"
}
for trace in fig_line.data:
    trace.line.color = color_map.get(trace.name, None)

# Mise en forme du graphique
fig_line.update_layout(
    title=dict(
        text=f"Évolution temporelle normalisée des indicateurs éducatifs – {selected_country}",
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
# DOUBLE VISUEL : MATRICE + SCATTER BUBBLE CHART
# ===============================
st.markdown("<h3 style='text-align: center;'>Relations entre environnement et économie</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Colonne gauche : Matrice de corrélation
with col1:

    st.markdown("<h4 style='text-align: center;'>Matrice de corrélation</h4>", unsafe_allow_html=True)

    # Renommage
    rename_dict = {
        "GDP per capita (current US$)": "PIB",
        "CO₂ emissions per capita (t/person, AR5)": "Émissions CO₂",
        "Renewable energy consumption (% of total final energy)": "Énergie renouvelable",
        "PM2.5 air pollution (µg/m³)": "Pollution PM2.5"
    }

    # Préparation matrice
    pivot = df_sel.pivot(index="year", columns="indicator", values="value")
    corr = pivot.corr().round(2)

    # Renommer lignes/colonnes
    corr = corr.rename(index=rename_dict, columns=rename_dict)

    # Réordonner : PIB toujours en premier
    new_order = ["PIB", "Émissions CO₂", "Énergie renouvelable", "Pollution PM2.5"]
    corr = corr.loc[new_order, new_order]

    # Triangle inférieur
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

    # Mise en forme uniforme
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

# Colonne droite : scatter-bubble chart
with col2:
    st.markdown("<h4 style='text-align: center;'>scatter-bubble chart International</h4>",
                unsafe_allow_html=True)

    # Sélecteur de pays
    selected_countries_env = st.multiselect(
        "Comparer jusqu'à 3 pays :",
        countries,
        default=["France", "Germany", "United States"],
        max_selections=3
    )

    # Sélecteur d’indicateur environnemental
    indicator_choice = st.selectbox(
        "Choisir un indicateur environnemental :",
        [
            "CO₂ emissions per capita (t/person, AR5)",
            "Renewable energy consumption (% of total final energy)",
            "PM2.5 air pollution (µg/m³)"
        ]
    )

    # Filtrer les données
    df_env_year = df_env[
        (df_env["country"].isin(selected_countries_env)) &
        (df_env["indicator"].isin([
            "GDP per capita (current US$)",
            indicator_choice
        ]))
    ].copy()

    # Dernière année disponible
    last_year = int(df_env_year["year"].max())
    df_env_year = df_env_year[df_env_year["year"] == last_year]

    # Pivot (forme large)
    pivot_env = df_env_year.pivot(
        index="country",
        columns="indicator",
        values="value"
    ).reset_index()

    # Renommer pour lisibilité
    pivot_env.rename(columns={
        "GDP per capita (current US$)": "PIB par habitant",
    }, inplace=True)

    # Graphique interactif scatter
    fig_env = px.scatter(
        pivot_env,
        x="PIB par habitant",
        y=indicator_choice,
        color="country",
        size=indicator_choice,  # taille des bulles selon l'indicateur
        hover_name="country",
        labels={
            "PIB par habitant": "PIB par habitant (USD)",
            indicator_choice: indicator_choice,
            "country": "Pays"
        },
        title=f"PIB & {indicator_choice} — {last_year}",
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    # Mise en forme propre
    fig_env.update_layout(
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        xaxis_title="PIB par habitant (USD)",
        yaxis_title=indicator_choice,
        margin=dict(t=70, b=40)
    )

    st.plotly_chart(fig_env, use_container_width=True)

# ==========
# CONCLUSION
# ==========
st.markdown("<h3 style='text-align: center;'>Ce que révèle l’analyse environnementale</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; max-width: 900px; margin: auto;'>

    <p>
    L’analyse croisée du PIB et des indicateurs environnementaux met en lumière une réalité essentielle :
    <strong>la croissance économique ne peut être considérée durable que si elle préserve les ressources naturelles,
    limite les émissions polluantes et protège la santé des populations</strong>. 
    Un pays peut enregistrer une progression soutenue de son PIB, mais si cette croissance s’accompagne
    d’une intensification du CO₂, d’une dépendance persistante aux énergies fossiles ou d’une dégradation 
    de la qualité de l’air, son modèle de développement devient fragilisé.
    </p><br>

    <p>
    Les émissions de CO₂, la part d’énergies renouvelables et la pollution atmosphérique sont autant de signaux
    qui renseignent sur la trajectoire écologique d’un pays. 
    <strong>Une réduction des émissions, une montée en puissance du renouvelable et une amélioration
    de la qualité de l’air témoignent d’une transition réussie, plus résiliente et alignée sur les objectifs 
    climatiques internationaux.</strong> 
    À l’inverse, une stagnation ou une détérioration de ces indicateurs suggèrent que la croissance repose encore
    sur un modèle coûteux pour le climat et la santé publique.
    </p><br>

    <p>
    Ces données rappellent une idée fondamentale : <strong>l’environnement n’est pas une contrainte économique,
    mais un pilier du développement durable</strong>. 
    La préservation de l’air, de l’énergie et du climat conditionne la stabilité à long terme, la sécurité
    énergétique, la productivité et le bien-être des populations.
    </p><br>

    <p>
    Confronter le PIB aux indicateurs environnementaux permet donc d’évaluer non seulement 
    la richesse produite, mais aussi <strong>son coût écologique et sa soutenabilité dans le temps</strong>.
    Un modèle économique réellement durable est celui qui parvient à concilier croissance,
    réduction de l’empreinte carbone et transition énergétique. 
    C’est la condition pour garantir une prospérité compatible avec les limites planétaires.
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
