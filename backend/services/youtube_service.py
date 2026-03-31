import os
import requests
from typing import List
from dotenv import load_dotenv
from schemas.youtube_schema import YoutubeVideoOutput

# Charger les variables d'environnement du fichier .env
load_dotenv()


def get_ytb_video(opening: str, max_results: int = 25) -> List[YoutubeVideoOutput]:
    """
    Recherche des vidéos YouTube sur une ouverture d'échecs.
    
    Args:
        opening: Le nom de l'ouverture (ex: "French Defence")
        max_results: Nombre maximum de résultats (défaut: 25)
    
    Returns:
        Liste de YoutubeVideoOutput
        
    Raises:
        ValueError: Si la clé API n'est pas configurée
        TimeoutError: Si la requête YouTube expire
        ConnectionError: Si la connexion échoue
        Exception: Pour les erreurs API YouTube
    """
    
    # 1. Vérifier les variables d'environnement
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not configured in environment variables")
    
    # 2. Configurer la requête
    url = "https://www.googleapis.com/youtube/v3/search"
    
    params = {
        "part": "snippet",
        "q": f"learn {opening} chess",
        "maxResults": max_results,
        "key": api_key,  # ✅ L'API YouTube utilise 'key' directement (pas de Bearer)
        "relevanceLanguage": "en",
        "hl": "en",
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # 3. Vérifier le code de statut HTTP
        if response.status_code != 200:
            error_data = response.json().get("error", {})
            error_message = error_data.get("message", "Unknown API error")
            raise Exception(f"YouTube API error ({response.status_code}): {error_message}")
    
        data = response.json()
        
        videos = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            
            video = YoutubeVideoOutput(
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                publishedAt=snippet.get("publishedAt", ""),
                video_url=f"https://www.youtube.com/watch?v={video_id}"
            )
            videos.append(video)
        
        return videos
    
    # 4. Gestion spécifique des erreurs de connexion
    except requests.exceptions.Timeout:
        raise TimeoutError("YouTube API took too long to respond")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not reach YouTube API")
    except requests.exceptions.RequestException as e:
        raise Exception(f"YouTube API request error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error while searching YouTube: {str(e)}")