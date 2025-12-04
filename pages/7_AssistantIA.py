import streamlit as st # type: ignore
import pandas as pd
import os
import re
import plotly.express as px # type: ignore

# CONFIGURATION

st.set_page_config(page_title="Assistant IA - Beyond GDP", page_icon="🤖", layout="wide")

# AJOUT DU FOND

st.markdown("""
<style>
.stApp {
    background-color: #E8F2FD;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Style du champ de question */
textarea {
    border: 2px solid #7DADE5 !important;  /* Bleu clair ONU */
    border-radius: 8px !important;
    background-color: #F8FBFF !important; /* Gris très clair tirant vers le bleu */
    padding: 10px !important;
}

/* Boîte autour du composant Streamlit */
div[data-baseweb="textarea"] > div {
    border-radius: 8px !important;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.10);
}
</style>
""", unsafe_allow_html=True)

# CHEMINS D’ACCÈS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data_dashboard_BeyondGDP.csv")

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
# Dictionnaire indicateurs
# ========================

indicator_aliases = {
    # ========================
    #  ÉCONOMIE & PRODUCTIVITÉ
    # ========================
    # PIB / GDP per capita
    "pib": "GDP per capita (current US$)",
    "pib par habitant": "GDP per capita (current US$)",
    "pib/habitant": "GDP per capita (current US$)",
    "gdp": "GDP per capita (current US$)",
    "gdp per capita": "GDP per capita (current US$)",
    "revenu par habitant": "GDP per capita (current US$)",
    "richesse par habitant": "GDP per capita (current US$)",
    "productivité moyenne": "GDP per capita (current US$)",

    # Formation brute de capital
    "formation brute de capital": "Gross capital formation (% of GDP)",
    "investissement": "Gross capital formation (% of GDP)",
    "investissements": "Gross capital formation (% of GDP)",
    "capital formation": "Gross capital formation (% of GDP)",
    "gfcf": "Gross capital formation (% of GDP)",
    "formation capital": "Gross capital formation (% of GDP)",
    "brut capital": "Gross capital formation (% of GDP)",

    # Inflation
    "inflation": "Inflation, consumer prices (annual %)",
    "hausse des prix": "Inflation, consumer prices (annual %)",
    "prix à la consommation": "Inflation, consumer prices (annual %)",
    "variation des prix": "Inflation, consumer prices (annual %)",


    # ==================
    #  SANTÉ & BIEN-ÊTRE
    # ==================
    # Espérance de vie
    "espérance de vie": "Life expectancy at birth (years)",
    "esperance de vie": "Life expectancy at birth (years)",
    "life expectancy": "Life expectancy at birth (years)",
    "vie": "Life expectancy at birth (years)",
    "longevité": "Life expectancy at birth (years)",

    # Dépenses de santé (% PIB)
    "dépenses de santé": "Current health expenditure (% of GDP)",
    "depenses de sante": "Current health expenditure (% of GDP)",
    "santé (% pib)": "Current health expenditure (% of GDP)",
    "health expenditure": "Current health expenditure (% of GDP)",
    "dépenses médicales": "Current health expenditure (% of GDP)",

    # Mortalité des -5 ans
    "mortalité des enfants": "Mortality rate, under-5 (per 1,000 live births)",
    "mortalité moins de 5 ans": "Mortality rate, under-5 (per 1,000 live births)",
    "taux mortalité enfant": "Mortality rate, under-5 (per 1,000 live births)",
    "under 5 mortality": "Mortality rate, under-5 (per 1,000 live births)",
    "u5mr": "Mortality rate, under-5 (per 1,000 live births)",


    # ===========================
    #  ÉDUCATION & CAPITAL HUMAIN
    # ===========================
    # Dépenses publiques d’éducation
    "dépenses éducation": "Government expenditure on education (% of GDP)",
    "depenses education": "Government expenditure on education (% of GDP)",
    "éducation (% pib)": "Government expenditure on education (% of GDP)",
    "education spending": "Government expenditure on education (% of GDP)",

    # Scolarisation secondaire
    "scolarisation secondaire": "School enrollment, secondary (% gross)",
    "taux scolarisation secondaire": "School enrollment, secondary (% gross)",
    "école secondaire": "School enrollment, secondary (% gross)",
    "lycée": "School enrollment, secondary (% gross)",
    "secondary enrollment": "School enrollment, secondary (% gross)",

    # Indice de capital humain
    "capital humain": "Human capital index (0–1 scale)",
    "hci": "Human capital index (0–1 scale)",
    "indice hci": "Human capital index (0–1 scale)",
    "human capital": "Human capital index (0–1 scale)",


    # ========================
    #  ENVIRONNEMENT & ÉNERGIE
    # ========================
    # CO₂ per capita
    "co2": "CO₂ emissions per capita (t/person, AR5)",
    "co₂": "CO₂ emissions per capita (t/person, AR5)",
    "émissions co2": "CO₂ emissions per capita (t/person, AR5)",
    "émissions carbone": "CO₂ emissions per capita (t/person, AR5)",
    "pollution carbone": "CO₂ emissions per capita (t/person, AR5)",
    "carbon emissions": "CO₂ emissions per capita (t/person, AR5)",

    # Renouvelables
    "énergies renouvelables": "Renewable energy consumption (% of total final energy)",
    "energies renouvelables": "Renewable energy consumption (% of total final energy)",
    "renouvelables": "Renewable energy consumption (% of total final energy)",
    "renewables": "Renewable energy consumption (% of total final energy)",
    "renewable consumption": "Renewable energy consumption (% of total final energy)",

    # PM2.5
    "pm2.5": "PM2.5 air pollution (µg/m³)",
    "pollution pm25": "PM2.5 air pollution (µg/m³)",
    "pollution particules": "PM2.5 air pollution (µg/m³)",
    "particules fines": "PM2.5 air pollution (µg/m³)",
    "air quality": "PM2.5 air pollution (µg/m³)",


    # ======================
    #  INÉGALITÉS & PAUVRETÉ
    # ======================
    # Indice de Gini
    "gini": "Gini index",
    "indice de gini": "Gini index",
    "inégalités": "Gini index",
    "inegalites": "Gini index",

    # Pauvreté monétaire
    "pauvreté": "Poverty headcount ratio at $3.65/day (2021 PPP)",
    "pauvrete": "Poverty headcount ratio at $3.65/day (2021 PPP)",
    "pauvreté extrême": "Poverty headcount ratio at $3.65/day (2021 PPP)",
    "pauvreté monétaire": "Poverty headcount ratio at $3.65/day (2021 PPP)",


    # =========================
    #  SOCIÉTÉ & INFRASTRUCTURE
    # =========================
    # Population urbaine
    "population urbaine": "Urban population (% of total population)",
    "urbain": "Urban population (% of total population)",
    "urbanisation": "Urban population (% of total population)",
    "urban population": "Urban population (% of total population)",

    # Eau potable
    "eau potable": "Access to basic drinking water (% of population)",
    "eau": "Access to basic drinking water (% of population)",
    "eau propre": "Access to basic drinking water (% of population)",
    "drinking water": "Access to basic drinking water (% of population)",
}

