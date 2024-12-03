import sys
import os

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT

class ConsultantChat:

    def __init__(self):
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )

    def receive_message(self, message):
        response = self.answer_question(message)  # Procesa la pregunta del usuario
        return response

    def answer_question(self, message):
        prompt = f"""
        Eres un experto en música y puedes responder cualquier pregunta relacionada con artistas, canciones, géneros musicales,
        historia de la música, instrumentos o tendencias actuales. Un usuario te ha preguntado lo siguiente:
        "{message}"

        Proporciona una respuesta completa, precisa y clara. Si la pregunta no es clara, responde con sugerencias sobre cómo
        podría reformularla o añade contexto adicional relacionado con música para ayudar al usuario. No incluyas información que no sea relevante.
        """

        try:
            # Llama a la API de OpenAI para obtener la respuesta
            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en música."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content

            return response

        except Exception as e:
            return f"Hubo un error al responder la pregunta: {str(e)}"
