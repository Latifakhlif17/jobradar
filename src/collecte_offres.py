import os
import requests
from dotenv import load_dotenv

# Charge les variables depuis le fichier .env (notamment JOOBLE_API_KEY)
load_dotenv()
API_KEY = os.getenv("JOOBLE_API_KEY")

# L'URL de l'API Jooble contient ta clé directement dans le chemin
URL = f"https://jooble.org/api/{API_KEY}"

def rechercher_offres(mots_cles, lieu="France", page=1):
    """Interroge l'API Jooble et renvoie la liste des offres trouvées."""
    corps_requete = {
        "keywords": mots_cles,
        "location": lieu,
        "page": page
    }

    reponse = requests.post(URL, json=corps_requete)
    reponse.raise_for_status()  # lève une erreur si la requête a échoué

    donnees = reponse.json()
    return donnees

import json

if __name__ == "__main__":
    mots_cles_a_tester = [
        "data analyst",
        "data scientist",
        "data engineer",
        "intelligence artificielle"
    ]

    offres_uniques = {}  # clé = id de l'offre, valeur = l'offre elle-même

    for mots_cles in mots_cles_a_tester:
        resultats = rechercher_offres(mots_cles)
        offres = resultats.get("jobs", [])
        print(f"Mots-clés : '{mots_cles}' → {len(offres)} offres reçues")

        for offre in offres:
            id_offre = offre.get("id")
            offres_uniques[id_offre] = offre  # écrase les doublons automatiquement

    print(f"\nTotal après dédoublonnage : {len(offres_uniques)} offres uniques")

    # Sauvegarde dans un fichier JSON
    with open("offres_brutes.json", "w", encoding="utf-8") as f:
        json.dump(list(offres_uniques.values()), f, ensure_ascii=False, indent=2)

    print("Fichier offres_brutes.json créé avec succès.")