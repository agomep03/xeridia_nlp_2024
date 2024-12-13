import re
import random
import joblib

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, API_MODEL_MINI, API_MODEL

from utils.process_text import extract_keywords
from apis.spotify_api import get_playlists, get_playlists_items, get_song, song_save_by_user, artist_followed_by_user, create_playlist
from chat.sentiment_analysis import SentimentAnalysis

def delete_duplicate_songs(songs):
    return list(dict.fromkeys(songs))


def parse_response(response):
        description_match = re.search(r"\[DESCRIPTION\]:\s*(.*?)\n", response)
        description = description_match.group(1) if description_match else ""


        title_match = re.search(r"\[TITLEPLAYLIST\]:\s*(.*?)\n", response)
        title = title_match.group(1) if title_match else ""

        songs_match = re.search(r"\[PLAYLIST\]:\s*(.*?)\s*$", response, re.DOTALL)
        songs = songs_match.group(1).strip() if songs_match else ""
        list_of_songs = songs.split(", ")
        
        return {"description":description, "title":title, "list":list_of_songs}

MUSICAL_GENDERS = ["Pop", "Rock","Hip-Hop","EDM","Indie","Jazz","Soul","Reggaetón","Música Clásica","Folk","R&B","Canciones acústicas","Lo-fi",
"Música instrumental","Música ambiental","Música latina","Funk","Música tropical","Bossa Nova","Dance"]

class PlaylistChat:

    def __init__(self):
        self.client = AzureOpenAI(
                api_version = API_VERSION,
                azure_endpoint = API_ENDPOINT,
                api_key = AZURE_OPENAI_API_KEY
        )
        self.systemMessage = { "role":"system", 
                            "content":"Te voy a pasar canciones de una playlist, la intención del usuario con la playlist y tienes que devolver este formato: "
                            "[DESCRIPTION]: <descripción general de la playlist>. "
                            "[TITLEPLAYLIST]: <título de la playlist>. "
                            "[PLAYLIST]: <canción 1>, <canción 2>, <canción 3>, ..."}
        self.sentiment = SentimentAnalysis()

        self.musical_gender_model, self.musical_gender_vectorizer = joblib.load('utils/musical_gender_model.pkl')
    

    def receive_message(self, message):
        # Process text to extract keywords
        keywords = extract_keywords(message)
        keywords = keywords.split(" ")

        for word in self.search_musical_gender(" ".join(keywords)):
            keywords.append(word)
                    
        # Add sentimient
        sentiment = self.sentiment.analyze_sentiment(message=message)
        if 'Estado de ánimo' in sentiment:
            keywords.append(sentiment['Estado de ánimo'])

        # Create songs lists
        numberSongsInPlaylist=20
        indexOfSearch = 3

        searchSongs = self.search_songs(keywords,numberSongsInPlaylist*indexOfSearch)
        songs = self.select_songs(searchSongs, numberSongsInPlaylist)
        songsNames = self.songs_names(songs)

        prompt="El usuario ha pedido: "+message+" Se le ha creado una playlist con las canciones: "+" ,".join(songsNames)
        response = self.create_response(prompt)

        print(response)

        create_playlist(songs=songs, title=response['title'], description=response['description'])

        return response
    
    def search_musical_gender(self, message):
        embbeded = self.musical_gender_vectorizer.transform([message])
        preds = self.musical_gender_model.predict(embbeded)[0]
        genders = []
        for i in range(len(preds)):
            if preds[i]:
                genders.append(MUSICAL_GENDERS[i])

        return genders

    
    def search_songs(self, keywords, numberSongsToSearch=60):
        songs = []
        lenNewKeywords = len(keywords)//2

        while len(songs) < numberSongsToSearch:
            newKeywords = keywords.copy()
            random.shuffle(newKeywords)
            newKeywords = newKeywords[:lenNewKeywords]
            query = " ".join(newKeywords)
            
            playlists = get_playlists(query, limit=2, property='id')
            for playlist in playlists:
                obtainSongs = [playlist]
                obtainSongs = get_playlists_items(playlist)
                songs += obtainSongs
            
            songs = delete_duplicate_songs(songs)

        return songs



    def select_songs(self, songs, numberSongsInPlaylist):
        assert len(songs) > numberSongsInPlaylist
        
        puntuations = []

        for song in songs:
            puntuations.append([song, self.get_puntuation(song)])
        
        sortedSongs = sorted(puntuations, key=lambda x:x[1], reverse=True)

        filterSongs = [x[0] for x in sortedSongs[:numberSongsInPlaylist]]

        return filterSongs

    def songs_names(self, songs):
        songsNames = []
        for song_id in songs:
            newSong = get_song(song_id)
            if newSong is not None:
                songsNames.append(newSong['name'])
        return songsNames


    def get_puntuation(self, songId):
        puntuation = 0

        try:
            puntuation += 100*song_save_by_user(songId)
            song = get_song(songId)
            if song is not None:
                puntuation += 100*artist_followed_by_user(song['artists'][0]['id'])
                puntuation += song["popularity"]
        except:
            puntuation = -100

        return puntuation



    def create_response(self, message):
        completion = self.client.chat.completions.create(
                model = API_MODEL,
                messages=[
                    self.systemMessage,
                    { "role":"user", "content":message },
                        ],
        )


        response = completion.choices[0].message.content
        response = parse_response(response)
        return response