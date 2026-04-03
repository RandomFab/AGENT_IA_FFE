# I. SOLUTIONS TECHNIQUES
## a - BRIQUES TECHNIQUE
- ### Ingestion de la donnée
    1. Source : API YouTube (ou autre plateforme)
    2. Workers de téléchargement & d'extraction : Téléchargent la vidéo et extraient des images (ex: 1 image toutes les secondes avec FFmpeg)
    3. Moteur d'inférence (Vision) : Un modèle (type YOLO pour trouver l'échiquier + un réseau de neurones convolutifs pour identifier les pièces) analyse l'image et génère la chaîne FEN.
    4. Logique de déduplication : Si la FEN à la seconde $T$ est identique à $T+1$, on fusionne le segment.
    5. Base de données (Index) : On stocke : FEN | URL_Vidéo | Timestamp_Début | Timestamp_Fin.

- ### Accès à la donnée
    1. Le Serveur MCP (La couche de recherche en temps réel) :
    2. Client MCP (L'application utilisateur) : L'utilisateur demande à ton IA : "Trouve-moi des vidéos sur cette position [FEN]".
    3. L'hôte / LLM : L'IA comprend la demande et utilise le standard MCP pour interroger ton outil.
    4. Serveur MCP : C'est une petite API que tu exposes. Elle contient un outil (une tool) par exemple nommée search_video_by_fen(fen_string).
    5. Exécution : Le serveur MCP interroge la Base de Données (créée à l'étape A) et renvoie à l'IA les liens YouTube avec les timestamps précis (ex: https://youtube.com/watch?v=...&t=124s).
    6. Réponse : L'IA synthétise la réponse et affiche la vidéo à l'utilisateur.

## b - SOLUTIONS
- ### Solution 1 : INGESTION BATCH
    1. Liste de videos prédéfinies selon les ouvertures les plus connues
    2. Analyse de cette liste de videos pour construire une base de donnée 
    3. Serveur MCP recherche dans la BDD fixe

- ### Solution 2 : INGESTION A LA DEMANDE
    1. Identification du nom d'ouverture selon une position FEN
    2. Recherche des vidéos youtubes concernées par l'ouverture
    3. Analyse de images
    4. Retrieve des séquences les plus pertinentes (MCP)

- ### Pourquoi la solution 1 ?
    1. Ne s'arrete pas au ouvertures connues
    2. Analyse des vidéos de tout type : cours, match officiel, parties en ligne commentées
    3. Temps d'inférence réduit
    4. Pas de recherches doublon

# II. BENEFICES & LIMITES
## a - BENEFICES
- ### Vidéo brute → BDD structuré
    Au lieu de forcer l'utilisateur à chercher manuellement dans une vidéo de 45 minutes, le système l'amène à la seconde exacte où la position d'échecs (ou l'ouverture) qui l'intéresse apparaît. L'apprentissage est immédiat.
- ### Gain de temps
    Vous transformez des milliers d'heures de vidéos brutes en une base de données hautement structurée et interrogeable par le contenu de l'image, et non plus seulement par le titre ou la description.
- ### Avantage concurentiel
    C'est une fonctionnalité de niche très experte. Cela positionne l'application comme un véritable assistant d'échecs, surpassant les moteurs de recherche traditionnels.
- ### Multilingue
    La notation FEN est universelle. Un utilisateur français peut trouver l'explication parfaite d'une position dans une vidéo en russe ou en anglais sans même s'en rendre compte.

## b - LIMITES
- ### Modèle de vision
    - Occlusion → main devant l'échiquier
    - Qualité de la vidéo
    - Angle d'enregistrement
    - Design des pièces d'échec
    - Transition = positions invalides
- ### Coût et temps de calcul
    Analyser chaque frame (ou même 1 frame par seconde) de milliers de vidéos représente une puissance de calcul colossale (nécessitant des GPU).
- ### Légalité
    Télécharger en masse et traiter des vidéos YouTube peut violer les Conditions d'Utilisation (ToS) de YouTube et poser des problèmes de droits d'auteur, même si l'on ne stocke pas la vidéo finale.
- ### Redondance
    Si une position reste à l'écran pendant 10 minutes, le système va extraire la même FEN 600 fois. Il faut une logique pour regrouper ces timestamps en segments continus.


# III. FAISABILITE & COUTS
## a - CAPEX
- ### Roles nécessaires
- ### Création du dataset
- ### Développement de l'infrastructure
    Mise en place des pipelines de données et développement du Serveur MCP.
## b - OPEX
- ### Coût d'ingestion €/minute de vidéo
- ### Coût API YOUTUBE
- ### Coût hébergement serveur MCP
- ### Coût stockage BDD : | FEN | TimeStamp | Lien youtube |
## c - PHASES DE DEVELOPPEMENT
### PHASE 1 : QuickWins
    Au lieu d'utiliser la vision par ordinateur, parser automatiquement les descriptions des vidéos YouTube ou les commentaires épinglés. Beaucoup de créateurs y mettent les fichiers PGN (Portable Game Notation) avec les chapitres. C'est beaucoup moins cher et 100% fiable.
### PHASE 2 : ScreenCast only
    Restreindre le système uniquement aux vidéos de type "Screencast" (où l'échiquier est en 2D sur un écran d'ordinateur, comme sur Chess.com ou Lichess). La détection est presque parfaite avec OpenCV de base, sans IA lourde.
### PHASE 3 : Recorded games
    Étendre aux vidéos de tournois réels (3D) une fois la rentabilité de la Phase 1 prouvée.