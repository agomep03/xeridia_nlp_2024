import discord
from discord.ext import commands
from apis.spotify_api import get_popular_songs
import config

from chat.recommend_chat import RecommendChat 
from chat.playlist_chat import PlaylistChat
from chat.consult_chat import ConsultantChat
from chat.review_chat import ReviewChat

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Creamos las instancias
recommend_chat = RecommendChat()
playlist_chat = PlaylistChat()
consult_chat = ConsultantChat()
review_chat = ReviewChat()

#Funcion para comprobar que el bot está conectado
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')


@bot.command()
async def topSongs(ctx):
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


@bot.command()
async def playlist(ctx, *, message: str):
    """Genera una playlist basada en los gustos o estado de ánimo del usuario."""
    try:
        # Llamar al método receive_message de la clase PlaylistChat
        playlist_data = playlist_chat.receive_message(message)
        
        # Enviar la respuesta formateada
        description = playlist_data.get("description", "Sin descripción.")
        title = playlist_data.get("title", "Título no disponible.")
        songs = playlist_data.get("list", [])
        
        if songs:
            song_list = "\n".join(songs)
            await ctx.send(f"**{title}**\n{description}\n\n**Canciones**:\n{song_list}")
        else:
            await ctx.send(f"**{title}**\n{description}\n\nNo se encontraron canciones para esta playlist.")
    
    except Exception as e:
        await ctx.send(f"Hubo un error al generar la playlist: {str(e)}")


@bot.command()
async def consult(ctx, *, message: str):
    """Responde preguntas relacionadas con música, artistas, géneros, etc."""
    try:
        # Llamar al método receive_message de la clase ConsultantChat
        response = consult_chat.receive_message(message)
        
        # Enviar la respuesta al canal
        await ctx.send(response)
    
    except Exception as e:
        await ctx.send(f"Hubo un error al responder la pregunta: {str(e)}")


@bot.command()
async def review(ctx, *, message: str):
    """Evalúa una reseña escrita por el usuario y devuelve una calificación en estrellas."""
    try:
        # Llamar al método receive_message de la clase ReviewChat para evaluar la reseña
        rating = review_chat.receive_message(message)

        # Enviar la calificación al canal
        await ctx.send(f"La reseña ha sido calificada con: {rating} estrellas")
    
    except Exception as e:
        await ctx.send(f"Hubo un error al evaluar la reseña: {str(e)}")


#Funcion para vaciar la conversacion
@bot.command()
async def clear(ctx):
    # Elimina los últimos 100 mensajes en el canal
    deleted = await ctx.channel.purge(limit=100)
    # Envia el mensajey  lo borra después de 3 segundos
    await ctx.send(f"Mensajes eliminados", delete_after=3)


bot.run(config.TOKEN_BOT)


        
