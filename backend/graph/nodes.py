# --- import ---
from graph.state import AgentState
from services.lichess_service import evaluate_opening
from services.stockfish_service import evaluate_position
from services.rag_service import retrieve_articles
from services.youtube_service import get_ytb_video
from services.format_service import format_llm_response
from schemas.lichess_schema import LichessOpeningWithGamesResponse
from schemas.stockfish_schema import StockfishEvaluationResponse

from config.logger import logger

# --- Lichess Node ---

def node_lichess(state: AgentState):
    """
    Nœud de consultation de la base théorique Lichess.
    Récupère les coups connus pour une position donnée.
    """
    fen = state["fen"]
    logger.info(f"[NODE LICHESS] Début - FEN: {fen[:50]}...")

    try:
        # Appel au service Lichess
        logger.debug("[NODE LICHESS] Appel du service Lichess...")
        raw_data = evaluate_opening(fen)
        logger.debug(f"[NODE LICHESS] Réponse brute reçue: {type(raw_data)}")

        # Validation de la réponse avec le schéma Pydantic
        logger.debug(
            "[NODE LICHESS] Validation de la réponse avec LichessOpeningWithGamesResponse..."
        )
        validated_response = LichessOpeningWithGamesResponse(**raw_data)

        # Gestion des erreurs (position non trouvée)
        if validated_response.status == 404 or validated_response.error:
            logger.warning(f"[NODE LICHESS] ⚠️ Position non trouvée: {validated_response.error}")
            return {"lichess_evaluation": None}

        # Extraction du nom de l'ouverture si détecté 
        opening_name = validated_response.opening.name if validated_response.opening else None
        if opening_name:
            logger.info(f"[NODE LICHESS] ✓ Succès - Théorie trouvée: {opening_name}")
            return {"lichess_evaluation": opening_name}
        else:
            logger.warning("[NODE LICHESS] ⚠️ Aucun coup disponible")
            return {"lichess_evaluation": None}

    except Exception as e:
        logger.error(f"[NODE LICHESS] ✗ Erreur validation: {str(e)}")
        logger.warning("[NODE LICHESS] Falling back vers Stockfish...")
        return {"lichess_evaluation": None}


# --- Stockfish Node ---

def node_stockfish(state: AgentState):
    """
    Nœud d'analyse via Stockfish.
    Appelé quand la base théorique Lichess n'a rien trouvé.
    """
    fen = state["fen"]
    logger.info(f"[NODE STOCKFISH] Début - FEN: {fen[:50]}...")

    try:
        # Appel au service Stockfish (profondeur fixée à 10 pour le POC)
        logger.debug("[NODE STOCKFISH] Appel du service Stockfish avec depth=10...")
        raw_data = evaluate_position(fen=fen, depth=10)
        logger.debug(f"[NODE STOCKFISH] Réponse brute reçue: {type(raw_data)}")

        # Gestion de l'erreur retournée par l'API
        if "error" in raw_data:
            logger.warning(
                f"[NODE STOCKFISH] API a retourné une erreur: {raw_data.get('error')}"
            )
            return {"stockfish_evaluation": None}

        # Validation de la réponse avec le schéma Pydantic
        logger.debug(
            "[NODE STOCKFISH] Validation de la réponse avec StockfishEvaluationResponse..."
        )
        validated_response = StockfishEvaluationResponse(**raw_data)

        # Extraction du meilleur coup
        best_move = validated_response.continuation
        logger.info(f"[NODE STOCKFISH] ✓ Succès - Coup analysé: {best_move}")

        best_move_cp = validated_response.evaluation
        logger.info(f"[NODE STOCKFISH] Evaluation du coup : {best_move_cp} cp(s)")

        return {"stockfish_evaluation": {"move" : best_move, "cp" : best_move_cp}}

    except ValueError as e:
        logger.error(f"[NODE STOCKFISH] ✗ Erreur validation (ValueError): {str(e)}")
        return {"stockfish_evaluation": None}
    except Exception as e:
        logger.error(f"[NODE STOCKFISH] ✗ Erreur inattendue: {str(e)}", exc_info=True)
        return {"stockfish_evaluation": None}

