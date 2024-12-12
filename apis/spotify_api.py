import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json

# Ruta al archivo de credenciales
CREDENTIALS_FILE = "spotify_credentials.json"

def load_credentials():
    """
    Carga las credenciales de Spotify desde un archivo JSON.
    Si el archivo no existe o está vacío, devuelve None.
    """
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            credentials = json.load(file)
        return credentials
    except FileNotFoundError:
        print("Archivo de credenciales no encontrado. Configure las credenciales primero.")
        return None
    except json.JSONDecodeError:
        print("El archivo de credenciales está mal formado.")
        return None

# Cargar credenciales desde el archivo
credentials = load_credentials()

if credentials:
    client_id = credentials["SPOTIFY_CLIENT_ID"]
    client_secret = credentials["SPOTIFY_CLIENT_SECRET"]
    redirect_uri = credentials["SPOTIFY_REDIRECT_URI"]

    # Autenticación basada en la aplicación
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, 
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Autenticación basada en el usuario
    user_auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-read-private user-top-read playlist-read-private"
    )
    sp_user = spotipy.Spotify(auth_manager=user_auth_manager)
else:
    sp = None
    sp_user = None


def get_popular_songs():
    """
    Obtiene canciones populares de un género específico, en este caso pop.
    """
    if not sp:
        return ["Error: Spotify no está configurado correctamente."]
    
    resultados = sp.search(q='genre:"pop"', type='track', limit=10)
    canciones = [f'{track["name"]} by {track["artists"][0]["name"]}' for track in resultados['tracks']['items']]
    return canciones


def get_user_profile():
    """
    Obtiene el perfil básico del usuario autenticado.
    """
    if not sp_user:
        return {"error": "Spotify no está configurado correctamente."}
    
    try:
        user_profile = sp_user.current_user()
        return {
            "name": user_profile.get("display_name", "Desconocido"),
            "id": user_profile.get("id", "No disponible"),
            "email": user_profile.get("email", "No disponible"),
            "country": user_profile.get("country", "No disponible"),
            "product": user_profile.get("product", "No disponible"),
            "followers": user_profile.get("followers", {}).get("total", 0),
        }
    except Exception as e:
        return {"error": f"Error al obtener el perfil: {str(e)}"}


def get_top_artists():
    """
    Obtiene los artistas más escuchados del usuario autenticado.
    """
    if not sp_user:
        return {"error": "Spotify no está configurado correctamente."}
    
    try:
        top_artists = sp_user.current_user_top_artists(limit=5)
        return [artist["name"] for artist in top_artists["items"]]
    except Exception as e:
        return {"error": str(e)}

def get_playlists(query, limit=2, property='id'):
    """
    Obtiene playlists según una query.
    """
    if not sp:
        return ["Error: Spotify no está configurado correctamente."]
    
    resultados = sp.search(q=query, type='playlist', limit=limit)
    playlists = [playlist[property] for playlist in resultados['playlists']['items'] if playlist is not None ]
    return playlists

def get_playlists_items(playlist_id, limit=10, property='id'):
    """
    Obtiene las canciones en una playlist
    """
    if not sp:
        return ["Error: Spotify no está configurado correctamente."]
    
    resultados = sp.playlist_tracks(playlist_id=playlist_id, limit=limit)
    songs = [song['track'][property] for song in resultados['items'] if song is not None ]
    return songs

def get_song(song_id):
    """
    Obtiene una propiedad de una playlist dado su id
    """
    if not sp:
        return ["Error: Spotify no está configurado correctamente."]
    
    resultados = sp.track(track_id=song_id)
    return resultados
    
def song_save_by_user(song_id):
    """
    Obtiene si el usuario tiene guardada una canción o no
    """
    if not sp_user:
        return ["Error: La cuenta de spotify no está configurada correctamente."]
    sp_user.current_user_saved_tracks_contains(tracks=song_id)



#Create Playlist

#Check If User Follows Artists or Users

#Check User's Saved Tracks
