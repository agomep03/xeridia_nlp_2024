import os
from dotenv import load_dotenv

AZURE_OPENAI_API_KEY = "7MoKzuuPAla0Cl3RYSM2aHjTAmkVopeVC4VhHCCdLPGDbAg0Vk4OJQQJ99AKACYeBjFXJ3w3AAABACOGrjrr"
API_VERSION = "2024-10-01-preview"
API_ENDPOINT = "https://practicas-2024.openai.azure.com/"
API_LOCATION = "eastus"

API_MODEL_MINI = "gpt-4o-mini"
API_MODEL = "gpt-4o"

#Token del bot de Discord
TOKEN_BOT = "MTMxMTk2MDAyNDU4NjkxNTg1MQ.GfklIE.-vBFrzIY3eRqrPgKy1IgKWF7nbNUaiuERLzVJY"

#Credenciales Spotify
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

#Token de Genius
TOKEN_GENIUS = "I7SU1zO8Rlc7mAuJJcyAuYxuHoj65nM_MBUwftLS8pPY3oEfwr5xjrqgFGG_y0PN"