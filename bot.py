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
from apis.spotify_api import get_popular_songs
import config

from chat.recommend_chat import RecommendChat 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Instancia de la clase RecommendChat
recommend_chat = RecommendChat()

#Funcion para comprobar que el bot está conectado
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')


@bot.command()
async def playlist(ctx):
    canciones = get_popular_songs()
    await ctx.send("Canciones populares:\n" + "\n".join(canciones))


@bot.command()
async def recommend(ctx, *, message: str):
    try:
        # Llamar a la función de recomendaciones de la clase RecommendChat
        recommendations = recommend_chat.receive_message(message)

        # Enviar las recomendaciones al canal
        await ctx.send(recommendations)
    
    except Exception as e:
        await ctx.send(f"Hubo un error al obtener las recomendaciones: {str(e)}")


#Funcion para vaciar la conversacion
@bot.command()
async def clean(ctx):
    # Elimina los últimos 100 mensajes en el canal
    deleted = await ctx.channel.purge(limit=100)
    # Envia el mensajey  lo borra después de 3 segundos
    await ctx.send(f"Mensajes eliminados", delete_after=3)


bot.run(config.TOKEN_BOT)


        
