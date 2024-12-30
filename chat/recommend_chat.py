import sys
import os

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT
from chat.sentiment_analysis import SentimentAnalysis
from utils.rag import RAG

class RecommendChat:

    def __init__(self,rag:RAG=None):
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )
        self.sentiment_analyzer = SentimentAnalysis()
        self.rag = rag

    def receive_message(self, message):
        recommendation = self.recommend(message)
        return recommendation

    def recommend(self, message):
            """
            Usa RAG para recuperar contexto y generar recomendaciones.
            :param message: Consulta del usuario.
            :return: Recomendaciones generadas.
            """
            #try:
            retrieved_context = self.rag.retrieve(message, top_k=5)
            
            context = "\n".join([
                f"- {item['rating']} (Canción: {item['song']}, Artista: {item['artist']})"
                for item in retrieved_context
            ])

            prompt = f"""
            Un usuario ha preguntado lo siguiente:
            "{message}"

            Basándote en la información recuperada:
            {context}

            Proporciona una lista clara de recomendaciones musicales:
            - Canciones relevantes.
            - Artistas relacionados.
            - Otros datos útiles.
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

            #except Exception as e:
            #    return f"Hubo un error al generar recomendaciones con RAG: {str(e)}"


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

    def get_recommendation_by_mood(self, message):
        """
        Obtiene recomendaciones basadas en el estado de ánimo detectado.
        :param message: Texto del usuario que será analizado para determinar su estado de ánimo.
        :return: Una lista de canciones relacionadas con el estado de ánimo.
        """
        try:
            mood = self.sentiment_analyzer.analyze_sentiment(message)

            prompt = f"""
            Un usuario está buscando música adecuada para su estado de ánimo detectado como: {mood}.

            Proporciona:
            - Canciones que reflejen este estado de ánimo.
            - Artistas que compongan música acorde a este estado de ánimo.
            - Géneros que sean relevantes para este estado de ánimo.

            Formato claro y directo, sin introducciones ni conclusiones innecesarias.
            """

            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en música y emociones."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content

            return response

        except Exception as e:
            return f"Hubo un error al generar recomendaciones para el estado de ánimo: {str(e)}"
