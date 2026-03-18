# --- import ---
from backend.graph.state import AgentState
from backend.services.lichess_service import evaluate_opening
from backend.services.stockfish_service import evaluate_position
from backend.schemas.lichess_schema import LichessEvaluationResponse
from backend.schemas.stockfish_schema import StockfishEvaluationResponse
from backend.services.rag_service import retrieve_articles

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
            "[NODE LICHESS] Validation de la réponse avec LichessEvaluationResponse..."
        )
        validated_response = LichessEvaluationResponse(**raw_data)

        # Extraction du meilleur coup
        best_move = validated_response.pvs[0].moves
        logger.info(f"[NODE LICHESS] ✓ Succès - Théorie trouvée: {best_move}")

        return {"lichess_evaluation": best_move}

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

        return {"stockfish_evaluation": best_move}

    except ValueError as e:
        logger.error(f"[NODE STOCKFISH] ✗ Erreur validation (ValueError): {str(e)}")
        return {"stockfish_evaluation": None}
    except Exception as e:
        logger.error(f"[NODE STOCKFISH] ✗ Erreur inattendue: {str(e)}", exc_info=True)
        return {"stockfish_evaluation": None}

# --- Milvus Node ---

def node_wikipedia_search(state: AgentState):
    """
    Nœud de recherche RAG pour enrichir l'analyse avec des articles Milvus.
    Utilise l'évaluation Lichess ou Stockfish comme requête de recherche.
    """
    logger.info("[NODE MILVUS] Début de recherche RAG...")
    
    try:
        # Déterminer le texte de recherche (priorité: Lichess, sinon Stockfish)
        search_query = state.get("lichess_evaluation") or state.get("stockfish_evaluation")
        
        if not search_query:
            logger.warning("[NODE MILVUS] ⚠️ Aucune évaluation disponible pour la recherche")
            return {"milvus_context": None}
        
        logger.debug(f"[NODE MILVUS] Requête de recherche: {str(search_query)[:50]}...")
        
        # Rechercher les articles similaires
        results = retrieve_articles(search_query)
        
        if results:
            logger.info(f"[NODE MILVUS] ✓ {len(results)} articles trouvés")
            # Formater le contexte pour le formatter final
            context = "\n".join([
                f"- {r.get('title', 'N/A')}: {r.get('text', '')[:100]}..."
                for r in results
            ])
            return {"milvus_context": context}
        else:
            logger.warning("[NODE MILVUS] ⚠️ Aucun article trouvé")
            return {"milvus_context": None}
    
    except Exception as e:
        logger.error(f"[NODE MILVUS] ✗ Erreur recherche RAG: {str(e)}")
        return {"milvus_context": None}


# --- Fromatter Node ---

def node_format_response(state: AgentState):
    """Formate la réponse finale pour l'utilisateur."""
    logger.info("[NODE FORMATTER] Début de formatage de la réponse")

    lichess_evaluation = state.get("lichess_evaluation")
    stockfish_evaluation = state.get("stockfish_evaluation")

    if lichess_evaluation:
        final_answer = f"Position connue. Théorie: {lichess_evaluation}"
    elif stockfish_evaluation:
        final_answer = f"Analyse Stockfish: {stockfish_evaluation}"
    else:
        final_answer = "Aucune réponse trouvée"

    logger.info(f"[NODE FORMATTER] ✓ Réponse formatée")
    return {"final_answer": final_answer}
