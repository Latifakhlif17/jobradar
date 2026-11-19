import re
import streamlit as st
import pandas as pd
from analyse import charger_offres, nettoyer_html

st.set_page_config(page_title="JobRadar - Dashboard", layout="wide")

st.title("📊 JobRadar — Analyse du marché data/IA en France")

df = charger_offres()

# On réapplique le même nettoyage que dans analyse.py
df["type_contrat"] = df["type_contrat"].replace("", pd.NA).fillna("Non précisé")
df["description_propre"] = df["description"].apply(nettoyer_html)

st.metric("Nombre total d'offres collectées", len(df))

st.subheader("Répartition par type de contrat")
st.bar_chart(df["type_contrat"].value_counts())

competences = ["Python", "SQL", "Excel", "Power BI", "Tableau", "Machine Learning", "AI", "LLM", "Java"]
resultats = {}
for competence in competences:
    motif = r"\b" + re.escape(competence) + r"\b"
    resultats[competence] = df["description_propre"].str.contains(motif, case=False, na=False, regex=True).sum()

st.subheader("Compétences mentionnées dans les descriptions")
st.bar_chart(pd.Series(resultats))