# =================
# Dictionnaire pays
# =================

country_aliases = {
    # Europe
    "france": "France",
    "allemagne": "Germany",
    "royaume-uni": "United Kingdom",
    "royaume uni": "United Kingdom",
    "angleterre": "United Kingdom",
    "etats-unis": "United States",
    "états-unis": "United States",
    "usa": "United States",
    "états unis": "United States",
    "chine": "China",
    "inde": "India",
    "japon": "Japan",
    "russie": "Russian Federation",
    "espagne": "Spain",
    "italie": "Italy",
    "belgique": "Belgium",
    "suisse": "Switzerland",
    "autriche": "Austria",
    "pologne": "Poland",
    "portugal": "Portugal",
    "pays-bas": "Netherlands",
    "pays bas": "Netherlands",
    "irlande": "Ireland",
    "islande": "Iceland",
    "norvege": "Norway",
    "norvège": "Norway",
    "suede": "Sweden",
    "suède": "Sweden",
    "danemark": "Denmark",
    "finlande": "Finland",

    # Afrique
    "algérie": "Algeria",
    "algerie": "Algeria",
    "maroc": "Morocco",
    "tunisie": "Tunisia",
    "egypte": "Egypt, Arab Rep.",
    "égypte": "Egypt, Arab Rep.",
    "afrique du sud": "South Africa",
    "nigeria": "Nigeria",
    "ethiopie": "Ethiopia",
    "éthiopie": "Ethiopia",
    "kenya": "Kenya",
    "cameroun": "Cameroon",
    "côte d'ivoire": "Cote d'Ivoire",
    "cote d'ivoire": "Cote d'Ivoire",
    "senegal": "Senegal",
    "sénégal": "Senegal",
    "mali": "Mali",
    "ghana": "Ghana",

    # Amériques
    "canada": "Canada",
    "mexique": "Mexico",
    "argentine": "Argentina",
    "brésil": "Brazil",
    "bresil": "Brazil",
    "chili": "Chile",
    "pérou": "Peru",
    "perou": "Peru",
    "colombie": "Colombia",
    "venezuela": "Venezuela, RB",
    "uruguay": "Uruguay",
    "paraguay": "Paraguay",

    # Asie
    "indonésie": "Indonesia",
    "indonesie": "Indonesia",
    "corée du sud": "Korea, Rep.",
    "corée": "Korea, Rep.",
    "coree": "Korea, Rep.",
    "turquie": "Turkiye",
    "saoudite": "Saudi Arabia",
    "arabie saoudite": "Saudi Arabia",
    "émirats arabes unis": "United Arab Emirates",
    "emirats arabes unis": "United Arab Emirates",
    "qatar": "Qatar",
    "pakistan": "Pakistan",
    "bangladesh": "Bangladesh",
    "vietnam": "Viet Nam",
    "thaïlande": "Thailand",
    "thailande": "Thailand",
    "iran": "Iran, Islamic Rep.",
    "irak": "Iraq",

    # Océanie
    "australie": "Australia",
    "nouvelle-zélande": "New Zealand",
    "nouvelle zelande": "New Zealand",

    # Europe de l'Est / Balkans
    "ukraine": "Ukraine",
    "serbie": "Serbia",
    "croatie": "Croatia",
    "roumanie": "Romania",
    "bulgarie": "Bulgaria",
    "hongrie": "Hungary",
    "tchéquie": "Czechia",
    "slovaquie": "Slovak Republic",
    "slovénie": "Slovenia",
    "lettonie": "Latvia",
    "lituanie": "Lithuania",
    "estonie": "Estonia",
}

