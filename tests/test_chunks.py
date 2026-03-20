from backend.services.rag_service import _extract_wikipedia_articles,_chunk_wikipedia_articles
from config.logger import logger


def debug_chunks(urls: list[str]) -> None:
    """Affiche les chunks générés pour vérifier leur contenu."""
    documents = _extract_wikipedia_articles(urls)
    chunks = _chunk_wikipedia_articles(documents)
    
    logger.info(f"🔍 DEBUG: {len(chunks)} chunks générés")
    print("\n" + "="*80)
    
    for i, chunk in enumerate(chunks[:5], 1):  # Affiche les 5 premiers chunks
        print(f"\n📌 CHUNK {i}")
        print(f"Titre: {chunk.metadata.get('title', 'N/A')}")
        print(f"URL: {chunk.metadata.get('source', 'N/A')}")
        print(f"Taille: {len(chunk.page_content)} caractères")
        print(f"Contenu:\n{chunk.page_content}")
        print("-" * 80)
    
    print(f"\n✅ Total: {len(chunks)} chunks")


if __name__ == "__main__" :

# Test avec une ou deux pages
    test_urls = [
        "https://en.wikipedia.org/wiki/Queen%27s_Gambit",
        "https://en.wikipedia.org/wiki/Sicilian_Defence"
    ]

    debug_chunks(test_urls)