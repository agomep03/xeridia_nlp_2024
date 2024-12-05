import joblib
import os
from chat.song_lyrics import SongLyricsFetcher

print(os.getcwd())
pipeline = joblib.load('process_input/text_classification_pipeline.pkl')

dictionary = {"artista": 0, "consultar_informacion": 1, "crear_playlist": 2}

text = input("Introduzca su consulta:\n")

predictions = pipeline.predict([text])
print("Predicciones:", predictions)

if(predictions[0] == 0):
    print("artista")
    
elif(predictions[0] == 1):
    print("consultar_informacion")

elif(predictions[0] == 2):
    print("crear_playlist")

elif(predictions[0] == 3):
    SongLyricsFetcher.get_lyrics([text])

