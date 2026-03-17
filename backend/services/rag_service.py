import urllib.parse
import numpy as np
from langchain_core.documents import Document
from langchain_community.document_loaders import WikipediaLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient

from config.logger import logger
from config.config import INDEX_WIKIPEDIA_DIR

# --- Fonction principale --- 

def ingest_chess_openings_to_milvus(urls: list[str]) -> dict:
    """Pipeline complet d'ingestion : extraction → chunking → embedding → Milvus.
    
    Fonction à usage unique pour générer la base de données Milvus complète.

    Args:
        urls: Liste d'URLs Wikipedia des ouvertures d'échecs

    Returns:
        Résultat du pipeline {inserted_count, total_chunks, total_urls, status}
        
    Raises:
        Exception: Si une étape du pipeline échoue
    """
    logger.info(f"🚀 Démarrage du pipeline d'ingestion complet ({len(urls)} pages)")

    try:
        # Étape 1 : Extraction
        documents = _extract_wikipedia_articles(urls)
        if not documents:
            logger.error("❌ Aucun document n'a pu être récupéré")
            return {
                "status": "failed",
                "inserted_count": 0,
                "total_chunks": 0,
                "total_urls": len(urls),
                "error": "Aucun document extrait"
            }

        logger.info(f"✅ {len(documents)} document(s) récupéré(s)")

        # Étape 2 : Chunking
        chunks = _chunk_wikipedia_articles(documents)
        logger.info(f"✅ {len(chunks)} chunks générés")

        # Étape 3 : Embedding
        milvus_data = _embed_chunks(chunks)
        logger.info(f"✅ {len(milvus_data)} vecteurs générés")

        # Étape 4 : Insertion dans Milvus
        result = _load_vectors_in_vector_store(milvus_data)
        
        logger.info(f"🎉 Pipeline terminé avec succès : {result['inserted_count']} vecteurs insérés")
        
        return {
            "status": "success",
            "inserted_count": result["inserted_count"],
            "total_chunks": len(chunks),
            "total_urls": len(urls)
        }

    except Exception as e:
        logger.error(f"❌ Pipeline échoué à cause de : {str(e)}")
        return {
            "status": "failed",
            "inserted_count": 0,
            "total_chunks": 0,
            "total_urls": len(urls),
            "error": str(e)
        }

# --- Sous fontions ---

## --- Extraction des noms depuis les liens WikiPedia ---

def _extract_title(url: str) -> str:
    """Extrait le titre propre depuis l'URL Wikipedia.

    Args:
        url: URL Wikipedia encodée (ex: https://en.wikipedia.org/wiki/Queen%27s_Indian_Defense)

    Returns:
        Titre décodé et formaté en minuscules (ex: "Queen's Indian Defense")
    """
    title_encoded = url.split("/wiki/")[-1]
    return urllib.parse.unquote(title_encoded).replace("_", " ")


## --- Extraction des articles ---

def _extract_wikipedia_articles(urls: list[str]) -> list[Document]:
    """Récupère et charge les articles Wikipedia depuis les URLs.

    Args:
        urls: Liste d'URLs Wikipedia

    Returns:
        Liste de documents LangChain avec métadonnées (titre, URL source)
    """
    documents = []

    for url in urls:
        title = _extract_title(url)
        logger.info(f"📥 Récupération de : {title}...")

        try:
            loader = WikipediaLoader(query=title, lang="en", load_max_docs=1)
            raw_docs = loader.load()

            if not raw_docs:
                logger.warning(f"⚠️ Page introuvable pour {title}")
                continue

            documents.extend(raw_docs)
            logger.info(f"✅ {title} chargé ({len(raw_docs)} document)")

        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de {title}: {str(e)}")
            continue

    return documents


## --- Transformation des texts en chunks ---

