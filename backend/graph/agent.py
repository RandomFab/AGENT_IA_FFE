from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from graph.nodes import node_stockfish, node_lichess, node_format_response,node_wikipedia_search, node_youtube_search


workflow = StateGraph(AgentState)

# --- Ajouter les nœuds ---
workflow.add_node("lichess", node_lichess)
workflow.add_node("wikipedia", node_wikipedia_search)
workflow.add_node("youtube", node_youtube_search)
workflow.add_node("stockfish", node_stockfish)
workflow.add_node("formatter", node_format_response)

# --- Configuration du point d'entrée ---
workflow.set_entry_point("lichess")

# --- Arête ---

## Arêtes Lichess 'conditionnelles' → (Stockfish OU wikipedia + youtube)


def should_use_stockfish(state: AgentState) -> str:
    """Détermine si on a besoin de Stockfish."""
    if state.get("lichess_evaluation") is None:
        return "stockfish"  # Pas de théorie trouvée, appelle Stockfish
    else:
        return ["wikipedia", "youtube"]


workflow.add_conditional_edges(
    "lichess",
    should_use_stockfish,
    {"stockfish": "stockfish", "wikipedia": "wikipedia", "youtube": "youtube"},
)

## Arête wikipedia → Fromatage
workflow.add_edge("wikipedia", "formatter")

## Arête youtube → Fromatage
workflow.add_edge("youtube", "formatter")

## Arête Stockfish → Fromatage
workflow.add_edge("stockfish", "formatter")

## Arête Fromatage → END
workflow.add_edge("formatter", END)

# Compile workflow
app = workflow.compile()