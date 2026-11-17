# Journal d'apprentissage – JobRadar

## 17/11/2026 – Étape 0 : environnement
**Ce que j'ai fait :** installé Git, créé le dépôt GitHub, cloné le projet, créé l'environnement virtuel.

**Ce que j'ai compris :**
- Git = un logiciel de gestion de versions, installé sur mon PC. Il garde l’historique de toutes les modifications (les commits) et permet de revenir en arrière.
- GitHub = un site en ligne qui héberge les dépôts Git. Il sert à sauvegarder le code en ligne, à le partager et à travailler en équipe. Mon dépôt est public pour que les recruteurs puissent le voir.
- Cloner = 
- Environnement virtuel = une bulle isolée propre à chaque projet, avec son Python et ses bibliothèques. Ça évite les conflits de versions entre projets.

## Étape 1 — Collecte des données (17/11/2026)

### Contexte : pivot d'API
Le plan initial prévoyait d'utiliser l'API "Offres d'emploi v2" de France Travail.
En essayant de m'y abonner sur francetravail.io, j'ai découvert que cette API a été
retirée du catalogue en libre-service (plus aucune souscription possible, erreur 403).
Ce n'était pas une erreur de ma part : l'accès a été fermé côté France Travail.

→ Pivot vers l'API Jooble (agrégateur d'offres d'emploi, gratuit, sans carte bancaire,
inscription par formulaire avec validation manuelle, clé reçue par email en quelques heures).

Notion apprise : en vrai projet, une dépendance externe (API tierce) peut disparaître ou
changer sans prévenir. Savoir pivoter rapidement vers une alternative est une compétence
en soi (à mentionner en entretien).

### Sécurisation de la clé API
- Création du fichier `.env` à la racine du projet, contenant `JOOBLE_API_KEY=...`
- Ce fichier est listé dans `.gitignore`, donc Git ne le suit jamais (vérifié avec
  `git status` : le fichier n'apparaît pas dans les modifications).
- Dans le code, la clé est lue avec `python-dotenv` (`load_dotenv()` + `os.getenv(...)`),
  jamais écrite en dur.

Pourquoi c'est important : si la clé était codée en dur dans un fichier `.py` et poussée
sur GitHub, n'importe qui pourrait la récupérer et l'utiliser à ma place (vol de quota,
voire facturation si l'API devient payante). C'est une question classique en entretien
("comment gères-tu les secrets ?").

### Script `src/collecte_offres.py`
Fonction principale : `rechercher_offres(mots_cles, lieu, page)`
- Construit un corps de requête JSON : `{"keywords": ..., "location": ..., "page": ...}`
- Envoie une requête **POST** à `https://jooble.org/api/{ma_cle}` avec la librairie `requests`
- `reponse.raise_for_status()` : fait planter le script immédiatement si l'API renvoie une
  erreur (clé invalide, quota dépassé...), plutôt que de continuer silencieusement avec
  des données vides ou corrompues.
- `reponse.json()` : convertit la réponse HTTP (texte brut au format JSON) en dictionnaire
  Python directement exploitable.

### Découverte : les mots-clés ne supportent pas le "OR" booléen
Premier essai avec `"data analyst OR data scientist OR data engineer"` → seulement 3 résultats.
Jooble traite cette chaîne littéralement (recherche du texte exact), pas comme un opérateur
logique. Solution : faire une requête séparée par mot-clé, puis fusionner les résultats
côté Python.

### Fusion et dédoublonnage
- 4 requêtes séparées : "data analyst" (16), "data scientist" (29), "data engineer" (8),
  "intelligence artificielle" (30) → 83 résultats bruts au total.
- Une même offre peut apparaître sous plusieurs mots-clés (ex: une offre "Data Scientist IA"
  matche à la fois "data scientist" et "intelligence artificielle").
- Technique de dédoublonnage : dictionnaire Python `offres_uniques = {}` où la clé est
  l'`id` unique de l'offre. Quand on réaffecte `offres_uniques[id] = offre`, Python écrase
  automatiquement l'entrée existante si l'id existe déjà → résultat final sans doublons.
- Résultat : **51 offres uniques** sur les 83 reçues (32 doublons supprimés).

Notion apprise : dédoublonnage de données, une tâche très courante en data engineering/analyse,
ici réalisée avec une structure de données simple (dictionnaire) plutôt qu'une librairie lourde.

### Sauvegarde
Les 51 offres uniques sont sauvegardées dans `offres_brutes.json` via le module `json`
de Python (`json.dump(..., ensure_ascii=False, indent=2)`) :
- `ensure_ascii=False` : garde les accents français lisibles dans le fichier au lieu de
  les encoder en `\uXXXX`.
- `indent=2` : formate le JSON de façon lisible (utile pour inspecter le fichier à l'œil).

### Prochaine étape
Stocker ces données de façon plus robuste (base de données plutôt que fichier JSON),
avant de passer au nettoyage avec pandas (étape 2).

## Étape 1 (suite) — Stockage dans PostgreSQL

- Création de la base `jobradar` et de la table `offres` dans pgAdmin
  (colonnes : id, titre, entreprise, lieu, lien, date_collecte)
- `id` en clé primaire → empêche les doublons directement au niveau de la base
- Script `stocker_offres.py` : lit offres_brutes.json et insère chaque offre
  via psycopg2, avec ON CONFLICT (id) DO NOTHING pour ignorer les doublons
- Pipeline en 2 scripts séparés (collecte puis stockage), pas encore automatisé
- Notion apprise : séparer collecte et stockage est une bonne pratique en
  data engineering ; prochaine étape = automatiser l'enchaînement (GitHub Actions)