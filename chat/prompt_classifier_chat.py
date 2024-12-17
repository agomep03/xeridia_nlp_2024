import joblib
import os
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator, TransformerMixin

from chat.recommend_chat import RecommendChat 
from chat.playlist_chat import PlaylistChat
from chat.consult_chat import ConsultantChat
from chat.review_chat import ReviewChat
from chat.song_lyrics import SongLyricsFetcher

class SentenceTransformerWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.embedder = SentenceTransformer(model_name)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.embedder.encode(X, show_progress_bar=False)
    

class PromptClassifier:
    def __init__(self):
        """Inicializa la clase cargando el pipeline de clasificación y el diccionario."""
        self.pipeline = joblib.load('process_input/modelos_v2/pipeline_model_v2.pkl')

        self.dictionary = {
            "recomendaciones":0,
            "consultar_informacion": 1,
            "crear_playlist": 2,
            "resena": 3,
            "letra": 4
        }

        print("Pipeline cargado correctamente.")

    def classify_prompt(self, text):
        """
        Clasifica el texto de entrada utilizando el pipeline.

        Args:
            text (str): Consulta introducida por el usuario.
        
        Returns:
            int: Índice de la predicción.
        """
        
        predictions = self.pipeline.predict([text])
        print("Predicciones:", predictions)
        return predictions[0]

    async def handle_prediction(self, prediction, text, message):
        """
        Maneja las acciones basadas en la predicción.

        Args:
            prediction (int): Índice de la predicción.
            text (str): Consulta introducida por el usuario.
            message: El mensaje original recibido del usuario.
        """

        if prediction == 0:  # Si la predicción es para recomendaciones
            print("Generando recomendaciones musicales...") 
            recommend_chat = RecommendChat()
            recommendations = recommend_chat.receive_message(text)
            return recommendations
    
        elif prediction == 1:
            print("Buscando información sobre...") 
            consult_chat = ConsultantChat()
            response = consult_chat.receive_message(text)  # Procesa la consulta sobre el artista
            return response

        elif prediction == 2:
            print("Generando una playlist...") 
            playlist_chat = PlaylistChat()
            playlist_data = playlist_chat.receive_message(text)
            return playlist_data

        elif prediction == 3:
            print("Analizando reseña...") 
            review_chat = ReviewChat()
            rating = review_chat.receive_message(text)
            return rating
        
        elif prediction == 4:
            print("Buscando la letra de la canción...") 
            lyrics_fetcher = SongLyricsFetcher()
            lyrics = lyrics_fetcher.get_lyrics(text)
            return lyrics


    def run(self):
        """
        Punto de entrada principal para ejecutar la clasificación de prompt.
        """
        print(f"Directorio actual: {os.getcwd()}")
        text = input("Introduzca su consulta:\n")
        prediction = self.classify_prompt(text)
        self.handle_prediction(prediction, text)


if __name__ == "__main__":
    classifier = PromptClassifier()
    classifier.run()
