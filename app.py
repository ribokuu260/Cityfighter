import requests
import streamlit as st
import pandas as pd

from datetime import datetime

st.markdown(
    """
    <style>
        .css-1q3owr1 {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #ffffff;
            z-index: 999;
            box-shadow: 0px 4px 2px -2px gray;
            padding: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def get_weather_icon(description):
    description = description.lower()
    if "soleil" in description or "dégagé" in description:
        return "☀️"
    elif "nuage" in description:
        return "☁️"
    elif "pluie" in description:
        return "🌧️"
    elif "orage" in description:
        return "⛈️"
    elif "neige" in description:
        return "❄️"
    else:
        return "🌫️"

from datetime import datetime

def afficher_meteo_illustree(ville, previsions):
    st.markdown(f"<h4 style='margin-bottom: 0.5em;'>📆 Prévisions illustrées – {ville}</h4>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    for i, item in enumerate(previsions):
        date_str, reste = item.split(" : ")
        temp, desc = reste.split("°C, ")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        jour = date_obj.strftime("%a").capitalize()

        icone = get_weather_icon(desc)

        bloc = f"""
        <div style='
            background: #f0f4ff;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            box-shadow: 0px 1px 4px rgba(0,0,0,0.1);
        '>
            <div style='font-size: 24px;'>{jour}</div>
            <div style='font-size: 32px;'>{icone}</div>
            <div style='font-size: 18px; font-weight:bold;'>{temp.strip()}°C</div>
            <div style='font-size: 14px; color: #555;'>{desc.strip()}</div>
        </div>
        """

        if i == 0: col1.markdown(bloc, unsafe_allow_html=True)
        elif i == 1: col2.markdown(bloc, unsafe_allow_html=True)
        elif i == 2: col3.markdown(bloc, unsafe_allow_html=True)
        elif i == 3: col4.markdown(bloc, unsafe_allow_html=True)
        elif i == 4: col5.markdown(bloc, unsafe_allow_html=True)


st.title("Bienvenue dans City Fighting")
st.write("Comparaison de deux villes sur plusieurs critères.")
# --- MENU LATERAL ---
st.sidebar.title("📊 Menu de navigation")
sections = {
    "Informations générales": st.sidebar.checkbox("📍 Informations générales", value=True),
    "Carte": st.sidebar.checkbox("🗺️ Carte des mairies", value=True),
    "Emploi": st.sidebar.checkbox("💼 Emploi", value=True),
    "Statuts emploi": st.sidebar.checkbox("📈 Emploi : Statuts", value=True),
    "Logement": st.sidebar.checkbox("🏡 Logement", value=True),
    "Logement détaillé": st.sidebar.checkbox("📊 Logement : Types", value=True),
    "Tourisme": st.sidebar.checkbox("🌍 Tourisme et découverte", value=True),
    "Tourisme capacité": st.sidebar.checkbox("🛎️ Capacité touristique", value=True)
}

#Chargement données Communes FR

@st.cache_data
def charger_villes():
    df = pd.read_csv("communes.csv", sep=",")
    df = df[df["population"] > 20000]  # filtrage
    return df.sort_values(by="population", ascending=False)
    

villes = charger_villes()

api_key = '1f57b67fa4a6baf27ca13587d2e91d20'

def get_weather_forecast(ville, api_key, n=5):
    try:
        # Ajoute ",FR" pour forcer la France
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={ville},FR&appid={api_key}&units=metric&lang=fr"
        response = requests.get(url)
        data = response.json()

        # S'il y a une erreur dans la réponse
        if data.get("cod") != "200":
            return [f"Erreur API : {data.get('message', 'inconnue')}"]

        previsions = []
        for item in data["list"]:
            if "12:00:00" in item["dt_txt"]:
                date = item["dt_txt"].split(" ")[0]
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]
                previsions.append(f"{date} : {temp}°C, {desc}")
                if len(previsions) >= n:
                    break

        return previsions

    except Exception as e:
        return [f"Erreur technique : {e}"]

    
# Sélecteurs Streamlit
col_sel1, col_sel2 = st.columns(2)

with col_sel1:
    ville1 = st.selectbox("🏙️ Choisissez la première ville :", villes["nom_standard"].unique())

with col_sel2:
    ville2 = st.selectbox("🏙️ Choisissez la deuxième ville :", villes["nom_standard"].unique())

st.markdown("---")

infos1 = villes[villes["nom_standard"] == ville1].iloc[0]
infos2 = villes[villes["nom_standard"] == ville2].iloc[0]

if sections["Informations générales"]:
    st.subheader("📍 Informations Générales")
    col1, col2 = st.columns(2)

    def bloc_infos_ville(nom_ville, infos):
        st.markdown(
            f"""
            <div style="background-color:#f9f9f9; padding: 20px; border-radius: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <h3 style="margin-top:0;">{nom_ville}</h3>
                <p>👥 <b>Population :</b> {int(infos['population'])}</p>
                <p>📏 <b>Superficie :</b> {infos['superficie_km2']} km²</p>
                <p>🏙️ <b>Densité :</b> {infos['densite']} hab/km²</p>
                <p>📌 <b>Département :</b> {infos['dep_nom']}</p>
                <p>🗺️ <b>Région :</b> {infos['reg_nom']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col1:
        bloc_infos_ville(ville1, infos1)

    with col2:
        bloc_infos_ville(ville2, infos2)

    # Prévisions météo
    col_meteo1, col_meteo2 = st.columns([1, 1], gap="large")

    with col_meteo1:
        afficher_meteo_illustree(ville1, get_weather_forecast(ville1, api_key))

    with col_meteo2:
        afficher_meteo_illustree(ville2, get_weather_forecast(ville2, api_key))

    # Mini graphe de densité
    st.markdown("#### 📊 Comparaison des densités")
    import matplotlib.pyplot as plt

    densites = [infos1["densite"], infos2["densite"]]
    labels = [ville1, ville2]
    fig, ax = plt.subplots()
    ax.bar(labels, densites, color=["#3498db", "#2ecc71"])
    ax.set_ylabel("hab/km²")
    ax.set_title("Densité de population")
    st.pyplot(fig)



import folium
from streamlit_folium import st_folium

# Créer une carte centrée entre les 2 villes
centre_lat = (infos1['latitude_mairie'] + infos2['latitude_mairie']) / 2
centre_lon = (infos1['longitude_mairie'] + infos2['longitude_mairie']) / 2
ma_carte = folium.Map(location=[centre_lat, centre_lon], zoom_start=6)

# Ajout des marqueurs
folium.Marker(
    location=[infos1['latitude_mairie'], infos1['longitude_mairie']],
    popup=f"{ville1} (mairie)",
    tooltip=ville1,
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(ma_carte)

folium.Marker(
    location=[infos2['latitude_mairie'], infos2['longitude_mairie']],
    popup=f"{ville2} (mairie)",
    tooltip=ville2,
    icon=folium.Icon(color="green", icon="info-sign")
).add_to(ma_carte)

# Affichage dans Streamlit
if sections["Carte"]:
    st.subheader("🗺️ Carte des mairies")
    st_folium(ma_carte, width=700, height=500)


@st.cache_data
def charger_donnees_emploi():
    df = pd.read_csv("dossier_complet.csv", sep=";", encoding="latin1", low_memory=False)
    df = df[["CODGEO", "P21_ACT1564", "P21_CHOM1564"]]
    df.columns = ["code_insee", "actifs", "chomeurs"]
    df[["actifs", "chomeurs"]] = df[["actifs", "chomeurs"]].apply(pd.to_numeric, errors="coerce")
    df["taux_chomage"] = (df["chomeurs"] / df["actifs"]) * 100
    return df


emploi = charger_donnees_emploi()
villes["code_insee"] = villes["code_insee"].astype(str)
emploi["code_insee"] = emploi["code_insee"].astype(str)
villes = villes.merge(emploi, on="code_insee", how="left")

# MAJ infos après fusion
infos1 = villes[villes["nom_standard"] == ville1].iloc[0]
infos2 = villes[villes["nom_standard"] == ville2].iloc[0]

# 🔍 DEBUG facultatif pour vérifier les colonnes après fusion
# st.write("🔍 Colonnes après fusion :", villes.columns.tolist())
# st.write("🔍 Ville 1 complète :", infos1)

# Section : Données sur l'emploi
if sections["Emploi"]:
    st.subheader("💼 Données sur l'emploi")

    # Création du tableau comparatif
    data_emploi = {
        "Indicateur": ["Actifs 15-64 ans", "Chômeurs 15-64 ans", "Taux de chômage"],
        ville1: [
            int(infos1["actifs"]) if pd.notna(infos1["actifs"]) else "N/A",
            int(infos1["chomeurs"]) if pd.notna(infos1["chomeurs"]) else "N/A",
            f"{infos1['taux_chomage']:.1f} %" if pd.notna(infos1["taux_chomage"]) else "N/A"
        ],
        ville2: [
            int(infos2["actifs"]) if pd.notna(infos2["actifs"]) else "N/A",
            int(infos2["chomeurs"]) if pd.notna(infos2["chomeurs"]) else "N/A",
            f"{infos2['taux_chomage']:.1f} %" if pd.notna(infos2["taux_chomage"]) else "N/A"
        ]
    }

    df_emploi = pd.DataFrame(data_emploi)
    st.table(df_emploi)

@st.cache_data
def charger_donnees_logement():
    df = pd.read_csv("dossier_complet.csv", sep=";", encoding="latin1", low_memory=False)
    df = df[["CODGEO", "P21_RP", "P21_LOGVAC", "P21_RSECOCC"]]
    df.columns = ["code_insee", "residences_principales", "logements_vacants", "residences_secondaires"]
    return df

logement = charger_donnees_logement()
logement["code_insee"] = logement["code_insee"].astype(str)
villes = villes.merge(logement, on="code_insee", how="left")

# MAJ infos après fusion
infos1 = villes[villes["nom_standard"] == ville1].iloc[0]
infos2 = villes[villes["nom_standard"] == ville2].iloc[0]

if sections["Logement"]:
    st.subheader("🏡 Données sur le logement")
    col_log1, col_log2 = st.columns(2)

    with col_log1:
        st.markdown(f"### {ville1}")
        st.write(f"Résidences principales : {int(infos1['residences_principales']) if pd.notna(infos1['residences_principales']) else 'N/A'}")
        st.write(f"Résidences secondaires : {int(infos1['residences_secondaires']) if pd.notna(infos1['residences_secondaires']) else 'N/A'}")
        st.write(f"Logements vacants : {int(infos1['logements_vacants']) if pd.notna(infos1['logements_vacants']) else 'N/A'}")

    with col_log2:
        st.markdown(f"### {ville2}")
        st.write(f"Résidences principales : {int(infos2['residences_principales']) if pd.notna(infos2['residences_principales']) else 'N/A'}")
        st.write(f"Résidences secondaires : {int(infos2['residences_secondaires']) if pd.notna(infos2['residences_secondaires']) else 'N/A'}")
        st.write(f"Logements vacants : {int(infos2['logements_vacants']) if pd.notna(infos2['logements_vacants']) else 'N/A'}")


if sections["Tourisme"]:
    st.subheader("🗺️ Tourisme et découverte")

    col_tour1, col_tour2 = st.columns(2)

    with col_tour1:
        st.markdown(f"### {ville1}")
        st.markdown(f"[🔗 Wikipédia {ville1}]({infos1['url_wikipedia']})")

    with col_tour2:
        st.markdown(f"### {ville2}")
        st.markdown(f"[🔗 Wikipédia {ville2}]({infos2['url_wikipedia']})")


# --- Chargement des données Emploi détaillé ---
@st.cache_data
def charger_emploi_detaille():
    df = pd.read_csv("base-cc-caract_emp-2021.csv", sep=";", encoding="latin1", low_memory=False)
    df = df[["CODGEO", "P21_ACTOCC15P", "P21_SAL15P", "P21_NSAL15P"]]
    df.columns = ["code_insee", "actifs_total", "salaries", "non_salaries"]
    df[["actifs_total", "salaries", "non_salaries"]] = df[
        ["actifs_total", "salaries", "non_salaries"]
    ].apply(pd.to_numeric, errors="coerce")
    return df


emploi = charger_emploi_detaille()
emploi["code_insee"] = emploi["code_insee"].astype(str)
villes["code_insee"] = villes["code_insee"].astype(str)
villes = villes.merge(emploi, on="code_insee", how="left")

infos1 = villes[villes["nom_standard"] == ville1].iloc[0]
infos2 = villes[villes["nom_standard"] == ville2].iloc[0]

if sections["Statuts emploi"]:
    st.subheader("💼 Emploi : répartition des statuts")

    df_emploi = pd.DataFrame({
        "Indicateur": ["Actifs totaux", "Salariés", "Non-salariés"],
        ville1: [
            int(infos1["actifs_total"]) if pd.notna(infos1["actifs_total"]) else "N/A",
            int(infos1["salaries"]) if pd.notna(infos1["salaries"]) else "N/A",
            int(infos1["non_salaries"]) if pd.notna(infos1["non_salaries"]) else "N/A"
        ],
        ville2: [
            int(infos2["actifs_total"]) if pd.notna(infos2["actifs_total"]) else "N/A",
            int(infos2["salaries"]) if pd.notna(infos2["salaries"]) else "N/A",
            int(infos2["non_salaries"]) if pd.notna(infos2["non_salaries"]) else "N/A"
        ]
    })

    st.dataframe(df_emploi)

    import matplotlib.pyplot as plt

    labels = ["Salariés", "Non-salariés"]
    val1 = [infos1["salaries"], infos1["non_salaries"]]
    val2 = [infos2["salaries"], infos2["non_salaries"]]

    fig, ax = plt.subplots()
    x = range(len(labels))
    ax.bar(x, val1, width=0.35, label=ville1)
    ax.bar([i + 0.35 for i in x], val2, width=0.35, label=ville2)
    ax.set_xticks([i + 0.175 for i in x])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Nombre d’actifs")
    ax.set_title("Comparaison salariés / non-salariés")
    ax.legend()
    st.pyplot(fig)

@st.cache_data
def charger_logement():
    df = pd.read_csv("base-cc-logement-2021.csv", sep=";", encoding="latin1")

    # Vérification des types de données et de l'existence de valeurs manquantes
    df['P21_LOG'] = pd.to_numeric(df['P21_LOG'], errors='coerce')
    df['P21_RSECOCC'] = pd.to_numeric(df['P21_RSECOCC'], errors='coerce')
    df['P21_LOGVAC'] = pd.to_numeric(df['P21_LOGVAC'], errors='coerce')
    df['P21_MAISON'] = pd.to_numeric(df['P21_MAISON'], errors='coerce')
    df['P21_APPART'] = pd.to_numeric(df['P21_APPART'], errors='coerce')
    # Nettoyer les noms de colonnes en supprimant les espaces et caractères invisibles
    df.columns = df.columns.str.strip()

    # Suppression des lignes où une colonne essentielle a une valeur manquante
    df_cleaned = df.dropna(subset=['P21_LOG', 'P21_RSECOCC', 'P21_LOGVAC', 'P21_MAISON', 'P21_APPART'])
    
    # Afficher les 10 premières lignes pour vérifier
    print(df_cleaned.head())
    df = df[["CODGEO", "P21_RP", "P21_LOGVAC", "P21_RSECOCC", "P21_MAISON", "P21_APPART"]]
    df.columns = ["code_insee", "res_principales", "log_vacants", "res_secondaires", "maisons", "appartements"]
    df[["res_principales", "log_vacants", "res_secondaires", "maisons", "appartements"]] = df[
        ["res_principales", "log_vacants", "res_secondaires", "maisons", "appartements"]
    ].apply(pd.to_numeric, errors="coerce")
    return df


logement = charger_logement()
logement["code_insee"] = logement["code_insee"].astype(str)
villes["code_insee"] = villes["code_insee"].astype(str)
villes = villes.merge(logement, on="code_insee", how="left")

infos1 = villes[villes["nom_standard"] == ville1].iloc[0]
infos2 = villes[villes["nom_standard"] == ville2].iloc[0]

if sections["Logement"]:
    st.subheader("🏠 Données sur le logement")

    df_logement = pd.DataFrame({
        "Indicateur": [
            "Résidences principales",
            "Logements vacants",
            "Résidences secondaires",
            "Maisons",
            "Appartements"
        ],
        ville1: [
            infos1["res_principales"],
            infos1["log_vacants"],
            infos1["res_secondaires"],
            infos1["maisons"],
            infos1["appartements"]
        ],
        ville2: [
            infos2["res_principales"],
            infos2["log_vacants"],
            infos2["res_secondaires"],
            infos2["maisons"],
            infos2["appartements"]
        ]
    })
    st.dataframe(df_logement)


    import matplotlib.pyplot as plt

    labels = ["Maisons", "Appartements"]
    val1 = [infos1["maisons"], infos1["appartements"]]
    val2 = [infos2["maisons"], infos2["appartements"]]

    fig, ax = plt.subplots()
    x = range(len(labels))
    ax.bar(x, val1, width=0.35, label=ville1)
    ax.bar([i + 0.35 for i in x], val2, width=0.35, label=ville2)
    ax.set_xticks([i + 0.175 for i in x])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Nombre de logements")
    ax.set_title("🏠 Répartition entre maisons et appartements")
    ax.legend()
    st.pyplot(fig)


@st.cache_data
def charger_donnees_tourisme():
    df = pd.read_excel("base-cc-tourisme-2021-geo2021.xlsx", skiprows=5, engine="openpyxl")
    df = df[["CODGEO", "HT21", "HTCH21", "CPG21", "VV21", "RT21"]]
    df.columns = ["code_insee", "hotels", "chambres_hotel", "campings", "villages_vacances", "residences_tourisme"]
    df["code_insee"] = df["code_insee"].astype(str)
    df[["hotels", "chambres_hotel", "campings", "villages_vacances", "residences_tourisme"]] = df[
        ["hotels", "chambres_hotel", "campings", "villages_vacances", "residences_tourisme"]
    ].apply(pd.to_numeric, errors="coerce")
    return df


tourisme = charger_donnees_tourisme()
villes = villes.merge(tourisme, on="code_insee", how="left")

infos1 = villes[villes["nom_standard"] == ville1].iloc[0]
infos2 = villes[villes["nom_standard"] == ville2].iloc[0]

if sections["Tourisme capacité"]:
    st.subheader("🌍 Tourisme : capacité d'accueil")

    df_tourisme = pd.DataFrame({
        "Indicateur": [
            "Nombre d'hôtels",
            "Chambres d'hôtel",
            "Campings",
            "Villages vacances",
            "Résidences de tourisme"
        ],
        ville1: [
            infos1["hotels"],
            infos1["chambres_hotel"],
            infos1["campings"],
            infos1["villages_vacances"],
            infos1["residences_tourisme"]
        ],
        ville2: [
            infos2["hotels"],
            infos2["chambres_hotel"],
            infos2["campings"],
            infos2["villages_vacances"],
            infos2["residences_tourisme"]
        ]
    })

    st.dataframe(df_tourisme)

    # --- Graphe de comparaison touristique ---
    import matplotlib.pyplot as plt

    labels = ["Hôtels", "Campings", "Villages vacances", "Rés. tourisme"]
    val1 = [infos1["hotels"], infos1["campings"], infos1["villages_vacances"], infos1["residences_tourisme"]]
    val2 = [infos2["hotels"], infos2["campings"], infos2["villages_vacances"], infos2["residences_tourisme"]]

    fig, ax = plt.subplots()
    x = range(len(labels))
    ax.bar(x, val1, width=0.35, label=ville1)
    ax.bar([i + 0.35 for i in x], val2, width=0.35, label=ville2)
    ax.set_xticks([i + 0.175 for i in x])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Capacité")
    ax.set_title("Comparaison des capacités touristiques")
    ax.legend()
    st.pyplot(fig)


