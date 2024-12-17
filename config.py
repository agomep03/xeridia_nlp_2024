import os
from dotenv import load_dotenv
import json

AZURE_OPENAI_API_KEY = "7MoKzuuPAla0Cl3RYSM2aHjTAmkVopeVC4VhHCCdLPGDbAg0Vk4OJQQJ99AKACYeBjFXJ3w3AAABACOGrjrr"
API_VERSION = "2024-10-01-preview"
API_ENDPOINT = "https://practicas-2024.openai.azure.com/"
API_LOCATION = "eastus"

API_MODEL_MINI = "gpt-4o-mini"
API_MODEL = "gpt-4o"

#Token del bot de Discord
TOKEN_BOT = "MTMxMTk2MDAyNDU4NjkxNTg1MQ.GfklIE.-vBFrzIY3eRqrPgKy1IgKWF7nbNUaiuERLzVJY"

# Ruta del archivo JSON con las credenciales
CREDENTIALS_FILE = "spotify_credentials.json"

# Leer credenciales desde el archivo JSON
if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "r") as file:
        credentials = json.load(file)
    CLIENT_ID = credentials.get("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = credentials.get("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = credentials.get("SPOTIFY_REDIRECT_URI")
else:
    raise FileNotFoundError(f"El archivo {CREDENTIALS_FILE} no existe. Por favor, verifica su ubicación.")

#Token de Genius
TOKEN_GENIUS = "oThFM0mHc0HegQJDNGIOvgGN1VV_b-ccpaxWautvzKxKF4uVnQrbJU8fIx3-xcTq"