def _chunk_wikipedia_articles(documents: list[Document]) -> list[Document]:
    """Découpe les documents Wikipedia en chunks intelligents.

    Args:
        documents: Liste de documents LangChain à découper

    Returns:
        Liste de chunks (Document) avec métadonnées préservées
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Taille raisonnable pour articles non structurés
        chunk_overlap=100,  # 20% de chevauchement pour contexte
        length_function=len,
    )

    all_chunks = []
    for doc in documents:
        chunks = text_splitter.split_documents([doc])
        all_chunks.extend(chunks)
        logger.debug(f"Document chunké : {len(chunks)} morceaux générés")

    return all_chunks


## --- Transformation des chunks en embeddings ---

_embedding_model = None  # Cache global pour éviter rechargement du modèle

def _get_embedding_model(model_name: str = 'Qwen/qwen3B-embedding-0.6B') -> SentenceTransformer:
    """Retourne le modèle d'embedding en cache (singleton).
    
    Args:
        model_name: Nom du modèle sur HuggingFace
        
    Returns:
        Instance du modèle SentenceTransformer
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"🤖 Chargement du modèle d'embedding : {model_name}")
        try:
            _embedding_model = SentenceTransformer(model_name)
            logger.info(f"✅ Modèle chargé avec succès")
        except Exception as e:
            logger.error(f"❌ Impossible de charger le modèle {model_name}: {str(e)}")
            raise
    return _embedding_model


def _embed_chunks(chunks: list[Document], model_name: str = 'Qwen/qwen3B-embedding-0.6B') -> list[dict]:
    """Génère les embeddings et prépare les données pour Milvus.
    
    Args:
        chunks: Liste de chunks (Document LangChain)
        model_name: Nom du modèle d'embedding
        
    Returns:
        Liste de dictionnaires {id, embedding, text, source, title} pour Milvus
        
    Raises:
        ValueError: Si la liste de chunks est vide
        Exception: Si l'embedding échoue
    """
    if not chunks:
        logger.warning("⚠️ Aucun chunk à embedder")
        return []
    
    logger.info(f"🔄 Génération d'embeddings pour {len(chunks)} chunks...")
    
    try:
        # Récupérer le texte des chunks
        texts = [chunk.page_content for chunk in chunks]
        
        # Charger le modèle
        model = _get_embedding_model(model_name)
        
        # Générer les embeddings
        vectors = model.encode(texts, show_progress_bar=True)
        
        # Préparer les données pour Milvus
        milvus_data = [
            {
                "id": i,
                "embedding": embedding.tolist(),
                "text": chunk.page_content,
                "source": chunk.metadata.get("source", ""),
                "title": chunk.metadata.get("title", "")
            }
            for i, (chunk, embedding) in enumerate(zip(chunks, vectors))
        ]
        
        logger.info(f"✅ {len(milvus_data)} vecteurs générés ({len(vectors[0])} dimensions)")
        return milvus_data
        
    except ValueError as e:
        logger.error(f"❌ Erreur de validation d'embedding: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération d'embeddings: {str(e)}")
        raise

## --- Chargement des vecteurs dans Milvus ---

def _load_vectors_in_vector_store(data: list[dict]) -> dict:
    """Insère les vecteurs dans la collection Milvus.
    
    Args:
        data: Liste de dictionnaires {id, embedding, text, source, title}
        
    Returns:
        Résultat de l'insertion {inserted_count, errors}
        
    Raises:
        Exception: Si l'insertion échoue
    """
    if not data:
        logger.warning("⚠️ Aucune donnée à insérer")
        return {"inserted_count": 0, "errors": []}
    
    client = None
    try:
        logger.info(f"📤 Connexion à Milvus ({INDEX_WIKIPEDIA_DIR})")
        client = MilvusClient(INDEX_WIKIPEDIA_DIR)
        
        logger.info(f"📝 Insertion de {len(data)} vecteurs dans 'wikipedia_collection'...")
        result = client.insert(
            collection_name="wikipedia_collection",
            data=data
        )
        
        inserted_count = result.get("insert_count", 0) if isinstance(result, dict) else len(result)
        logger.info(f"✅ {inserted_count} vecteurs insérés avec succès")
        
        return {
            "inserted_count": inserted_count,
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'insertion dans Milvus: {str(e)}")
        raise
    finally:
        if client:
            try:
                client.close()
                logger.debug("🔌 Connexion Milvus fermée")
            except Exception as e:
                logger.warning(f"⚠️ Erreur lors de la fermeture Milvus: {str(e)}")