# --- Articles Node ---

def node_wikipedia_search(state: AgentState):
    """
    Nœud de recherche RAG pour enrichir l'analyse avec des articles Wikipedia.
    Utilise l'évaluation Lichess ou Stockfish comme requête de recherche.
    """
    logger.info("[NODE WIKIPEDIA] Début de recherche RAG...")
    
    try:
        # Déterminer le texte de recherche (priorité: Lichess, sinon Stockfish)
        search_query = state.get("lichess_evaluation")
        
        if not search_query:
            logger.warning("[NODE WIKIPEDIA] ⚠️ Aucune évaluation disponible pour la recherche")
            return {"articles_context": None}
        
        logger.debug(f"[NODE WIKIPEDIA] Requête de recherche: {str(search_query)[:50]}...")
        
        # Rechercher les articles similaires
        results = retrieve_articles(search_query, limit=5)
        
        if results:
            # Convertir les objets Pydantic en dicts pour le state
            articles_as_dicts = [article.model_dump() for article in results]
            logger.info(f"[NODE WIKIPEDIA] ✓ {len(articles_as_dicts)} articles trouvés")
            return {"articles_context": articles_as_dicts}
        else:
            logger.warning("[NODE WIKIPEDIA] ⚠️ Aucun article trouvé")
            return {"articles_context": None}
    
    except Exception as e:
        logger.error(f"[NODE WIKIPEDIA] ✗ Erreur recherche RAG: {str(e)}")
        return {"articles_context": None}


# --- Videos Node ---

def node_youtube_search(state: AgentState):
    """
    Nœud de recherche youtube pour enrichir l'analyse avec des videos
    Utilise l'évaluation d'ouverture Lichess comme requête de recherche.
    """
    logger.info("[NODE YOUTUBE] Début de recherche youtube...")
    
    try:
        # Déterminer le texte de recherche (priorité: Lichess, sinon Stockfish)
        search_query = state.get("lichess_evaluation")
        
        if not search_query:
            logger.warning("[NODE YOUTUBE] ⚠️ Aucune évaluation disponible pour la recherche")
            return {"videos_context": None}
        
        logger.debug(f"[NODE YOUTUBE] Requête de recherche: {str(search_query)[:50]}...")
        
        # Rechercher les vidéos
        results = get_ytb_video(search_query, max_results=3)
        
        if results:
            # Convertir les objets Pydantic en dicts pour le state
            videos_as_dicts = [video.model_dump() for video in results]
            logger.info(f"[NODE YOUTUBE] ✓ {len(videos_as_dicts)} vidéos trouvées")
            return {"videos_context": videos_as_dicts}
        else:
            logger.warning("[NODE YOUTUBE] ⚠️ Aucune vidéo trouvée")
            return {"videos_context": None}
    
    except ValueError as e:
        logger.error(f"[NODE YOUTUBE] ✗ Erreur configuration: {str(e)}")
        return {"videos_context": None}
    except (TimeoutError, ConnectionError) as e:
        logger.error(f"[NODE YOUTUBE] ✗ Erreur connexion YouTube: {str(e)}")
        return {"videos_context": None}
    except Exception as e:
        logger.error(f"[NODE YOUTUBE] ✗ Erreur recherche YouTube: {str(e)}")
        return {"videos_context": None}
    

# --- Fromatter Node ---

def node_format_response(state: AgentState):
    """Formate la réponse final avec un LLM."""
    logger.info("[NODE FORMATTER] Début de formatage avec LLM")
    
    try:
        final_answer = format_llm_response(state)
        logger.info(f"[NODE FORMATTER] ✓ Réponse formatée")
        return {"final_answer": final_answer}
    except Exception as e:
        logger.error(f"[NODE FORMATTER] ✗ Erreur: {str(e)}")
        # Fallback ultra-simple
        return {"final_answer": "Erreur lors de la génération de la réponse"}