import sys
import os

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT

class PlaylistChat:

    def __init__(self):
        self.client = AzureOpenAI(
                api_version = API_VERSION,
                azure_endpoint = API_ENDPOINT
        )

    def receive_message(self, message):
        print(message)

