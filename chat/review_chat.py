import sys
import os

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT

class ReviewChat:

    def __init__(self):
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )

    def receive_message(self, review_text):
        """
        Recibe una reseña escrita y devuelve una calificación en estrellas (1 a 5).
        """
        prompt = f"""
        Eres un modelo que evalúa reseñas escritas por usuarios y asigna una calificación en estrellas (de 1 a 5).
        Analiza el contenido de la siguiente reseña y proporciona una calificación basada en la experiencia que describe:
        
        "{review_text}"
        
        Devuelve únicamente el número de estrellas (1, 2, 3, 4 o 5) como respuesta. No incluyas explicaciones adicionales.
        """

        try:
            # Llama a la API de OpenAI para generar la calificación
            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un modelo especializado en análisis de reseñas y calificaciones en estrellas."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=10,
                temperature=0.0,  # Reducir la aleatoriedad para respuestas consistentes
            )

            response = chat_completion.choices[0].message.content.strip()
            return response

        except Exception as e:
            return f"Hubo un error al evaluar la reseña: {str(e)}"
