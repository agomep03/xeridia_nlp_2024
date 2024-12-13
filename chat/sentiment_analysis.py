from transformers import pipeline


# Usa meramente NLP (es bastante exacto pero la categoría de sentimiento es más general)
class SentimentAnalysis:
    def __init__(self):
        """
        Inicializa el analizador de sentimiento utilizando un modelo preentrenado de Hugging Face específico para español.
        """
        # Modelo multilingüe compatible con análisis de sentimientos en español
        model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.analyzer = pipeline("sentiment-analysis", model=model_name)

    def analyze_sentiment(self, message):
        """
        Analiza el sentimiento predominante en el mensaje.
        :param message: El mensaje del usuario.
        :return: Un diccionario con el sentimiento predominante y la puntuación.
        """
        try:
            # Utiliza el modelo preentrenado para analizar el sentimiento del mensaje
            result = self.analyzer(message)[0]
            sentiment = result['label']  # Sentimiento predominante (e.g., 1 estrella, 5 estrellas)
            score = result.get('score', None)  # Puntuación de confianza (si está disponible)

            # Clasifica el sentimiento en categorías más específicas
            if "1" in sentiment or "2" in sentiment:
                sentiment_category = "Negativo"
            elif "4" in sentiment or "5" in sentiment:
                sentiment_category = "Positivo"
            else:
                sentiment_category = "Neutro"

            # Retorna el resultado con la categoría específica y el puntaje del modelo
            return {"Estado de ánimo": sentiment_category, "Confianza": round(score, 2) if score else "N/A"}
        
        except Exception as e:
            return {"error": f"Error al analizar el sentimiento: {str(e)}"}


# Prueba de la clase
if __name__ == "__main__":
    analyzer = SentimentAnalysis()
    user_input = input("Introduce un mensaje en español para analizar su sentimiento: ")
    result = analyzer.analyze_sentiment(user_input)
    print("Resultado del análisis:", result)
