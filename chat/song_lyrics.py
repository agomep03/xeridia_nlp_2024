import re
from openai import AzureOpenAI
from lyricsgenius import Genius
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, TOKEN_GENIUS, API_MODEL
import requests

class SongLyricsFetcher:
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )

        # Configuración de Genius con un User-Agent actualizado
        self.genius = Genius(
            TOKEN_GENIUS,
            timeout=15,
            retries=3,
            remove_section_headers=True,
            verbose=True
        )
        self.genius._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def extract_song_info(self, message):
        """
        Usa la API de OpenAI para analizar el mensaje y extraer el nombre del artista, 
        la canción y/o una frase de la canción.
        """
        prompt = f"""
        Eres un experto en música. Analiza el siguiente mensaje y extrae:
        - El nombre del artista (si está presente).
        - El nombre de la canción (si está presente).
        - Una frase de la canción (si está presente).

        Ejemplo: si el mensaje pone "extremoduro salir" o "salir de extremoduro", etc extrae nombre del artista (Extremoduro)
        y nombre de la canción (Salir).
        Si no se menciona algo, deja la respuesta como 'Desconocido' para esa parte.

        Mensaje: "{message}"

        Devuelve la información en el siguiente formato:
        Artista: <nombre del artista o 'Desconocido'>
        Canción: <nombre de la canción o 'Desconocido'>
        Frase: <frase de la canción o 'Desconocido'>
        """
        try:
            chat_completion = self.client.chat.completions.create(
                model=API_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en música."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content.strip()
            print("Respuesta de OpenAI:\n", response)

            artist, song, phrase = "Desconocido", "Desconocido", "Desconocido"

            artist_match = re.search(r"Artista:\s*(.+)", response)
            song_match = re.search(r"Canción:\s*(.+)", response)
            phrase_match = re.search(r"Frase:\s*(.+)", response)

            if artist_match:
                artist = artist_match.group(1).strip()
            if song_match:
                song = song_match.group(1).strip()
            if phrase_match:
                phrase = phrase_match.group(1).strip()

            print(f"Artista: {artist}, Canción: {song}, Frase: {phrase}")
            return artist, song, phrase

        except Exception as e:
            print("Error al procesar el mensaje:", str(e))
            return "Error", "Desconocido", f"Hubo un error al procesar el mensaje: {str(e)}"

    def fetch_song_lyrics(self, artist, song, phrase):
        """
        Usa la API de Genius para obtener la letra de la canción considerando todos los casos:
        """
        try:
            if not artist or not song:
                return "Por favor, proporciona tanto el artista como la canción."

            print(f"Buscando la letra de '{song}' de '{artist}'...")
            song_data = self.genius.search_song(song, artist)

            if song_data:
                return song_data.lyrics
            else:
                return f"No se encontró la canción '{song}' de '{artist}'."

        except Exception as e:
            return f"Hubo un error al obtener la letra: {str(e)}"

    def get_lyrics(self, message):
        """
        Coordina el flujo: extrae la información y obtiene la letra.
        """
        artist, song, phrase = self.extract_song_info(message)
        
        if artist == "Desconocido" and song == "Desconocido":
            return "No se pudo extraer la información del mensaje."

        lyrics = self.get_song_url(
            artist if artist != "Desconocido" else "" +
            song if song != "Desconocido" else "" +
            phrase if phrase != "Desconocido" else ""
        )
        return lyrics

    import requests

    def get_song_url(self,message):
        headers = {'Authorization': f'Bearer {TOKEN_GENIUS}'}
        url = "https://api.genius.com/search"
        params = {'q': message}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            song_path = data['response']['hits'][0]['result']['path']
            song_url = f"https://genius.com{song_path}"
            return song_url
        else:
            return f"Error en la solicitud: {response.status_code} - {response.text}"