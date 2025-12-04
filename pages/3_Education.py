import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore
import os
import numpy as np

# CONFIGURATION

st.set_page_config(page_title="Éducation - Beyond GDP", page_icon="📚", layout="wide")

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
    "SE.XPD.TOTL.GD.ZS": "Government expenditure on education (% of GDP)",
    "SE.SEC.ENRR": "School enrollment, secondary (% gross)",
    "HD.HCI.OVRL": "Human capital index (0–1 scale)"
}

df_edu = df[df["indicator"].isin(indicators.values())]

# ================
# TITRE AVEC IMAGE
# ================

# Convertit l'image en base64
import base64

image_path = os.path.join(IMG_PATH, "RubanEducation.png")

with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-top:20px; margin-bottom:10px;">
        <img src="data:image/png;base64,{img_base64}" style="height:55px;">
        <h1 style="margin:0; padding:0;">Le PIB face aux indicateurs d'éducation</h1>
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
    st.markdown("<h4 style='text-align: center;'>Dépenses publiques d’éducation (% du PIB)</h4>", unsafe_allow_html=True)
    st.markdown("Regroupent l’ensemble des ressources financières que l’État consacre chaque année au fonctionnement du système éducatif, de l’école primaire à l’enseignement supérieur. Exprimées en pourcentage du PIB, elles indiquent la part de la richesse nationale investie dans l’éducation et reflètent l’engagement d’un pays en faveur du développement des compétences, du capital humain et de l’égalité des chances.")

with col2:
    st.markdown("<h4 style='text-align: center;'>Scolarisation dans le secondaire (% brut)</h4>", unsafe_allow_html=True)
    st.markdown("Mesure le nombre total d’élèves inscrits dans l’enseignement secondaire, quel que soit leur âge, rapporté à la population correspondant normalement à ce niveau d’enseignement. Exprimé en pourcentage, il permet d’évaluer l’accès à l’éducation secondaire et la capacité du système éducatif à accueillir les élèves. Un taux élevé reflète généralement une forte participation scolaire et un meilleur développement du capital humain.")

with col3:
    st.markdown("<h4 style='text-align: center;'>Indice capital humain (0–1)</h4>", unsafe_allow_html=True)
    st.markdown("Evalue le niveau de développement des compétences et du potentiel productif d’une population. Compris entre 0 et 1, il combine des dimensions telles que la santé, la scolarisation et la qualité de l’éducation. Un score élevé indique que les individus disposent de meilleures conditions pour apprendre, travailler et contribuer à la croissance économique future.")

st.markdown("---")

