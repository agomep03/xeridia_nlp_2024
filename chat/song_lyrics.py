import re
from openai import AzureOpenAI
from lyricsgenius import Genius
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, TOKEN_GENIUS

class SongLyricsFetcher:
    
    def __init__(self):
        # Iniciamos el cliente de OpenAI
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )
        # Iniciamos el cliente de Genius con el token
        self.genius = Genius(TOKEN_GENIUS)
    
    def extract_song_info(self, message):
        """
        Usa la API de OpenAI para analizar el mensaje y extraer el nombre del artista, la canción y/o una frase de la canción.
        """
        prompt = f"""
        Analiza el siguiente mensaje y extrae:
        - El nombre del artista (si está presente).
        - El nombre de la canción (si está presente).
        - Una frase de la canción (si está presente).

        Si no se menciona algo, deja la respuesta como 'Desconocido' para esa parte.

        Mensaje: "{message}"
        """

        try:
            # Llamamos a la API de OpenAI para procesar el mensaje
            chat_completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en música."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content.strip()

            # Intentamos extraer la información de manera flexible
            artist = "Desconocido"
            song = "Desconocido"
            phrase = "Desconocido"

            # Buscamos patrones comunes de respuesta de OpenAI
            match_artist_song = re.search(r"Artista:\s*(.*?),\s*Canción:\s*(.*?),\s*Frase:\s*(.*)", response)
            match_artist = re.search(r"Artista:\s*(.*?),\s*Canción:\s*(.*)", response)
            match_song = re.search(r"Canción:\s*(.*?),\s*Frase:\s*(.*)", response)
            match_phrase = re.search(r"Frase:\s*(.*)", response)

            if match_artist_song:
                artist = match_artist_song.group(1).strip()
                song = match_artist_song.group(2).strip()
                phrase = match_artist_song.group(3).strip()
            elif match_artist:
                artist = match_artist.group(1).strip()
                song = match_artist.group(2).strip()
            elif match_song:
                song = match_song.group(1).strip()
                phrase = match_song.group(2).strip()
            elif match_phrase:
                phrase = match_phrase.group(1).strip()

            return artist, song, phrase

        except Exception as e:
            return "Error", "Desconocido", f"Hubo un error al procesar el mensaje: {str(e)}"

    def fetch_song_lyrics(self, artist, song, phrase):
        """
        Usa la API de Genius para obtener la letra de la canción.
        """
        try:
            if artist and song:
                # Si se tiene tanto el artista como la canción
                artist_data = self.genius.search_artist(artist, max_songs=3, sort="title")
                if artist_data:
                    song_data = self.genius.search_song(song, artist_data.name)
                    if song_data:
                        return song_data.lyrics
                    else:
                        return f"No se encontró la canción '{song}' para el artista '{artist}'."
                else:
                    return f"No se encontró el artista '{artist}'."
            
            elif song and phrase:
                # Si se tiene solo la canción y una frase (podría ser una búsqueda de canción basada en fragmento)
                search_result = self.genius.search_song(phrase)
                if search_result:
                    return search_result.lyrics
                else:
                    return f"No se encontró ninguna canción con la frase '{phrase}'."
            
            elif artist and phrase:
                # Si se tiene el artista y una frase (búsqueda por frase)
                search_result = self.genius.search_song(phrase, artist)
                if search_result:
                    return search_result.lyrics
                else:
                    return f"No se encontró ninguna canción de '{artist}' con la frase '{phrase}'."
            
            else:
                return "No se ha encontrado suficiente información para obtener la letra de la canción."
            
        except Exception as e:
            return f"Hubo un error al obtener la letra: {str(e)}"

    
    def get_lyrics(self, message):
        """
        Esta función coordina el flujo: extrae la información y obtiene la letra.
        """
        artist, song, phrase = self.extract_song_info(message)
        
        # Verificamos si todos los datos son "Desconocido"
        if artist == "Desconocido" and song == "Desconocido" and phrase == "Desconocido":
            return "No se pudo extraer la información del mensaje."

        # Solo pasamos los parámetros relevantes a fetch_song_lyrics
        lyrics = self.fetch_song_lyrics(artist if artist != "Desconocido" else None,
                                        song if song != "Desconocido" else None,
                                        phrase if phrase != "Desconocido" else None)
        return lyrics



