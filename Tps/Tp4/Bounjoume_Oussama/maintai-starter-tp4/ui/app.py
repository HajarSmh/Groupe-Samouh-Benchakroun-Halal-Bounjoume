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
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
    c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

    variable = st.selectbox("Variable", FEATURES)
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True).failure.mean()
    taux.index = [round(i.mid) for i in taux.index]  # le milieu de chaque tranche
    st.subheader(f"Taux de panne selon {variable}")
    st.bar_chart(taux)

    st.subheader("Température et vibration (500 relevés)")
    echantillon = df.sample(500, random_state=0).assign(panne=lambda d: d.failure.map({0: "non", 1: "oui"}))
    st.scatter_chart(echantillon, x="temperature_c", y="vibration_mm_s", color="panne")

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
        try:
            res = MaintaiClient(url, api_key=cle).predict(releve)
        except APIError as e:
            st.warning(f"Erreur {e.status_code} : {e.detail}")
        except httpx.HTTPError:
            st.error("API injoignable : uvicorn est-il lancé ?")
        else:
            pct = round(res["failure_probability"] * 100)
            st.metric("Probabilité de panne", f"{pct} %")
            if res["alert"]:
                st.error(f"ALERTE : au-dessus du seuil {res['threshold']}")
            else:
                st.success(f"Normal : sous le seuil {res['threshold']}")
