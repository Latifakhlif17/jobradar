import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("JOOBLE_API_KEY")
URL = f"https://jooble.org/api/{API_KEY}"

def rechercher_offres(mots_cles, lieu="France", page=1):
    """Interroge l'API Jooble et renvoie la liste des offres trouvées."""
    corps_requete = {
        "keywords": mots_cles,
        "location": lieu,
        "page": page
    }
    reponse = requests.post(URL, json=corps_requete)
    reponse.raise_for_status()
    donnees = reponse.json()
    return donnees

if __name__ == "__main__":
    mots_cles_a_tester = [
        "data analyst",
        "data scientist",
        "data engineer",
        "intelligence artificielle",
        "machine learning",
        "business intelligence",
        "data visualisation",
        "BI analyst",
        "analyste de données",
        "ingénieur data",
        "scientifique des données",
        "analyste business intelligence",
        "Python data",
        "SQL data",
        "Power BI",
        "Tableau software",
        "AWS data",
        "Azure data",
        "Spark data",
        "data analyst alternance"
    ]

    offres_uniques = {}

    for mots_cles in mots_cles_a_tester:
        for page in range(1, 6):  # pages 1 à 5
            resultats = rechercher_offres(mots_cles, page=page)
            offres = resultats.get("jobs", [])
            print(f"Mots-clés : '{mots_cles}' (page {page}) → {len(offres)} offres reçues")
            if not offres:
                break  # si une page est vide, inutile de demander la suivante
            for offre in offres:
                id_offre = offre.get("id")
                if id_offre not in offres_uniques:
                    offres_uniques[id_offre] = offre

    print(f"\nTotal après dédoublonnage : {len(offres_uniques)} offres uniques")

    with open("offres_brutes.json", "w", encoding="utf-8") as f:
        json.dump(list(offres_uniques.values()), f, ensure_ascii=False, indent=2)

    print("Fichier offres_brutes.json créé avec succès.")