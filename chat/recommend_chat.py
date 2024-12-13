import sys
import os

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT

class RecommendChat:

    def __init__(self):
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )

    def receive_message(self, message):
        recommendation = self.recommend(message)  # Se llama a la función recomendadora
        return recommendation

    def recommend(self, message):
        prompt = f"""
        Eres un asistente experto en música y podcasts. Un usuario te ha pedido recomendaciones basadas en el siguiente mensaje:
        "{message}"

        Proporciona solo una lista de recomendaciones que incluya:
        - Canciones del artista (si se menciona).
        - Artistas relacionados.
        - Canciones relacionadas.
        - Si el usuario lo menciona explícitamente, recomendaciones de podcasts relevantes.

        Cada apartado debe estar encabezado por los puntos anteriores en caso de que se mencione el artista. Si no se menciona o el usuario no sabe
        que escuchar los apartados los puedes poner como quieras.
        Por favor, no incluyas ninguna introducción ni conclusión como "Aquí tienes recomendaciones" o "Si deseas más información".
        Solo proporciona las recomendaciones en un formato claro y directo. No repitas el mensaje del usuario ni incluyas texto innecesario.

        Si no hay recomendaciones directas, ofrece opciones generales basadas en géneros similares.
        """

        try:
            # Se llama a la API de OpenAI para obtener recomendaciones
            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en música y podcasts."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content

            return response

        except Exception as e:
            return f"Hubo un error al generar las recomendaciones: {str(e)}"

    def get_recommendation_by_artist(self, artist_name):
        """
        Obtiene recomendaciones basadas en un artista específico.
        :param artist_name: Nombre del artista.
        :return: Una lista de canciones relacionadas.
        """
        try:
            prompt = f"""
            Un usuario está buscando recomendaciones basadas en el artista: {artist_name}.

            Proporciona:
            - Canciones populares del artista.
            - Artistas relacionados.
            - Canciones similares.

            Formato claro y directo, sin introducciones ni conclusiones innecesarias.
            """

            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en música y recomendaciones."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content

            return response

        except Exception as e:
            return f"Hubo un error al generar recomendaciones para el artista {artist_name}: {str(e)}"

    def get_recommendation_by_genre(self, genre):
        """
        Obtiene recomendaciones basadas en un género musical.
        :param genre: Género especificado por el usuario.
        :return: Una lista de canciones relacionadas.
        """
        try:
            prompt = f"""
            Un usuario está buscando recomendaciones musicales en el género: {genre}.

            Proporciona:
            - Canciones destacadas en este género.
            - Artistas influyentes.
            - Canciones modernas que representan el género.

            Formato claro y directo, sin introducciones ni conclusiones innecesarias.
            """

            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en géneros musicales."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content

            return response

        except Exception as e:
            return f"Hubo un error al generar recomendaciones para el género {genre}: {str(e)}"