# ===============================
# IMPORTANCE DE LA CONFRONTATION
# ===============================
st.markdown("<h3 style='text-align: center;'>Pourquoi confronter le PIB à ces indicateurs ?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Le PIB indique ce qu’un pays produit aujourd’hui, mais il ne dit rien sur sa capacité à produire demain. Or, une économie ne peut être solide que si elle investit dans l’éducation, développe les compétences et garantit l’accès à la scolarité. Les dépenses d’éducation, la scolarisation et l’indice de capital humain révèlent la qualité des apprentissages, l’égalité des chances et le potentiel productif futur d’un pays. Confronter ces indicateurs au PIB permet donc de mesurer si la richesse actuelle repose sur un capital humain réellement formé et capable d’assurer la croissance de demain — ou si l’économie avance avec un désavantage structurel.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# GRAPHIQUE D'ÉVOLUTION COMPARATIVE (NORMALISÉE)
# ===============================
st.markdown("<h3 style='text-align: center;'>Évolution comparée du PIB et des indicateurs d’éducation</h3>", unsafe_allow_html=True)

countries = sorted(df_edu["country"].unique())
selected_country = st.selectbox(
    "Sélectionner un pays :",
    countries,
    index=countries.index("France") if "France" in countries else 0
)

df_sel = df_edu[df_edu["country"] == selected_country].copy()

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
    "Government expenditure on education (% of GDP)": "purple",
    "School enrollment, secondary (% gross)": "teal",
    "Human capital index (0–1 scale)": "orange"
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
# DOUBLE VISUEL : MATRICE + BUBBLE-BAR CHART
# ===============================
st.markdown("<h3 style='text-align: center;'>Relations entre éducation et performance économique</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Colonne gauche : Matrice de corrélation
with col1:

    st.markdown("<h4 style='text-align: center;'>Matrice de corrélation</h4>", unsafe_allow_html=True)

    # Renommage
    rename_dict = {
        "GDP per capita (current US$)": "PIB",
        "Government expenditure on education (% of GDP)": "Dépenses éducation",
        "School enrollment, secondary (% gross)": "Scolarisation secondaire",
        "Human capital index (0–1 scale)": "Capital humain"
    }

    # Préparation matrice
    pivot = df_sel.pivot(index="year", columns="indicator", values="value")
    corr = pivot.corr().round(2)

    # Renommage des colonnes et lignes
    corr = corr.rename(index=rename_dict, columns=rename_dict)

    # Réordonner : PIB en premier
    new_order = ["PIB", "Dépenses éducation", "Scolarisation secondaire", "Capital humain"]
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

# Colonne droite : Composite Bubble-Bar Chart
with col2:

    st.markdown("<h4 style='text-align: center;'>Composite Bubble-Bar Chart International</h4>", unsafe_allow_html=True)

    # Choisir plusieurs pays
    selected_countries_bar = st.multiselect(
        "Comparer plusieurs pays :",
        countries,
        default=["France", "Germany", "Japan"],
        max_selections=6
    )

    df_bar = df_edu[df_edu["country"].isin(selected_countries_bar)].copy()

    # Filtrer la dernière année disponible
    last_year = df_bar["year"].max()
    df_bar = df_bar[df_bar["year"] == last_year]

    # Garder uniquement PIB + scolarisation secondaire
    df_bar = df_bar[df_bar["indicator"].isin([
        "GDP per capita (current US$)",
        "School enrollment, secondary (% gross)"
    ])]

    # Pivot
    pivot_bar = df_bar.pivot(index="country", columns="indicator", values="value").reset_index()

    # Renommage clair
    pivot_bar = pivot_bar.rename(columns={
        "GDP per capita (current US$)": "PIB par habitant (USD)",
        "School enrollment, secondary (% gross)": "Scolarisation secondaire (%)"
    })

    # Normalisation pour éviter des bulles ridiculement grandes
    # (on réduit l’écart tout en gardant les différences)
    min_val = pivot_bar["Scolarisation secondaire (%)"].min()
    max_val = pivot_bar["Scolarisation secondaire (%)"].max()

    pivot_bar["bubble_size"] = ((pivot_bar["Scolarisation secondaire (%)"] - min_val) /
                                (max_val - min_val + 1e-9)) * 80 + 30
    # tailles entre 30 et 110 (ajustable)

    # Graphique barres + bulles
    fig_combo = px.bar(
        pivot_bar,
        x="country",
        y="PIB par habitant (USD)",
        color_discrete_sequence=["#4A90E2"]
    )

    # Ajouter les bulles proportionnelles
    fig_combo.add_scatter(
        x=pivot_bar["country"],
        y=pivot_bar["PIB par habitant (USD)"],
        mode="markers+text",
        marker=dict(
            size=pivot_bar["bubble_size"],
            color=pivot_bar["Scolarisation secondaire (%)"],
            colorscale="Viridis",
            showscale=True,
            colorbar_title="Scolarisation secondaire (%)"
        ),
        text=pivot_bar["Scolarisation secondaire (%)"].round(1),
        textposition="top center",
        name="Scolarisation secondaire (%)",
        showlegend=False
    )

    # Mise en forme
    fig_combo.update_layout(
        title=dict(
            text=f"PIB & Scolarisation secondaire — {last_year}",
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        xaxis_title="Pays",
        yaxis_title="PIB par habitant (USD)",
        margin=dict(t=80, b=30)
    )

    st.plotly_chart(fig_combo, use_container_width=True)

# ==========
# CONCLUSION
# ==========
st.markdown("<h3 style='text-align: center;'>Ce que révèle l’analyse éducative</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; max-width: 900px; margin: auto;'>

    <p>
    L’analyse croisée du PIB et des indicateurs d’éducation montre une réalité fondamentale :
    <strong>la prospérité économique n’a de sens que si elle s’accompagne d’un investissement soutenu
    dans le capital humain</strong>. Un pays peut afficher un PIB élevé, mais s’il néglige la formation,
    les compétences et l’accès à l’éducation, il fragilise son potentiel de croissance à long terme.
    </p><br>

    <p>
    Les dépenses publiques d’éducation, la scolarisation dans le secondaire et l’indice de capital humain
    révèlent la capacité d’un pays à préparer sa population aux exigences économiques contemporaines.
    <strong>Là où l’investissement éducatif est solide, les opportunités s'élargissent, l’innovation progresse
    et la mobilité sociale s’améliore.</strong> À l’inverse, une scolarisation faible ou un capital humain
    insuffisamment développé limite la productivité et accentue les inégalités.
    </p><br>

    <p>
    Ces données soulignent une idée centrale : <strong>l’éducation n’est pas un coût, mais un levier stratégique</strong>.
    Elle conditionne la résilience économique, l’employabilité, la compétitivité et la capacité d’un pays
    à s’adapter aux transformations technologiques et sociales.
    </p><br>

    <p>
    Confronter le PIB aux indicateurs éducatifs permet ainsi d’évaluer non seulement la richesse créée aujourd’hui,
    mais surtout la capacité d’une nation à assurer celle de demain. Le développement économique durable repose
    sur une population formée, qualifiée et en mesure de répondre aux défis futurs.
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