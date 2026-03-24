from backend.graph.agent import app  # Importe le workflow compilé
from backend.graph.state import AgentState

# État de test
initial_state: AgentState = {
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "is_valid_fen": True,
    "lichess_evaluation": None,
    "stockfish_evaluation": None,
    "final_answer": ""
}

# Afficher le schéma du graphe
print("=== SCHÉMA DU GRAPHE ===")
print(app.get_graph().draw_ascii())

# Lancer le workflow
result = app.invoke(initial_state)

# Afficher le résultat
print("=== RÉSULTAT DU WORKFLOW ===")
print(f"Lichess: {result['lichess_evaluation']}")
print(f"Stockfish: {result['stockfish_evaluation']}")
print(f"wikipedia: {result['milvus_context']}")
print(f"Réponse finale: {result['final_answer']}")