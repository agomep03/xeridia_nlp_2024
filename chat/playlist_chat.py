import re
import random

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, API_MODEL_MINI, API_MODEL

from utils.process_text import extract_keywords
from apis.spotify_api import get_playlists, get_playlists_items, get_song, song_save_by_user

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
    
    

    def receive_message(self, message):
        # Process text to extract keywords
        keywords = extract_keywords(message)
        keywords = keywords.split(" ")

        #TODO Add to keywords the user preferences (ej: pop)
        #TODO Add to keywords the sentimient of message 

        # Create songs lists
        numberSongsInPlaylist=2
        indexOfSearch = 3

        searchSongs = self.search_songs(keywords,numberSongsInPlaylist*indexOfSearch)
        songsNames = self.songs_names(searchSongs)
        print(songsNames)
        songs = self.select_songs(searchSongs, numberSongsInPlaylist)
        print(songs)
        songsNames = self.songs_names(songs)
        print(songsNames)

        #TODO Create playlist
        #create_spotify_playlist(songs)


        # Create response to user
        prompt="El usuario ha pedido: "+message+" Se le ha creado una playlist con las canciones: "+" ,".join(songsNames)
        response = self.create_response(prompt)
        return response

    
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
        
        print(puntuations)

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
        #TODO give puntuation

        puntuation += 100*song_save_by_user(songId)
        #puntuation += 10*artist_follow_by_user(songID)
        puntuation += get_song(song_id=songId)["popularity"]

        return puntuation



    def create_spotify_playlist(self, songs):
        for song in songs:
            #TODO spotify.create_playlist(songs)
            pass


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