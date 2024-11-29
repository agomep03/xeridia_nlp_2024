import sys
import os

from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, API_VERSION, API_ENDPOINT, API_MODEL_MINI, API_MODEL


class PlaylistChat:

    def __init__(self):
        self.client = AzureOpenAI(
                api_version = API_VERSION,
                azure_endpoint = API_ENDPOINT,
                api_key = AZURE_OPENAI_API_KEY
        )

    def receive_message(self, message):
        completion = self.client.chat.completions.create(
                model = API_MODEL_MINI,
                messages=[
                    { "role":"user", "content":message },
                        ],
        )

        return completion.choices[0].message.content

