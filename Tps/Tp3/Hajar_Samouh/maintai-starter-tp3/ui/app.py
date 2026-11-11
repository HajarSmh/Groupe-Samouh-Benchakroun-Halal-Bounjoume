"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.

Lancement (depuis la racine du projet) : python -m streamlit run ui/app.py
"""
import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings

st.set_page_config(page_title="MaintAI", page_icon="🔧")
st.title("MaintAI · prédiction de panne")


@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lu une seule fois : Streamlit relance tout le script à chaque clic
    return pd.read_csv(path)


with st.sidebar:
    url = st.text_input("URL de l'API", "http://localhost:8000")
    cle = st.text_input("Clé API", type="password")

onglet_donnees, onglet_prediction = st.tabs(["Données", "Prédiction"])

# Sprint 1 : explorer les données
with onglet_donnees:
    df = charger(get_settings().data_path)
    # TODO TP3 sprint 1 :
    #   1. trois indicateurs côte à côte (st.columns, puis .metric) :
    #      le nombre de relevés, le taux de panne (df.failure.mean()), la température moyenne
    #   2. une liste déroulante (st.selectbox) pour choisir une variable parmi FEATURES
    #   3. le taux de panne par tranche de cette variable (pd.cut, groupby), en barres (st.bar_chart)
    #   4. un nuage de points température / vibration, coloré par panne (st.scatter_chart)
    st.info("Sprint 1 : les indicateurs et les graphiques viendront ici.")


# Sprint 2 : demander une prédiction à l'API
with onglet_prediction:
    with st.form("releve"):
        releve = {
            "temperature_c": st.slider("Température (°C)", -40.0, 150.0, 72.0),
            "vibration_mm_s": st.slider("Vibration (mm/s)", 0.0, 50.0, 6.0),
            "load_pct": st.slider("Charge (%)", 0.0, 100.0, 85.0),
            "runtime_hours": st.number_input("Heures de fonctionnement", 0, 100_000, 15000),
        }
        envoye = st.form_submit_button("Prédire")

    if envoye:
        # TODO TP3 sprint 2 :
        #   1. créer MaintaiClient(url, api_key=cle) et appeler .predict(releve)
        #   2. APIError → st.warning avec le code et le message ; httpx.HTTPError → st.error("API injoignable ...")
        #   3. sinon : st.metric("Probabilité de panne", f"{pct} %"), puis st.error (alerte) ou st.success (normal)
        st.info("Sprint 2 : la prédiction s'affichera ici.")
