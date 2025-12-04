import streamlit as st  # type: ignore
import pandas as pd
import plotly.express as px  # type: ignore
import os
import numpy as np

# CONFIGURATION

st.set_page_config(page_title="Société - Beyond GDP", page_icon="🌍", layout="wide")

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
    "SP.URB.TOTL.IN.ZS": "Urban population (% of total population)",
    "SH.H2O.BASW.ZS": "Access to basic drinking water (% of population)"
}

df_soc = df[df["indicator"].isin(indicators.values())]

# ================
# TITRE AVEC IMAGE
# ================

# Convertit l'image en base64
import base64

image_path = os.path.join(IMG_PATH, "RubanSociete.png")

with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-top:20px; margin-bottom:10px;">
        <img src="data:image/png;base64,{img_base64}" style="height:55px;">
        <h1 style="margin:0; padding:0;">Le PIB face aux indicateurs de société</h1>
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
    st.markdown("<h4 style='text-align: center;'>Population urbaine (% total)</h4>", unsafe_allow_html=True)
    st.markdown("Correspond à la part des habitants vivant dans des zones classées comme urbaines selon les critères nationaux. Exprimé en pourcentage du total de la population, cet indicateur renseigne sur le degré d’urbanisation d’un pays et sur les dynamiques démographiques liées au développement économique.")

with col2:
    st.markdown("<h4 style='text-align: center;'>Accès à l'eau potable</h4>", unsafe_allow_html=True)
    st.markdown("Mesure la proportion de la population ayant accès à une source d’eau sûre et améliorée répondant aux standards internationaux. Exprimé en pourcentage, cet indicateur reflète les conditions sanitaires, la qualité des infrastructures et le niveau général de bien-être des populations.")

st.markdown("---")

