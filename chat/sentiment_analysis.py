from transformers import pipeline


# Utiliza NLP pero principalmente utiliza un diccionario de palabras clave (más exacto)
class SentimentAnalysis:
    def __init__(self):
        """
        Inicializa el analizador de sentimiento utilizando un modelo preentrenado de Hugging Face.
        """
        self.analyzer = pipeline("sentiment-analysis")
        
        # Palabras clave para encasillar el mensaje en una categoría específica
        self.keywords = {
            "Motivado": ["motivado", "inspirado", "entusiasmado", "energético", "positivo"],
            "Alegre": ["feliz", "contento", "alegre", "optimista", "emocionado"],
            "Relax": ["relajado", "tranquilo", "calmo", "sereno", "chill"],
            "Depresivo": ["depresivo", "desesperado", "sin esperanza", "vacío", "llorar"],
            "Triste": ["triste", "melancólico", "desanimado", "desdichado", "desolado"],
            "Sentimental": ["nostálgico", "sensible", "emocional", "sentimental"]
        }

    def analyze_sentiment(self, message):
        """
        Analiza el sentimiento predominante en el mensaje.
        :param message: El mensaje del usuario.
        :return: Un diccionario con el sentimiento predominante y la puntuación.
        """
        try:
            # Comprobamos si el mensaje contiene alguna palabra clave
            sentiment_category = self.check_for_keywords(message)
            if sentiment_category:
                return {"sentiment": sentiment_category, "score": "N/A"}  # No analizamos el score, ya que es un match por palabra clave

            # Si no contiene palabras clave, procedemos con el análisis del modelo
            result = self.analyzer(message)[0]
            sentiment = result['label']  # Sentimiento predominante (e.g., POSITIVE, NEGATIVE, NEUTRAL)
            score = result['score']  # Puntuación de confianza

            # Asignamos un sentimiento más específico según el score
            if sentiment == "POSITIVE":
                if score >= 0.75:
                    sentiment_category = "Motivado"
                elif score >= 0.5:
                    sentiment_category = "Alegre"
                else:
                    sentiment_category = "Relax"
            elif sentiment == "NEGATIVE":
                if score >= 0.75:
                    sentiment_category = "Depresivo"
                elif score >= 0.5:
                    sentiment_category = "Triste"
                else:
                    sentiment_category = "Sentimental"
            else:
                sentiment_category = "Neutro"

            # Retornar el resultado
            return {"Estado de ánimo": sentiment_category}
        
        except Exception as e:
            return {"error": f"Error al analizar el sentimiento: {str(e)}"}

    def check_for_keywords(self, message):
        """
        Verifica si el mensaje contiene alguna palabra clave que corresponde a una categoría de sentimiento.
        :param message: El mensaje del usuario.
        :return: La categoría correspondiente o None si no hay coincidencia.
        """
        message_lower = message.lower()  # Convertir el mensaje a minúsculas para hacer la búsqueda más flexible
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return category
        return None


# Prueba de la clase
if __name__ == "__main__":
    analyzer = SentimentAnalysis()
    user_input = input("Introduce un mensaje para analizar su sentimiento: ")
    result = analyzer.analyze_sentiment(user_input)
    print("Resultado del análisis:", result)
