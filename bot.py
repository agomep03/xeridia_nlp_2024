import discord
from discord.ext import commands
from apis.spotify_api import get_popular_songs, get_user_profile, get_top_artists
import config
import json

from chat.prompt_classifier_chat import PromptClassifier
from chat.sentence_transformer_wrapper import SentenceTransformerWrapper

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Creamos las instancias
prompt_classifier = PromptClassifier()

user_in_config = {}
user_responses = {}  # Controlar si el usuario ya ha respondido
ready_message_sent = False  #Controlar que el mensaje de los credenciales ya se ha enviado

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

    # Marcar que ya se envió el mensaje
    ready_message_sent = True


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

    # Comprobamos si el usuario ya está configurando las credenciales
    if message.author.id in user_in_config and user_in_config[message.author.id]:
        # Si el usuario está en el proceso de configuración, no procesamos otros mensajes
        return

    # Comprobamos si el usuario ya ha respondido
    if message.author.id in user_responses:
        # Procesar el mensaje con la clase PromptClassifier
        prediction = prompt_classifier.classify_prompt(message.content)  # Clasificar el mensaje

        '''
        # Opcional: responder al usuario según la acción
        if prediction == 0:
            await message.channel.send("Generando recomendaciones musicales...")
        elif prediction == 1:
            await message.channel.send("Buscando información sobre...")
        elif prediction == 2:
            await message.channel.send("Generando una playlist...")
        elif prediction == 3:
            await message.channel.send("Analizando reseña...")
        elif prediction == 4:
            await message.channel.send("Buscando la letra de la canción...")
        '''

        respuesta = await prompt_classifier.handle_prediction(prediction, message.content, message)  # Manejar la predicción
        await message.channel.send(respuesta)

    else:
        # Si el mensaje es "sí" o "no", registramos la respuesta
        if message.content.lower() == "sí" or message.content.lower() == "si":
            user_responses[message.author.id] = "sí"
            user_in_config[message.author.id] = True  # Marcar que está en configuración
            await message.channel.send(f"{message.author.mention}, ¡Genial! Ahora vamos a configurar tus credenciales de Spotify.")
            await logIn(message)  # Llamamos a la función para manejar el login

        elif message.content.lower() == "no":
            user_responses[message.author.id] = "no"
            user_in_config[message.author.id] = True  # Marcar que está en configuración
            await message.channel.send(f"{message.author.mention}, por favor ve a https://developer.spotify.com/dashboard/applications (recomendamos usarlo en Google Chrome) para obtener tus claves. Una vez dentro, sigue las instrucciones que te he enviado por privado.")
            await info_credential(message)
            await logIn(message)  # Llamamos a la función para manejar el logins

        else:
            await message.channel.send("Por favor, responde con 'sí' o 'no'.")

    # Procesar otros comandos
    await bot.process_commands(message)


async def info_credential(message):
    """
    Envia las instrucciones detalladas sobre cómo obtener las credenciales de Spotify.
    """
    instructions = (
        "Haga clic en el botón de inicio de sesión ubicado en la esquina superior derecha.\n"
        "Introduzca sus datos (correo electrónico y contraseña).\n"
        "Una vez haya iniciado sesión, haga clic en su perfil y acceda al panel de control (Dashboard). Será necesario aceptar los términos y condiciones.\n"
        "Es probalbe que le pida verificar su dirección de correo electrónico antes de poder continuar.\n"
        "Una vez verificada su cuenta, tendrá la opción de crear una nueva aplicación. Haga clic en esta opción.\n"
        "Se abrirá un formulario en el cual deberá ingresar los siguientes datos:\n"
        "- Nombre de la aplicación: MiBotSpotify\n"
        "- Descripción de la aplicación: Aplicación para integrar la API de Spotify con un bot de Discord, permitiendo a los usuarios interactuar con sus listas de reproducción, canciones favoritas y otros datos relacionados con su cuenta de Spotify.\n"
        "- Redirect URIs: http://localhost:8888/callback/ (haga clic en 'Add').\n"
        "- APIs utilizadas: Web API.\n"
        "Marque la casilla que indica que entiende y acepta los términos y condiciones.\n"
        "Haga clic en 'SAVE'.\n"
        "Deberá esperar unos minutos hasta que el sistema le permita continuar.\n"
        "Una vez haya podido continuar, será redirigido a la página principal (Home). Desde allí, haga clic en el botón de 'Settings' en la esquina superior derecha.\n"
        "En esa sección, encontrará el Client ID, y justo debajo, el Client Secret (deberá hacer clic en 'Mostrar'). Más abajo, también encontrará los Redirect URIs.\n"
        "A continuacíon vuelve al bot e introduce '!login', y dile que 'si' tienes los credenciales, luego te los irá pidiendo."
    )

    # Enviar instrucciones paso a paso al usuario
    await message.author.send(instructions)


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
        client_id = await bot.wait_for('message', check=check, timeout=3600.0)
        
        # Preguntar por el CLIENT_SECRET
        await message.channel.send("¿Cuál es tu SPOTIFY_CLIENT_SECRET?")
        client_secret = await bot.wait_for('message', check=check, timeout=3600.0)

        # Preguntar por el REDIRECT_URI
        await message.channel.send("¿Cuál es tu SPOTIFY_REDIRECT_URI?")
        redirect_uri = await bot.wait_for('message', check=check, timeout=3600.0)

        # Guardar las credenciales en un archivo JSON
        credentials = {
            "SPOTIFY_CLIENT_ID": client_id.content,
            "SPOTIFY_CLIENT_SECRET": client_secret.content,
            "SPOTIFY_REDIRECT_URI": redirect_uri.content
        }

        with open(CREDENTIALS_FILE, "w") as file:
            json.dump(credentials, file)
        
        # Eliminar los mensajes relacionados con el proceso de configuración
        await message.channel.purge(limit=8)
        
        # Resetear el flag indicando que el proceso ha terminado
        user_in_config[message.author.id] = False

        # Aquí puedes continuar con la lógica después de guardar las credenciales
        await message.channel.send("¡Credenciales de Spotify guardadas con éxito!")
        await message.channel.send("Estoy preparado para ayudarte en lo que necesites.")
        
    except Exception as e:
        await message.channel.send(f"Hubo un error al configurar las credenciales. {str(e)}")


# Ruta del archivo para guardar credenciales
CREDENTIALS_FILE = "spotify_credentials.json"

bot.run(config.TOKEN_BOT)
