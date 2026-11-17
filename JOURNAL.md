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

  ## Étape 1 (suite) — Migration cloud et automatisation

- Migration de la base PostgreSQL locale vers Supabase (hébergement cloud gratuit,
  sans carte bancaire) : nécessaire car GitHub Actions ne peut pas accéder à une
  base tournant sur mon PC local (localhost)
- Connexion via le "Session pooler" de Supabase (IPv4) plutôt que la connexion
  directe (IPv6) — évite un add-on payant
- Secrets (clé Jooble + identifiants base de données) stockés dans GitHub Secrets,
  jamais en clair dans le code ni dans le dépôt
- Création du workflow GitHub Actions (.github/workflows/collecte_quotidienne.yml) :
  s'exécute tous les jours à 7h UTC (cron), + déclenchement manuel possible
  (workflow_dispatch)
- Premier run manuel réussi : collecte + stockage en 34 secondes, 100% automatisé,
  sans intervention de mon PC
- Notion apprise : CI/CD basique — une machine éphémère dans le cloud exécute du
  code selon un calendrier, sans jamais toucher à l'infrastructure personnelle

  ## Étape 2 — Nettoyage des données et premières analyses avec pandas

### Chargement des données
J'ai écrit `src/analyse.py`, qui se connecte à Supabase (même logique de connexion que `stocker_offres.py`) et charge toute la table `offres` dans un DataFrame pandas avec `pd.read_sql()`. Ça donne un tableau de 57 lignes et 9 colonnes manipulable directement en Python, plutôt que de boucler ligne par ligne comme avec psycopg2 seul.

### Nettoyage de type_contrat
J'ai découvert que les valeurs manquantes étaient représentées de deux façons différentes dans mes données : `NaN` (vraiment aucune info, vient des offres jamais enrichies) et `''` chaîne vide (vient de Jooble qui ne fournit pas toujours cette info). J'ai uniformisé les deux avec `.replace("", pd.NA)` puis `.fillna("Non précisé")`, pour avoir une seule catégorie claire. Résultat : 48 "Full-time", 8 "Non précisé", 1 "Temporary".

### Limite découverte : le champ salaire
Seulement 3 offres sur 57 ont un vrai salaire renseigné (le reste est vide ou absent). Pas assez de données pour faire une analyse salaire-par-ville fiable. J'ai documenté cette limite plutôt que de forcer une conclusion non fiable sur 3 valeurs.

### Nettoyage HTML dans les descriptions
Les descriptions (le champ "snippet" de Jooble) contenaient des balises HTML (`<b>`, `&nbsp;`) mélangées au texte. J'ai écrit une fonction `nettoyer_html()` avec le module `re` (expressions régulières) pour les enlever, en gardant le texte brut original dans une colonne séparée (`description_propre`) — bonne pratique : ne jamais écraser la donnée source.

### Analyse des compétences demandées
J'ai cherché des mots-clés techniques (Python, SQL, Power BI...) dans les descriptions avec `.str.contains()`. Piège rencontré : chercher "AI" sans limite de mot (`\b`) donnait des faux positifs (le mot "detail" contient "ai"). Corrigé avec une regex `\bAI\b`. Limite découverte : le "snippet" Jooble est trop court pour contenir la plupart des outils techniques précis — seul "AI" ressort beaucoup, car c'est un des mots-clés de recherche utilisés dès la collecte.

### Limite découverte : le champ lieu
Le champ `lieu` vaut "France" pour les 57 offres, sans ville précise — Jooble ne renvoie pas toujours une localisation détaillée. Les vraies villes (ex: "Grenoble", "Dunkirk") apparaissent parfois dans le texte libre de la description, mais pas dans le champ structuré. Analyse géographique abandonnée faute de données exploitables.

### Analyse des titres de poste
J'ai cherché des mots-clés (Senior, Junior, Lead, Data Scientist...) dans les titres. Résultat : 11 "Senior", 0 "Junior", 4 "Lead", 9 "Manager". Mais "Data Scientist"/"Data Engineer"/"Data Analyst" ressortent très peu (2, 0, 0) car les titres réels varient beaucoup dans leur formulation (ex: "Senior Quantitative Analyst" est un métier data mais ne contient aucun de ces mots exacts). Leçon : la recherche par mot-clé exact a des limites pour capturer la diversité du langage naturel.

### Compétence clé retenue de cette étape
Savoir documenter les limites des données (sparse, imprécises, formulées différemment) est aussi important que produire des chiffres — ça montre une analyse rigoureuse plutôt qu'une conclusion forcée.