import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from backend.schemas.youtube_schema import YoutubeVideosOutput, YoutubeVideo

# Charger les variables d'environnement du fichier .env
load_dotenv()


def get_chess_opening_ytb_video(opening: str, max_results: int = 25) -> YoutubeVideosOutput | Dict[str, Any]:
    """
    Recherche des vidéos YouTube sur une ouverture d'échecs.
    
    Args:
        opening: Le nom de l'ouverture (ex: "French Defence")
        max_results: Nombre maximum de résultats (défaut: 25)
    
    Returns:
        Dict contenant les résultats ou un message d'erreur
    """
    
    # 1. Vérifier les variables d'environnement
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return {
            "error": "YOUTUBE_API_KEY not configured in environment variables",
            "statusCode": 400
        }
    
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
            return {
                "error": error_data.get("message", "Unknown API error"),
                "statusCode": response.status_code,
                "details": error_data
            }
    
        data = response.json()
        
        videos = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            
            video = YoutubeVideo(
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                thumbnail_url=snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                publishedAt=snippet.get("publishedAt", ""),
                video_url=f"https://www.youtube.com/watch?v={video_id}"
            )
            videos.append(video)
        
        return YoutubeVideosOutput(videos=videos)
    
    # 4. Gestion spécifique des erreurs de connexion
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout - YouTube API took too long to respond",
            "statusCode": 504
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Connection error - Could not reach YouTube API",
            "statusCode": 503
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Request error: {str(e)}",
            "statusCode": 500
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "statusCode": 500
        }