def smart_query(question, df): 
    # normaliser en minuscules
    q = question.lower()

    # ======================================
    # 0) Conversion FR → EN des noms de pays
    # ======================================
    for fr, en in country_aliases.items():
        if fr in q:
            q = q.replace(fr, en.lower())

    # ======================================
    # 1) Extraction multi-pays (EN après traduction)
    # ======================================
    all_countries = df["country"].unique()
    countries = [c for c in all_countries if c.lower() in q]

    # =========================
    # 2) Extraction d'une année (OBLIGATOIRE)
    # =========================
    match = re.search(r"(19|20)\d{2}", q)
    if match:
        year = int(match.group())
    else:
        return "Veuillez préciser une année (ex : 2010)."

    # =========================
    # 3) Extraction indicateurs
    # =========================
    indicators_found = []

    # alias français → indicateur anglais
    for alias, name in indicator_aliases.items():
        if alias in q:
            indicators_found.append(name)

    # recherche dans les noms anglais officiels
    if not indicators_found:
        for ind in df["indicator"].unique():
            if any(w in q for w in ind.lower().split()):
                indicators_found.append(ind)

    indicators_found = list(set(indicators_found))

    if not indicators_found:
        return "Quel indicateur souhaitez-vous analyser ?"

    ind = indicators_found[0]

    # =========================
    # 4) Cas multi-pays avec UNE année
    # =========================
    if countries:
        d = df[
            (df["indicator"] == ind) &
            (df["country"].isin(countries)) &
            (df["year"] == year)
        ]

        if d.empty:
            return "Aucune donnée trouvée."

        # 1 seul pays → juste tableau
        if len(countries) == 1:
            return d

        # plusieurs pays → tableau + scatter
        pivot = d.pivot(index="year", columns="country", values="value")

        pivot_long = pivot.reset_index().melt(
            id_vars="year",
            var_name="country",
            value_name="value"
        )

        fig = px.scatter(
            pivot_long,
            x="country",
            y="value",
            color="country",
            hover_data={"year": True, "country": True, "value": True},
            size="value",
            size_max=40,
            title=f"{ind} en {year}"
        )

        return pivot, fig

    # =======================
    # 5) Cas min/max global
    # =======================
    if "plus faible" in q or "plus bas" in q or "minimum" in q:
        d = df[(df["indicator"] == ind) & (df["year"] == year)]
        return d.sort_values("value").head(1)

    if "plus élevé" in q or "maximum" in q or "plus haut" in q:
        d = df[(df["indicator"] == ind) & (df["year"] == year)]
        return d.sort_values("value", ascending=False).head(1)

    # ================
    # 6) Rien compris
    # ================
    return "Je comprends la question, mais j’ai besoin d’un pays, d’une année ou d’un indicateur."

