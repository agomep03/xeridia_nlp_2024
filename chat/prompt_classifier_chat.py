import joblib
import os
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator, TransformerMixin
"""from song_lyrics import SongLyricsFetcher"""

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
        self.pipeline = joblib.load('process_input/pipeline_model.pkl')

        self.dictionary = {
            "artista": 0,
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

    def handle_prediction(self, prediction, text):
        """
        Maneja las acciones basadas en la predicción.

        Args:
            prediction (int): Índice de la predicción.
            text (str): Consulta introducida por el usuario.
        """
        if prediction == 0:
            print("artista")
        
        elif prediction == 1:
            print("consultar_informacion")

        elif prediction == 2:
            print("crear_playlist")

        elif prediction == 3:
            print("Reseñas")

        """elif prediction == 4:
            chat2 = SongLyricsFetcher()
            chat2.get_lyrics([text])"""

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
