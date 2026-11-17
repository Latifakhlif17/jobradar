import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connexion_bdd():
    """Ouvre une connexion vers la base PostgreSQL jobradar."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def inserer_offres(chemin_json):
    """Lit le fichier JSON et insère chaque offre dans la table 'offres'."""
    with open(chemin_json, "r", encoding="utf-8") as f:
        offres = json.load(f)

    conn = connexion_bdd()
    cur = conn.cursor()  # le "curseur" : l'objet qui exécute les requêtes SQL

    nb_inserees = 0
    for offre in offres:
        cur.execute(
            """
            INSERT INTO offres (id, titre, entreprise, lieu, lien)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                offre.get("id"),
                offre.get("title"),
                offre.get("company"),
                offre.get("location"),
                offre.get("link"),
            )
        )
        if cur.rowcount > 0:
            nb_inserees += 1

    conn.commit()  # valide définitivement les changements dans la base
    cur.close()
    conn.close()

    print(f"{nb_inserees} nouvelles offres insérées dans la base.")

if __name__ == "__main__":
    inserer_offres("offres_brutes.json")