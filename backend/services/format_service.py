import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI

from config.logger import logger
from backend.graph.state import AgentState

# --- Initialisation du LLM ---


def get_llm():
    """Initialise et retourne une instance du LLM."""

    api_key = os.getenv("MISTRAL_API_KEY")

    return ChatMistralAI(model="mistral-small-2603", temperature=0.7, api_key=api_key)


# --- Construction du prompt ---
def build_formatting_prompt():
    """Crée le template du prompt pour formater la réponse."""
    template = """You are an elite Chess Grandmaster and professional coach. Your goal is to analyze a chess opening based on the provided context.

    ### CONTEXT DATA:
    {context}

    ### INSTRUCTIONS:
    Using ONLY the context provided, craft a natural, insightful, and structured response in English. Follow this structure:

    1. **Opening Overview**: Identify the opening and provide a brief historical or strategic overview based on the context.
    2. **Engine Analysis**: If Stockfish evaluations are present, explain the evaluation (in centipawns or +/- notation) and list the top engine-recommended moves.
    3. **Key Concepts (Wikipedia)**: Summarize the most meaningful insights from the Wikipedia data. Focus on the 'why' behind the moves, not just the names.
    4. **Curated Resources**: Select the best video links from the context. Provide a one-sentence summary for each, explaining what the viewer will learn.
    5. **Coach's Recommendation**: End with a definitive, encouraging recommendation for the next move or the overall strategy to adopt.

    ### TONE & STYLE:
    - Speak like an experienced mentor: authoritative yet encouraging.
    - Avoid robotic lists; use transitions to make the text flow naturally.
    - If certain information is missing from the context, do not hallucinate; focus on what is available."""

    return ChatPromptTemplate.from_template(template=template)


def build_context_string(state: AgentState) -> str:
    """Construit une chaîne de contexte à partir du state."""

    parts = []

    # Théorie Lichess
    if state.get("lichess_evaluation"):
        parts.append(f"opening : {state["lichess_evaluation"]}")

    # Analyse Stockfish
    if state.get("stockfish_evaluation"):
        stockfish = state["stockfish_evaluation"]
        parts.append(
            f"Best move(Stockfish): {stockfish.get('move')} "
            f"({stockfish.get('cp')} centipawns)"
        )

    # Articles wikipedia
    if state.get("articles_context"):
        articles = state["articles_context"]

        for i, article in enumerate(articles):
            parts.append(
                f"wikipedia {i+1} - {article.get('title', 'N/A')} : {article.get('text', 'N/A')}"
            )

    # Vidéos YouTube
    if state.get("videos_context"):
        videos = state["videos_context"]

        for i, video in enumerate(videos):
            parts.append(
                f"youtube {i+1}  - {video.get('title', 'N/A')} : {video.get('description', 'N/A')}"
                f"thumbnail : {video.get('video_url', 'N/A')}"
                f"url : {video.get('video_url', 'N/A')}"
            )

    return "\n".join(parts) if parts else "Aucune information disponible"


def format_llm_response(state: AgentState) -> str:
    """
    Formate la réponse finale en utilisant un LLM.

    Args:
        state: L'état du graphe contenant tous les résultats

    Returns:
        Une réponse formatée naturellement
    """
    logger.info("[FORMAT_SERVICE] Début du formatage avec LLM")

    try:
        # Construire le contexte
        context = build_context_string(state)
        logger.debug(f"[FORMAT_SERVICE] Contexte construit: {len(context)} caractères")

        # Initialiser le LLM et le prompt
        llm = get_llm()
        prompt = build_formatting_prompt()

        # Créer la chain
        chain = prompt | llm | StrOutputParser()

        # Invoquer
        logger.debug("[FORMAT_SERVICE] Appel du LLM...")
        response = chain.invoke({"context": context})

        logger.info(
            f"[FORMAT_SERVICE] ✓ Réponse formatée par LLM ({len(response)} caractères)"
        )
        return response

    except Exception as e:
        logger.error(f"[FORMAT_SERVICE] ✗ Erreur: {str(e)}")
        logger.info("[FORMAT_SERVICE] Fallback: formatage simple")
        # Fallback en cas d'erreur LLM
        return _format_simple_fallback(state)


def _format_simple_fallback(state: AgentState) -> str:
    """Fallback en formatage simple si le LLM échoue."""
    context = build_context_string(state)
    return f"Analyse de position:\n\n{context}"