# =========
# INTERFACE
# =========
st.markdown("<h1 style='text-align: center;'>Assistant IA - Analyse locale</h1>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
<p style="font-size:14px; text-align:justify;">
Cette page vous permet d’interroger la base <strong>Beyond GDP</strong> en langage naturel afin d’obtenir 
des valeurs précises pour une année donnée, des comparaisons entre plusieurs pays ou encore des classements 
tels que les minima et maxima d’un indicateur.  
L’assistant reconnaît les noms de pays en français (<em>Chine, États-Unis, Royaume-Uni…</em>) 
comme en anglais, ainsi qu’un large éventail d’indicateurs économiques, sociaux, sanitaires, éducatifs ou environnementaux.

Voici quelques exemples de questions que vous pouvez poser :
</p>

<ul style="font-size:14px; line-height:1.5;">
<li><em>PIB par habitant en France en 2010</em></li>
<li><em>Comparaison de l’espérance de vie entre France, Japon et États-Unis en 2005</em></li>
<li><em>Quel pays a le Gini le plus faible en 2020 ?</em></li>
<li><em>Dépenses de santé (% PIB) en Allemagne en 2018</em></li>
<li><em>Population urbaine en Inde en 1990</em></li>
<li><em>Quel pays a les émissions de CO₂ les plus élevées en 2015 ?</em></li>
</ul>
""", unsafe_allow_html=True)


question = st.text_area("Posez une question :", height=120)

if st.button("Analyser la question"):
    if not question.strip():
        st.warning("Veuillez entrer une question.")
    else:
        st.markdown("### Résultat")

        result = smart_query(question, df)

        # ====================================================
        # CAS 1 : Le modèle renvoie un tuple → (pivot, fig)
        # ====================================================
        if isinstance(result, tuple) and len(result) == 2:
            pivot, fig = result

            st.write("Voici la comparaison demandée :")
            st.dataframe(pivot)

            # Affichage du graphique uniquement s’il y a assez de points :
            # - ≥ 2 années (plusieurs lignes)
            # - OU ≥ 2 pays (plusieurs colonnes)
            if (len(pivot.index) > 1) or (len(pivot.columns) > 1):
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas assez de points pour tracer un graphique pertinent.")

        # ==============================================
        # CAS 2 : Le modèle renvoie un DataFrame simple
        #        → min/max, valeur unique, filtre simple
        # ==============================================
        elif isinstance(result, pd.DataFrame):

            # Cas 2A : Une seule ligne → phrase + tableau
            if len(result) == 1:
                pays = result["country"].values[0]
                année = result["year"].values[0]
                valeur = result["value"].values[0]
                indicateur = result["indicator"].values[0]

                st.write(f"En **{année}**, la valeur de **{indicateur}** pour **{pays}** est **{valeur:,.2f}**.")
                st.dataframe(result)

            # Cas 2B : Plusieurs lignes → juste tableau
            else:
                st.write("Voici les données correspondant à votre requête :")
                st.dataframe(result)

        # ====================================================
        # CAS 3 : Le modèle renvoie une phrase → réponse simple
        # ====================================================
        elif isinstance(result, str):
            st.write(result)

        # ===================
        # CAS 4 : Cas imprévu
        # ===================
        else:
            st.warning("Je n'ai pas pu interpréter correctement la question.")

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