# ===============================
# IMPORTANCE DE LA CONFRONTATION
# ===============================
st.markdown("<h3 style='text-align: center;'>Pourquoi confronter le PIB aux indicateurs sociétaux ?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Le PIB mesure la richesse produite par un pays, mais il ne dit rien sur les conditions de vie réelles de sa population ni sur la qualité de ses infrastructures. Or, une économie ne peut fonctionner efficacement que si les habitants disposent d’un environnement sûr, urbanisé et doté de services essentiels. La part de population vivant en zone urbaine renseigne sur l’accès aux emplois, aux transports et aux opportunités économiques, tandis que l’accès à l’eau potable révèle le niveau d’infrastructures, de santé publique et de bien-être. Confronter ces indicateurs sociétaux au PIB permet donc d’évaluer si la richesse produite s’accompagne d’un développement humain et territorial équilibré, ou si la croissance masque des conditions de vie encore fragiles.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# GRAPHIQUE D'ÉVOLUTION COMPARATIVE (NORMALISÉE)
# ===============================
st.markdown("<h3 style='text-align: center;'>Évolution comparée du PIB et des indicateurs sociétaux</h3>", unsafe_allow_html=True)

countries = sorted(df_soc["country"].unique())
selected_country = st.selectbox(
    "Sélectionner un pays :",
    countries,
    index=countries.index("France") if "France" in countries else 0
)

df_sel = df_soc[df_soc["country"] == selected_country].copy()

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

# Couleurs personnalisées
color_map = {
    "GDP per capita (current US$)": "red",
    "Urban population (% of total population)": "purple",
    "Access to basic drinking water (% of population)": "orange"
}
for trace in fig_line.data:
    trace.line.color = color_map.get(trace.name, None)

# Mise en forme
fig_line.update_layout(
    title=dict(
        text=f"Évolution temporelle normalisée des indicateurs sociétaux – {selected_country}",
        x=0.5,
        xanchor="center",
        font=dict(size=16)
    ),
    legend_title_text="",
    margin=dict(t=80, b=30)
)

st.plotly_chart(fig_line, use_container_width=True)
st.markdown("---")

# ===============================
# DOUBLE VISUEL : MATRICE + SCATTER PLOT
# ===============================
st.markdown("<h3 style='text-align: center;'>Relations entre société et économie</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Colonne gauche : Matrice de corrélation
with col1:

    st.markdown("<h4 style='text-align: center;'>Matrice de corrélation</h4>", unsafe_allow_html=True)

    # Renommage
    rename_dict = {
        "GDP per capita (current US$)": "PIB",
        "Urban population (% of total population)": "Population urbaine",
        "Access to basic drinking water (% of population)": "Accès eau potable"
    }

    # Préparation matrice
    pivot = df_sel.pivot(index="year", columns="indicator", values="value")
    corr = pivot.corr().round(2)

    # Renommage
    corr = corr.rename(index=rename_dict, columns=rename_dict)

    # Réordonner : PIB en premier
    new_order = [
        "PIB",
        "Population urbaine",
        "Accès eau potable"
    ]
    corr = corr.loc[new_order, new_order]

    # Triangle inférieur pour éviter les doublons
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

    # Mise en forme standardisée
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

# Colonne droite :
with col2:

    st.markdown("<h4 style='text-align: center;'>Scatter Plot International</h4>", unsafe_allow_html=True)

    # -------------------------------
    # Sélecteurs utilisateur
    # -------------------------------
    compare_countries = st.multiselect(
        "Comparer jusqu'à 3 pays :",
        options=df["country"].unique(),
        default=["France", "United States", "China"],
        max_selections=3
    )

    # Année sélectionnée
    year_selected = st.slider(
        "Sélectionner une année :",
        int(df["year"].min()),
        int(df["year"].max()),
        int(df["year"].max())
    )

    # -------------------------------
    # Extraction des données
    # -------------------------------
    df_soc = df[
        (df["country"].isin(compare_countries)) &
        (df["year"] == year_selected) &
        (df["indicator"].isin([
            "GDP per capita (current US$)",
            "Urban population (% of total population)"
        ]))
    ]

    df_soc = df_soc.pivot(
        index="country",
        columns="indicator",
        values="value"
    ).reset_index()

    # Si données manquantes
    df_soc = df_soc.dropna()

    # -------------------------------
    # SCATTER INTERACTIF PIB ↔ URBAN POP
    # -------------------------------

    fig = px.scatter(
    df_soc,
    x="GDP per capita (current US$)",
    y="Urban population (% of total population)",
    color="country",
    hover_name="country",
    log_x=True,
    size="Urban population (% of total population)",  # 🔥 Ajout taille dynamique
    size_max=60,  # 🔥 augmente la taille max des bulles
    template="plotly_white",
    title=f"PIB & Urbanisation – {year_selected}"
    )

    fig.update_layout(
        xaxis_title="PIB par habitant (USD, échelle logarithmique)",
        yaxis_title="Population urbaine (% du total)",
        title=dict(x=0.5, xanchor="center", font=dict(size=18)),
        height=450,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========
# CONCLUSION
# ==========
st.markdown("<h3 style='text-align: center;'>Ce que révèle l’analyse sociétale</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; max-width: 900px; margin: auto;'>

    <p>
    L’analyse croisée du PIB et des indicateurs sociétaux met en évidence un principe fondamental du
    développement durable : <strong>une économie n’est véritablement performante que si elle repose sur
    des conditions de vie sûres, inclusives et soutenues par des infrastructures solides</strong>.
    La richesse produite n’a de sens que si elle s’accompagne d’un environnement propice au bien-être
    et à l’épanouissement des populations.
    </p><br>

    <p>
    Le niveau d’urbanisation reflète la capacité d’un pays à offrir des opportunités économiques, des services,
    des transports et un cadre de vie adapté à une population croissante.
    <strong>Une urbanisation maîtrisée est souvent associée à une meilleure productivité et à une dynamique
    économique plus soutenue</strong>. À l’inverse, des disparités territoriales marquées ou une urbanisation
    insuffisamment accompagnée peuvent créer des vulnérabilités structurelles.
    </p><br>

    <p>
    L’accès à l’eau potable constitue un indicateur essentiel du bien-être humain : il renseigne sur la qualité
    des infrastructures, de la santé publique et du niveau général de sécurité sanitaire.
    <strong>Lorsque la croissance économique s’accompagne d’une amélioration de l’accès aux services essentiels,
    elle se traduit par un développement réellement inclusif</strong>.
    </p><br>

    <p>
    Confronter ces indicateurs sociétaux au PIB permet ainsi d’évaluer non seulement la richesse créée,
    mais aussi la manière dont elle se traduit en progrès social et territorial.
    <strong>Un développement équilibré repose sur des infrastructures fiables, un accès équitable aux ressources
    vitales et une organisation urbaine capable de soutenir la croissance démographique et économique</strong>.
    Cette analyse rappelle que la qualité du cadre de vie constitue un fondement indispensable d’un
    développement durable, humain et résilient.
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
