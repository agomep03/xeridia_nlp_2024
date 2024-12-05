import joblib
import os

print(os.getcwd())
pipeline = joblib.load('process_input/text_classification_pipeline.pkl')

dictionary = {"artista": 0, "consultar_informacion": 1, "crear_playlist": 2}

text = input("Introduzca su consulta:\n")

predictions = pipeline.predict([text])
print("Predicciones:", predictions)

