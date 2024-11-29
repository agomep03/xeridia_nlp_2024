import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config

client_id = config.CLIENT_ID
client_secret = config.CLIENT_SECRET

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_popular_songs():
    resultados = sp.search(q='genre:"pop"', type='track', limit=10)
    canciones = [f'{track["name"]} by {track["artists"][0]["name"]}' for track in resultados['tracks']['items']]
    return canciones
