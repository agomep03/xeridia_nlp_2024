import discord
from discord.ext import commands
from apis.spotify_api import get_popular_songs, get_user_profile, get_top_artists
import config
import json

from chat.recommend_chat import RecommendChat 
from chat.playlist_chat import PlaylistChat
from chat.consult_chat import ConsultantChat
from chat.review_chat import ReviewChat
from spotipy.oauth2 import SpotifyOAuth

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Creamos las instancias
recommend_chat = RecommendChat()
playlist_chat = PlaylistChat()
consult_chat = ConsultantChat()
review_chat = ReviewChat()


has_spotify_credentials = {}
user_responses = {}  # Controlar si el usuario ya ha respondido


# Evento que se ejecuta cuando el bot está listo
@bot.event
async def on_ready():
    """
    Se ejecuta automáticamente cuando el bot se conecta a Discord.
    Muestra en la consola un mensaje indicando que el bot está listo.
    """
    print(f'Bot conectado como {bot.user}')
    channel = bot.get_channel(1311959894219427843)  # Reemplaza por el ID del canal
    if channel:
        await channel.send("¿Tienes tus claves de Spotify listas? (sí/no)")  
    else:
        print("No se pudo encontrar el canal.")

# Evento que se ejecuta cuando el bot recibe un mensaje
@bot.event
async def on_message(message):
    """
    Se ejecuta cada vez que el bot recibe un mensaje.
    Aquí se gestionan las respuestas a la pregunta sobre Spotify.
    """
    # Evitar que el bot responda a sus propios mensajes
    if message.author == bot.user:
        return

    # Comprobamos si el usuario ya ha respondido
    if message.author.id in user_responses:
        return  # Si ya ha respondido, no hacemos nada más.

    # Si el mensaje es "sí" o "no", registramos la respuesta
    if message.content.lower() == "sí" or message.content.lower() == "si":
        user_responses[message.author.id] = "sí"
        await message.channel.send(f"{message.author.mention}, ¡Genial! Ahora vamos a configurar tus credenciales de Spotify.")
        await logIn(message)  # Llamamos a la función para manejar el login
    elif message.content.lower() == "no":
        user_responses[message.author.id] = "no"
        await message.channel.send(f"{message.author.mention}, por favor ve a https://developer.spotify.com/dashboard/applications para obtener tus claves.")
    else:
        await message.channel.send("Por favor, responde con 'sí' o 'no'.")

    # Procesar otros comandos
    await bot.process_commands(message)

# Función para iniciar el proceso de configuración de las credenciales de Spotify
@bot.command()
async def logIn(message):
    """
    Inicia el proceso para configurar las credenciales de Spotify.
    """
    await message.channel.send("Por favor, responde a las siguientes preguntas para configurar las credenciales de Spotify.")

    def check(m):
        return m.author == message.author and m.channel == message.channel

    try:
        # Preguntar por el CLIENT_ID
        await message.channel.send("¿Cuál es tu SPOTIFY_CLIENT_ID?")
        client_id = await bot.wait_for('message', check=check, timeout=60.0)
        
        # Preguntar por el CLIENT_SECRET
        await message.channel.send("¿Cuál es tu SPOTIFY_CLIENT_SECRET?")
        client_secret = await bot.wait_for('message', check=check, timeout=60.0)

        # Preguntar por el REDIRECT_URI
        await message.channel.send("¿Cuál es tu SPOTIFY_REDIRECT_URI?")
        redirect_uri = await bot.wait_for('message', check=check, timeout=60.0)

        # Guardar las credenciales en un archivo JSON
        credentials = {
            "SPOTIFY_CLIENT_ID": client_id.content,
            "SPOTIFY_CLIENT_SECRET": client_secret.content,
            "SPOTIFY_REDIRECT_URI": redirect_uri.content
        }

        with open(CREDENTIALS_FILE, "w") as file:
            json.dump(credentials, file)
        
        # Eliminar los mensajes relacionados con el proceso de configuración
        await message.channel.purge(limit=7)
        
        await message.channel.send("¡Credenciales de Spotify guardadas con éxito!")
        await message.channel.send("Estoy preparado para ayudarte en lo que necesites")
    
    except Exception as e:
        await message.channel.send(f"Hubo un error al configurar las credenciales: {str(e)}")


# Ruta del archivo para guardar credenciales
CREDENTIALS_FILE = "spotify_credentials.json"


@bot.command()
async def topSongs(ctx):
    """Muestra una lista de canciones populares obtenidas de Spotify."""    
    canciones = get_popular_songs()
    await ctx.send("Canciones populares:\n" + "\n".join(canciones))


@bot.command()
async def recommend(ctx, *, message: str):
    """Genera recomendaciones musicales basadas en el mensaje proporcionado por el usuario."""
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


@bot.command()
async def profile(ctx):
    """Obtiene el perfil básico del usuario de Spotify."""
    user_info = get_user_profile()
    if "error" in user_info:
        await ctx.send(f"Error al obtener el perfil: {user_info['error']}")
    else:
        await ctx.send(f"Perfil de Spotify:\n"
                       f"Nombre: {user_info['name']}\n"
                       f"ID: {user_info['id']}\n"
                       f"Email: {user_info['email']}\n"
                       f"Seguidores: {user_info['followers']}\n"
                       f"País: {user_info['country']}\n"
                       f"Producto: {user_info['product']}")


@bot.command()
async def topArtists(ctx):
    """Obtiene los artistas más escuchados del usuario."""
    top_artists = get_top_artists()
    if "error" in top_artists:
        await ctx.send(f"Error al obtener los artistas: {top_artists['error']}")
    else:
        await ctx.send(f"Artistas más escuchados:\n" + "\n".join(top_artists))

#Funcion para vaciar la conversacion
@bot.command()
async def clear(ctx):
    """
    Borra hasta 100 mensajes recientes en el canal actual.
    Envía un mensaje de confirmación y lo elimina después de 3 segundos.
    """
    # Elimina los últimos 100 mensajes en el canal
    deleted = await ctx.channel.purge(limit=100)
    # Envia el mensajey  lo borra después de 3 segundos
    await ctx.send(f"Mensajes eliminados", delete_after=3)


bot.run(config.TOKEN_BOT)


        
