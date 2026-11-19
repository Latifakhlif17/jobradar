import re
import streamlit as st
import pandas as pd
import altair as alt
from analyse import charger_offres, nettoyer_html

st.set_page_config(page_title="JobRadar - Dashboard", layout="wide")

st.markdown("# JobRadar")
st.markdown("##### Analyse du marché de l'emploi data / IA en France")
st.divider()

df = charger_offres()

df["type_contrat"] = df["type_contrat"].replace("", pd.NA).fillna("Non précisé")
df["description_propre"] = df["description"].apply(nettoyer_html)

col1, col2, col3 = st.columns(3)
col1.metric("Offres collectées", len(df))
col2.metric("Entreprises distinctes", df["entreprise"].nunique())
col3.metric("Dernière collecte", df["date_collecte"].max().strftime("%d/%m/%Y"))

st.divider()

def graphique_barres(series, titre):
    """Construit un graphique en barres stylisé à partir d'une pandas Series."""
    data = series.reset_index()
    data.columns = ["categorie", "valeur"]
    chart = (
        alt.Chart(data)
        .mark_bar(color="#0F766E", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("categorie:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-30)),
            y=alt.Y("valeur:Q", title="Nombre d'offres"),
            tooltip=["categorie", "valeur"]
        )
        .properties(height=350)
    )
    st.subheader(titre)
    st.altair_chart(chart, use_container_width=True)

graphique_barres(df["type_contrat"].value_counts(), "Répartition par type de contrat")

competences = ["Python", "SQL", "Excel", "Power BI", "Tableau", "Machine Learning", "AI", "LLM", "Java"]
resultats_comp = {}
for competence in competences:
    motif = r"\b" + re.escape(competence) + r"\b"
    resultats_comp[competence] = df["description_propre"].str.contains(motif, case=False, na=False, regex=True).sum()
graphique_barres(pd.Series(resultats_comp), "Compétences mentionnées dans les descriptions")

mots_titre = ["Senior", "Junior", "Lead", "Manager", "Data Scientist", "Data Engineer", "Data Analyst"]
resultats_titre = {}
for mot in mots_titre:
    motif = r"\b" + re.escape(mot) + r"\b"
    resultats_titre[mot] = df["titre"].str.contains(motif, case=False, na=False, regex=True).sum()
graphique_barres(pd.Series(resultats_titre), "Niveaux et types de postes (d'après les titres)")

st.divider()
st.subheader("Dernières offres collectées")
colonnes_a_afficher = ["titre", "entreprise", "type_contrat", "date_collecte"]
st.dataframe(
    df[colonnes_a_afficher].sort_values("date_collecte", ascending=False).head(10),
    use_container_width=True,
    hide_index=True
)