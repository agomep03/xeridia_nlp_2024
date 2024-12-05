from transformers import pipeline

class SentimentAnalysis:
    def __init__(self):
        """
        Inicializa el analizador de sentimiento utilizando un modelo preentrenado de Hugging Face.
        """
        self.analyzer = pipeline("sentiment-analysis")

    def analyze_sentiment(self, message):
        """
        Analiza el sentimiento predominante en el mensaje.
        :param message: El mensaje del usuario.
        :return: Un diccionario con el sentimiento predominante y la puntuación.
        """
        try:
            # Analizamos el mensaje
            result = self.analyzer(message)[0]
            sentiment = result['label']  # Sentimiento predominante (e.g., POSITIVE, NEGATIVE, NEUTRAL)
            score = result['score']  # Puntuación de confianza
            return {"sentiment": sentiment, "score": score}
        except Exception as e:
            return {"error": f"Error al analizar el sentimiento: {str(e)}"}

# Prueba de la clase
if __name__ == "__main__":
    analyzer = SentimentAnalysis()
    user_input = input("Introduce un mensaje para analizar su sentimiento: ")
    result = analyzer.analyze_sentiment(user_input)
    print("Resultado del análisis:", result)
