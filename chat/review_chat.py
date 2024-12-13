from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT
from utils.rag import RAG


def parse_response(response):
    
    dict = {"rating": None, "song": None, "artist": None}

    for phrase in response.split('\n'):
        if "[CAL" in phrase:
            dict['rating'] = int(phrase.split("]")[1].strip())
        elif "[CAN" in phrase:
            dict['song'] = phrase.split("]")[1].strip()
        elif "[ART" in phrase:
            dict['artist'] = phrase.split("]")[1].strip()

    return dict



CONTEXT ="""Eres un modelo especializado en análisis de reseñas y calificaciones en estrellas.
            Devuelve de output siempre esta estructura:
            [CALIFICACIÓN] Un número del 1 al 5
            [CANCIÓN] La canción en la reseña o 'None' en caso de no haber.
            [ARTISTA] El artista en la reseña o 'None' en caso de no haber.
"""

class ReviewChat:

    def __init__(self, rag:RAG=None):
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )

        self.rag = rag

    def receive_message(self, review_text):
        """
        Recibe una reseña escrita y devuelve una calificación en estrellas (1 a 5).
        """
        prompt = f"""
        Por favor analiza esta reseña y responde con la estructura indicada: 
        
        "{review_text}"
        """

        try:
            # Llama a la API de OpenAI para generar la calificación
            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": CONTEXT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,  # Reducir la aleatoriedad para respuestas consistentes
            )
            response = chat_completion.choices[0].message.content
            print(response)
            response = parse_response(response)
            print(response)
            if self.rag is not None:
                self.rag.index_review(review_text, response)
            return response['rating']

        except Exception as e:
            return f"Hubo un error al evaluar la reseña: {str(e)}"
