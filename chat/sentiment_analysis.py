from transformers import pipeline

class SentimentAnalysis:
    def __init__(self):
        """
        Inicializa el analizador de sentimiento utilizando un modelo preentrenado de Hugging Face específico para español.
        """
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.analyzer = pipeline("sentiment-analysis", model=model_name)

    def analyze_sentiment(self, message):
        """
        Analiza el sentimiento predominante en el mensaje.
        :param message: El mensaje del usuario.
        :return: Un diccionario con el sentimiento predominante y la puntuación.
        """
        try:
            result = self.analyzer(message)[0]
            sentiment = result['label']  # Sentimiento predominante (1 estrella, 5 estrellas)
            score = result.get('score', None)  # Puntuación de confianza (si está disponible)

            if "1" in sentiment or "2" in sentiment:
                sentiment_category = "Negativo"
            elif "4" in sentiment or "5" in sentiment:
                sentiment_category = "Positivo"
            else:
                sentiment_category = "Neutro"

            return {"Estado de ánimo": sentiment_category, "Confianza": round(score, 2) if score else "N/A"}
        
        except Exception as e:
            return {"error": f"Error al analizar el sentimiento: {str(e)}"}


if __name__ == "__main__":
    analyzer = SentimentAnalysis()
    user_input = input("Introduce un mensaje en español para analizar su sentimiento: ")
    result = analyzer.analyze_sentiment(user_input)
    print("Resultado del análisis:", result)
