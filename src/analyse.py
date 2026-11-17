import os
import re
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connexion_bdd():
    """Ouvre une connexion vers la base PostgreSQL (Supabase)."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def charger_offres():
    """Charge toutes les offres de la table 'offres' dans un DataFrame pandas."""
    conn = connexion_bdd()
    df = pd.read_sql("SELECT * FROM offres;", conn)
    conn.close()
    return df

def nettoyer_html(texte):
    """Enlève les balises HTML (<b>, &nbsp;, etc.) d'un texte."""
    if pd.isna(texte):
        return texte
    texte = re.sub(r"<.*?>", " ", texte)      # enlève les balises comme <b> ou </b>
    texte = texte.replace("&nbsp;", " ")      # enlève les espaces insécables HTML
    return texte

if __name__ == "__main__":
    df = charger_offres()

    # Nettoyage de type_contrat
    df["type_contrat"] = df["type_contrat"].replace("", pd.NA)
    df["salaire"] = df["salaire"].replace("", pd.NA)
    df["type_contrat"] = df["type_contrat"].fillna("Non précisé")

    print("\n--- Répartition de 'type_contrat' après nettoyage ---")
    print(df["type_contrat"].value_counts())

    # Nettoyage du HTML dans les descriptions
    df["description_propre"] = df["description"].apply(nettoyer_html)

    print("\n--- Exemples de descriptions nettoyées ---")
    for texte in df["description_propre"].dropna().head(3):
        print(texte)
        print("---")

    # Analyse des compétences demandées, avec \b pour matcher le mot entier
    competences = ["Python", "SQL", "Excel", "Power BI", "Tableau", "Machine Learning", "AI", "LLM", "Java"]

    print("\n--- Fréquence des compétences dans les descriptions ---")
    for competence in competences:
        motif = r"\b" + re.escape(competence) + r"\b"
        nb_offres = df["description_propre"].str.contains(motif, case=False, na=False, regex=True).sum()
        print(f"{competence} : {nb_offres} offres sur {len(df)}")

    print("\n--- Répartition par ville/lieu ---")
    print(df["lieu"].value_counts().head(10))

    mots_titre = ["Senior", "Junior", "Lead", "Data Scientist", "Data Engineer", "Data Analyst", "Manager"]

    print("\n--- Fréquence dans les titres de poste ---")
    for mot in mots_titre:
        motif = r"\b" + re.escape(mot) + r"\b"
        nb_offres = df["titre"].str.contains(motif, case=False, na=False, regex=True).sum()
        print(f"{mot} : {nb_offres} offres sur {len(df)}")