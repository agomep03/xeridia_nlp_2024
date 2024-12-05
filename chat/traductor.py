import pandas as pd
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT

class ReviewTranslator:
    def __init__(self):
        # Configurar el cliente de OpenAI
        self.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=API_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY
        )

    def translate_review(self, review_text):
        # Este es el prompt para traducir la reseña
        prompt = f"""
        Traducir el siguiente texto al español:
        "{review_text}"
        """

        try:
            # Llama a la API de OpenAI para traducir el texto
            chat_completion = self.client.chat.completions.create(
                model="gpt-4",  # O el modelo que estés utilizando
                messages=[
                    {"role": "system", "content": "Eres un traductor experto."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.5,
            )

            # Obtén la traducción
            translated_review = chat_completion.choices[0].message.content.strip()

            return translated_review

        except Exception as e:
            return f"Error al traducir: {str(e)}"

    def translate_reviews_in_csv(self, input_csv, output_csv):
        # Leer el archivo CSV
        df = pd.read_csv(input_csv)

        # Verificar que la columna 'Review' exista en el archivo
        if 'Review' not in df.columns:
            return "La columna 'Review' no se encuentra en el archivo CSV."

        # Traducir cada reseña en la columna 'Review' y agregarla a una nueva columna 'Review_Traducida'
        df['Review_Traducida'] = df['Review'].apply(self.translate_review)

        # Guardar el archivo con las reseñas traducidas
        df.to_csv(output_csv, index=False, encoding='utf-8')

        return f"Archivo con las reseñas traducidas guardado en: {output_csv}"


# Crear una instancia del traductor
translator = ReviewTranslator()

# Llamar a la función para traducir las reseñas
input_file = r"C:\Users\adria\OneDrive\Escritorio\UNI\4º\PE\xeridia_nlp_2024\chat\music_album_reviews.csv"
output_file = r"C:\Users\adria\OneDrive\Escritorio\UNI\4º\PE\xeridia_nlp_2024\chat\archivo_traducido.csv"

print("CSV leido correctamente")

# Traducir y guardar el nuevo archivo
result = translator.translate_reviews_in_csv(input_file, output_file)

# Imprimir el resultado
print("Traducido")
