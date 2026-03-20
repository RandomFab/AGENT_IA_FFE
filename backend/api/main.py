from fastapi import FastAPI

from contextlib import asynccontextmanager
from backend.api.routes import router

from backend.services.rag_service import ingest_chess_openings_to_milvus, is_milvus_collection_exists

from config.config import WIKIPEDIA_OPENING_CHESS_URLS
from config.logger import logger

# --- Event handler de démarrage ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application (startup/shutdown)."""
   
    logger.info("🚀 Démarrage de l'application...")
    
    if not is_milvus_collection_exists():
        logger.info("📊 Chargement des données Milvus...")
        result = ingest_chess_openings_to_milvus(WIKIPEDIA_OPENING_CHESS_URLS)
        if result["status"] == "success":
            logger.info(f"✅ {result['inserted_count']} vecteurs chargés")
        else:
            logger.error(f"⚠️ Erreur lors du chargement: {result['error']}")
    else:
        logger.info("✅ Données Milvus déjà chargées, skip initialisation")
    
    yield  


# --- Configuration FastAPI ---

tags_metadata = [
    {
        "name": "Health",
        "description": "Vérification de l'état du service",
    },
    {
        "name": "move_evaluation",
        "description": "Accès à la base théorique Lichess et a l'evaluation stockfish",
    },
    {
        "name": "retrieve",
        "description": "Videos youtube et articles wikipedia sur les ouvertures",
    },
        {
        "name": "Agent",
        "description": "Agent intelligent d'analyse d'échecs",
    },
]


# --- Creation FastAPI ---

api = FastAPI(
    title="FFE Chess Analysis API",
    description="API d'analyse d'échecs avec accès à la base théorique et moteur d'analyse",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)


# --- Health endpoints ---

@api.get("/api/v1/", tags=["Health"])
def root():
    """Endpoint racine de l'API."""
    return {"message": "Hello FFE"}


@api.get("/api/v1/health", tags=["Health"])
def health():
    """Vérifie l'état de santé de l'API."""
    return {"message": "Api is healthy"}


# --- Service endpoint ---

api.include_router(router)

