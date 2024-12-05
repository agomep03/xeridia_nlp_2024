import re
from openai import AzureOpenAI
from lyricsgenius import Genius
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, TOKEN_GENIUS, API_MODEL

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
            # Llamada a la API de Azure OpenAI
            chat_completion = self.client.chat.completions.create(
                model=API_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en música."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            # Obtener el contenido de la respuesta
            response = chat_completion.choices[0].message.content.strip()
            print("Respuesta de OpenAI:\n", response)  # Verificar el formato

            # Inicializamos los valores como 'Desconocido'
            artist, song, phrase = "Desconocido", "Desconocido", "Desconocido"

            # Ajustar las expresiones regulares para extraer la información
            artist_match = re.search(r"Artista:\s*(.+)", response)
            song_match = re.search(r"Canción:\s*(.+)", response)
            phrase_match = re.search(r"Frase:\s*(.+)", response)

            if artist_match:
                artist = artist_match.group(1).strip()
            if song_match:
                song = song_match.group(1).strip()
            if phrase_match:
                phrase = phrase_match.group(1).strip()

            print(f"Artista: {artist}, Canción: {song}, Frase: {phrase}")  # Verificar los valores extraídos
            return artist, song, phrase

        except Exception as e:
            print("Error al procesar el mensaje:", str(e))
            return "Error", "Desconocido", f"Hubo un error al procesar el mensaje: {str(e)}"

    def fetch_song_lyrics(self, artist, song, phrase):
        """
        Usa la API de Genius para obtener la letra de la canción considerando todos los casos:
        - Tenemos artista, canción y frase
        - Tenemos artista y canción pero no frase
        - Tenemos artista y frase pero no canción
        - Tenemos artista pero no canción ni frase
        - Tenemos canción y frase pero no artista
        - Tenemos canción pero no frase ni artista
        - Tenemos frase pero no artista ni canción
        - No tenemos artista, ni canción ni frase
        """
        try:
            # Caso 1: Tenemos artista, canción y frase
            if artist and song and phrase:
                song_data = self.genius.search_song(song, artist)
                if song_data and phrase.lower() in song_data.lyrics.lower():
                    return song_data.lyrics
                else:
                    return f"No se encontró la canción '{song}' del artista '{artist}' que contenga la frase '{phrase}'."

            # Caso 2: Tenemos artista y canción, pero no frase
            elif artist and song:
                song_data = self.genius.search_song(song, artist)
                if song_data:
                    return song_data.lyrics
                else:
                    return f"No se encontró la canción '{song}' del artista '{artist}'."

            # Caso 3: Tenemos artista y frase, pero no canción
            elif artist and phrase:
                search_result = self.genius.search_song(phrase, artist)
                if search_result:
                    return search_result.lyrics
                else:
                    return f"No se encontró ninguna canción de '{artist}' que contenga la frase '{phrase}'."

            # Caso 4: Tenemos solo el artista
            elif artist:
                artist_data = self.genius.search_artist(artist, max_songs=3, sort="title")
                if artist_data:
                    return f"Se encontraron canciones del artista '{artist}':\n" + \
                        "\n".join(song.title for song in artist_data.songs[:3])
                else:
                    return f"No se encontró el artista '{artist}'."

            # Caso 5: Tenemos canción y frase, pero no artista
            elif song and phrase:
                search_result = self.genius.search_song(song)
                if search_result and phrase.lower() in search_result.lyrics.lower():
                    return search_result.lyrics
                else:
                    return f"No se encontró la canción '{song}' que contenga la frase '{phrase}'."

            # Caso 6: Tenemos solo la canción
            elif song:
                search_result = self.genius.search_song(song)
                if search_result:
                    return search_result.lyrics
                else:
                    return f"No se encontró la canción '{song}'."

            # Caso 7: Tenemos solo la frase
            elif phrase:
                search_result = self.genius.search_song(phrase)
                if search_result:
                    return search_result.lyrics
                else:
                    return f"No se encontró ninguna canción con la frase '{phrase}'."

            # Caso 8: No tenemos artista, canción ni frase
            else:
                return "No se ha proporcionado suficiente información para obtener la letra de la canción."

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



