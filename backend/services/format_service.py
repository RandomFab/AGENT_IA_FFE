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
    **CRITICAL**: Use ONLY information from the context provided. NEVER invent, hallucinate, or add information not in the context. If information is missing, skip that section.

    Structure your response in this exact order:

    1. **Best Move**: Start with the best move to play (from Lichess or Stockfish evaluation). Be direct and clear.
    
    2. **Opening Overview**: If an opening name is found in the context, provide a brief historical or strategic overview based ONLY on the Wikipedia context given.
    
    3. **Best Resource**: Select the SINGLE best video link from the context that explains this opening in approximately 10 minutes or less. Choose based on the description provided. Include the video title, a one-line summary of what the viewer will learn, and the link.
    
    4. **Coach's Recommendation**: Give a definitive, encouraging recommendation for strategy or next steps based on the context.

    ### SPECIAL CASE - Stockfish Only:
    If the context contains ONLY Stockfish evaluation data with NO opening name or Wikipedia/YouTube context:
    - Propose the best move with a brief explanation of the key alternative moves
    - Keep the response SHORT and FOCUSED (under 1000 characters)
    - Do NOT generate lengthy text

    ### CONSTRAINTS:
    - **MAXIMUM 3000 characters** for the entire response
    - **ONLY use information explicitly provided in the context**
    - Speak like an experienced mentor: authoritative yet encouraging
    - Use natural transitions between sections
    - If a section's information is missing from context, skip it entirely"""

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
        logger.debug(context)

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
