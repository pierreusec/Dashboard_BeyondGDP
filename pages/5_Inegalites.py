import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import os
import numpy as np 

# CONFIGURATION

st.set_page_config(page_title="Inégalités - Beyond GDP", page_icon="⚖️", layout="wide")

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
    "SI.POV.GINI": "Gini index",
    "SI.POV.DDAY": "Poverty headcount ratio at $3.65/day (2021 PPP)"
}

df_ineg = df[df["indicator"].isin(indicators.values())]

# ================
# TITRE AVEC IMAGE
# ================
import base64

image_path = os.path.join(IMG_PATH, "RubanInegalites.png")

with open(image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-top:20px; margin-bottom:10px;">
        <img src="data:image/png;base64,{img_base64}" style="height:55px;">
        <h1 style="margin:0; padding:0;">Le PIB face aux indicateurs d'inégalités</h1>
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
    st.markdown("<h4 style='text-align: center;'>Indice de Gini</h4>", unsafe_allow_html=True)
    st.markdown("Mesure le niveau d’inégalité dans la distribution des revenus au sein d’un pays. Compris entre 0 et 100, un score proche de 0 indique une répartition égalitaire, tandis qu’un score élevé reflète de fortes disparités. Cet indicateur est largement utilisé pour analyser l’équité sociale et économique.")

with col2:
    st.markdown("<h4 style='text-align: center;'>Pauvreté monétaire ($3.65/jour)</h4>", unsafe_allow_html=True)
    st.markdown("Correspond à la proportion de personnes vivant avec un revenu inférieur à ce montant en parité de pouvoir d’achat. Cet indicateur permet d’évaluer l’extrême pauvreté et de suivre les progrès réalisés en matière de réduction de la vulnérabilité économique.")

st.markdown("---")

# ===============================
# IMPORTANCE DE LA CONFRONTATION
# ===============================
st.markdown("<h3 style='text-align: center;'>Pourquoi confronter le PIB à ces indicateurs d’inégalités ?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Le PIB mesure la richesse totale produite par un pays, mais il ne dit rien sur la manière dont cette richesse est répartie ni sur le niveau de vie réel des populations. Des inégalités fortes, une pauvreté persistante ou un accès insuffisant à des services essentiels fragilisent directement le développement économique : elles réduisent les opportunités, limitent l’éducation, freinent l’emploi et accentuent les tensions sociales. L’indice de Gini et la pauvreté monétaire révèlent la capacité d’un pays à offrir des conditions de vie dignes et équitables à l’ensemble de sa population. Confronter ces indicateurs au PIB permet donc d’évaluer si la croissance bénéficie réellement à tous — ou si elle se concentre entre les mains de quelques-uns, au détriment du développement humain et de la stabilité économique.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# GRAPHIQUE D'ÉVOLUTION COMPARATIVE (NORMALISÉE)
# ===============================
st.markdown("<h3 style='text-align: center;'>Évolution comparée du PIB et des indicateurs d’inégalités</h3>", unsafe_allow_html=True)

countries = sorted(df_ineg["country"].unique())
selected_country = st.selectbox(
    "Sélectionner un pays :",
    countries,
    index=countries.index("France") if "France" in countries else 0
)

df_sel = df_ineg[df_ineg["country"] == selected_country].copy()

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
    "Gini index": "purple",
    "Poverty headcount ratio at $3.65/day (2021 PPP)": "darkgreen"
}
for trace in fig_line.data:
    trace.line.color = color_map.get(trace.name, None)

# Mise en forme du graphique
fig_line.update_layout(
    title=dict(
        text=f"Évolution temporelle normalisée des indicateurs d’inégalités – {selected_country}",
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
# DOUBLE VISUEL : MATRICE + QUADRANT CHART
# ===============================
st.markdown("<h3 style='text-align: center;'>Relations entre inégalités et économie</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Colonne gauche : Matrice de corrélation
with col1:

    st.markdown("<h4 style='text-align: center;'>Matrice de corrélation</h4>", unsafe_allow_html=True)

    rename_dict = {
        "GDP per capita (current US$)": "PIB",
        "Gini index": "Indice de Gini",
        "Poverty headcount ratio at $3.65/day (2021 PPP)": "Pauvreté (<3.65$/jour)"
    }

    pivot = df_sel.pivot(index="year", columns="indicator", values="value")
    corr = pivot.corr().round(2)
    corr = corr.rename(index=rename_dict, columns=rename_dict)

    new_order = ["PIB", "Indice de Gini", "Pauvreté (<3.65$/jour)"]
    corr = corr.loc[new_order, new_order]

    mask = np.tril(np.ones_like(corr, dtype=bool))
    corr_tri = corr.where(mask)

    fig = px.imshow(
        corr_tri,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto"
    )

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

    st.markdown("<h4 style='text-align: center;'>Quadrant Chart International</h4>", unsafe_allow_html=True)

    # -------------------------------
    # Sélecteurs utilisateur
    # -------------------------------

    compare_countries = st.multiselect(
        "Comparer jusqu'à 3 pays :",
        options=df["country"].unique(),
        default=["France", "China", "United States"],   # Valeurs par défaut
        max_selections=3
    )

    inequality_indicator = st.selectbox(
        "Choisir un indicateur d’inégalités :",
        [
            "Gini index",
            "Poverty headcount ratio at $3.65/day (2021 PPP)"
        ]
    )

    # Année par défaut = 2022 si disponible, sinon dernière année
    default_year = 2022 if 2022 in df["year"].unique() else int(df["year"].max())

    year_selected = st.slider(
        "Sélectionner une année :",
        int(df["year"].min()),
        int(df["year"].max()),
        default_year
    )

    # -------------------------------
    # Extraction et pivot
    # -------------------------------
    df_quad = df[
        (df["country"].isin(compare_countries)) &
        (df["year"] == year_selected) &
        (df["indicator"].isin([
            "GDP per capita (current US$)",
            inequality_indicator
        ]))
    ]

    df_quad = df_quad.pivot(
        index="country",
        columns="indicator",
        values="value"
    ).reset_index()

    df_quad = df_quad.dropna()

    # -------------------------------
    # Calcul des médianes pour quadrants
    # -------------------------------
    gdp_median = df_quad["GDP per capita (current US$)"].median()
    ineq_median = df_quad[inequality_indicator].median()

    # -------------------------------
    # Quadrant Chart
    # -------------------------------

    fig_quad = go.Figure()

    # Quadrant 1 : Haut PIB - fortes inégalités
    fig_quad.add_shape(
        type="rect",
        x0=gdp_median, x1=df_quad["GDP per capita (current US$)"].max(),
        y0=ineq_median, y1=df_quad[inequality_indicator].max(),
        fillcolor="rgba(0, 128, 0, 0.08)", line_width=0
    )

    # Quadrant 2 : Bas PIB - fortes inégalités
    fig_quad.add_shape(
        type="rect",
        x0=df_quad["GDP per capita (current US$)"].min(), x1=gdp_median,
        y0=ineq_median, y1=df_quad[inequality_indicator].max(),
        fillcolor="rgba(255, 165, 0, 0.08)", line_width=0
    )

    # Quadrant 3 : Haut PIB - faibles inégalités
    fig_quad.add_shape(
        type="rect",
        x0=gdp_median, x1=df_quad["GDP per capita (current US$)"].max(),
        y0=df_quad[inequality_indicator].min(), y1=ineq_median,
        fillcolor="rgba(135, 206, 250, 0.10)", line_width=0
    )

    # Quadrant 4 : Bas PIB - faibles inégalités
    fig_quad.add_shape(
        type="rect",
        x0=df_quad["GDP per capita (current US$)"].min(), x1=gdp_median,
        y0=df_quad[inequality_indicator].min(), y1=ineq_median,
        fillcolor="rgba(240, 128, 128, 0.10)", line_width=0
    )

    # Points des pays
    fig_quad.add_trace(go.Scatter(
        x=df_quad["GDP per capita (current US$)"],
        y=df_quad[inequality_indicator],
        mode="markers+text",
        text=df_quad["country"],
        textposition="top center",
        marker=dict(size=16, color="#4C72B0"),
        hovertemplate="<b>%{text}</b><br>PIB/hab: %{x:$,.0f}<br>Inégalité: %{y:.2f}<extra></extra>"
    ))

    # -------------------------------
    # Mise en forme finale
    # -------------------------------
    fig_quad.update_layout(
        title=dict(
            text=f"Positionnement des pays - {year_selected}",
            x=0.5,            # Centre horizontal
            xanchor="center",
            font=dict(size=18)
        ),
        xaxis=dict(
            title="PIB par habitant (USD)",
            type="log",
            showgrid=True
        ),
        yaxis=dict(
            title=inequality_indicator,
            showgrid=True
        ),
        height=450,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_quad, use_container_width=True)

# ==========
# CONCLUSION
# ==========
st.markdown("<h3 style='text-align: center;'>Ce que révèle l’analyse des inégalités</h3>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; max-width: 900px; margin: auto;'>

    <p>
    L’analyse conjointe du PIB et des indicateurs d’inégalités met en évidence une réalité essentielle du développement :
    <strong>la richesse économique n’a de portée que si elle est partagée de manière équitable et si elle garantit
    des conditions de vie dignes à l’ensemble de la population</strong>.
    La croissance ne peut être considérée comme un progrès lorsqu’elle s’accompagne d’un creusement des écarts
    ou d’une persistance de la pauvreté.
    </p><br>

    <p>
    L’indice de Gini et le taux de pauvreté monétaire révèlent la manière dont les fruits de la croissance sont distribués.
    <strong>Des inégalités élevées fragilisent la cohésion sociale, limitent la mobilité économique et réduisent
    l’efficacité des politiques publiques</strong>.
    À l’inverse, un faible niveau d’inégalités ou une réduction durable de la pauvreté témoignent d’un modèle
    de développement plus inclusif, capable d’améliorer le bien-être collectif.
    </p><br>

    <p>
    Ces indicateurs soulignent une notion fondamentale : 
    <strong>la qualité d’un modèle économique ne se mesure pas uniquement à la richesse créée, 
    mais à la manière dont cette richesse transforme la vie des individus</strong>.
    Un pays peut afficher un PIB élevé tout en laissant persister des inégalités structurelles,
    ou au contraire progresser économiquement tout en renforçant l’équité et l’inclusion.
    </p><br>

    <p>
    Confronter le PIB aux mesures des inégalités permet ainsi de comprendre si la croissance bénéficie réellement à l’ensemble
    de la société — ou si elle demeure concentrée entre les mains de quelques-uns.
    <strong>Un développement durable et humainement centré exige non seulement de créer de la richesse,
    mais aussi de la distribuer de manière à garantir justice sociale, stabilité et opportunités pour tous</strong>.
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
