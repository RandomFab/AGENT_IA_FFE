"""
Script pour nettoyer la collection Milvus 'chess_openings'.
"""

import os
from dotenv import load_dotenv
from pymilvus import connections, utility
from config.logger import logger

load_dotenv()


def clean_milvus_collection(collection_name: str = "chess_openings") -> dict:
    """Supprime la collection Milvus spécifiée.
    
    Args:
        collection_name: Nom de la collection à nettoyer (défaut: chess_openings)
        
    Returns:
        Dictionnaire avec le statut et les détails de l'opération
    """
    try:
        # Se connecter à Milvus
        milvus_host = os.getenv("MILVUS_HOST", "localhost")
        milvus_port = os.getenv("MILVUS_PORT", "19530")
        
        logger.info(f"🔗 Connexion à Milvus : {milvus_host}:{milvus_port}")
        connections.connect(
            "default",
            host=milvus_host,
            port=milvus_port
        )
        
        # Vérifier si la collection existe
        if not utility.has_collection(collection_name):
            logger.warning(f"⚠️ La collection '{collection_name}' n'existe pas")
            return {
                "status": "warning",
                "message": f"La collection '{collection_name}' n'existe pas"
            }
        
        # Récupérer le nombre d'entités avant suppression
        from pymilvus import Collection
        collection = Collection(collection_name)
        row_count_before = collection.num_entities
        logger.info(f"📊 Collection '{collection_name}' contient {row_count_before} entrées")
        
        # Supprimer la collection
        logger.info(f"🗑️ Suppression de la collection '{collection_name}'...")
        utility.drop_collection(collection_name)
        
        # Vérifier que la collection a bien été supprimée
        if utility.has_collection(collection_name):
            logger.error(f"❌ Erreur: La collection '{collection_name}' existe toujours après suppression")
            return {
                "status": "error",
                "message": f"Erreur lors de la suppression de '{collection_name}'"
            }
        
        logger.info(f"✅ Collection '{collection_name}' supprimée avec succès ({row_count_before} entrées supprimées)")
        
        return {
            "status": "success",
            "collection_name": collection_name,
            "deleted_entries": row_count_before,
            "message": f"Collection '{collection_name}' nettoyée avec succès"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage de la collection : {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur: {str(e)}"
        }
    finally:
        # Fermer la connexion
        connections.disconnect("default")
        logger.debug("🔌 Connexion Milvus fermée")


if __name__ == "__main__":
    # Importer la config
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))
    
    # Nettoyer la collection
    result = clean_milvus_collection()
    
    # Afficher le résultat
    print("\n" + "="*60)
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    if result['status'] == 'success':
        print(f"Entrées supprimées: {result['deleted_entries']}")
    print("="*60 + "\n")
