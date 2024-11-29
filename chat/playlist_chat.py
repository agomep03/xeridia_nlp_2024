import re
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, API_MODEL_MINI, API_MODEL

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
                            "content":"Eres un asistente de creación de playlists. Dependiendo de los gustos del usuario y cómo se sienta tienes que generarle una playlist. La respuesta tiene que ser en el siguiente formato: "
                            "[DESCRIPTION]: <descripción general de la playlist>. "
                            "[TITLEPLAYLIST]: <título de la playlist>. "
                            "[PLAYLIST]: <canción 1>, <canción 2>, <canción 3>, ..."}
    
    

    def receive_message(self, message):
        completion = self.client.chat.completions.create(
                model = API_MODEL_MINI,
                messages=[
                    self.systemMessage,
                    { "role":"user", "content":message },
                        ],
        )


        response = completion.choices[0].message.content
        response = parse_response(response)
        return response

    


