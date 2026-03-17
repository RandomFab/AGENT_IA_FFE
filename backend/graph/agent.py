from langgraph.graph import StateGraph, START, END
from backend.graph.state import AgentState
from backend.graph.nodes import node_stockfish, node_lichess, node_format_response


workflow = StateGraph(AgentState)

# --- Ajouter les nœuds ---
workflow.add_node("lichess", node_lichess)
workflow.add_node("stockfish", node_stockfish)
workflow.add_node("formatter", node_format_response)

# --- Configuration du point d'entrée ---
workflow.set_entry_point("lichess")

# --- Arête ---

## Arêtes Lichess 'conditionnelles' → (Stockfish OU Formatage)


def should_use_stockfish(state: AgentState) -> str:
    """Détermine si on a besoin de Stockfish."""
    if state.get("lichess_evaluation") is None:
        return "stockfish"  # Pas de théorie trouvée, appelle Stockfish
    else:
        return "formatter"


workflow.add_conditional_edges(
    "lichess",
    should_use_stockfish,
    {"stockfish": "stockfish", "formatter": "formatter"},
)

## Arête Stockfish → Fromatage
workflow.add_edge("stockfish", "formatter")

## Arête Fromatage → END
workflow.add_edge("formatter", END)

# Compile workflow
app = workflow.compile()
