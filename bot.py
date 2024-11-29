# TODO: start bot

#Conect with discord

#Comect spotify api in discord

#init: prompt_classifier, recommend_chat, consult_chat, playlist_chat

#For each message in discord:
    #process input

    #case recommend:
        #recommend_chat.receive_message()

    #case consult:
        #consult_chat.receive_message()

    #case create playlist:
        #playlist_chat.receive_message()
        #spotify.createPlaylist(message[0])
        #message=message[1]

    #discord.output(message)


import discord
from discord.ext import commands
from apis.spotify_api import obtener_canciones_populares
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def playlist(ctx):
    canciones = obtener_canciones_populares()
    await ctx.send("Canciones populares:\n" + "\n".join(canciones))

bot.run(config.TOKEN_BOT)


        
