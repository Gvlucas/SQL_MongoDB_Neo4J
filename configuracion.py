#CONFIGURACIÓN INICIAL DE LOS DATOS

#A modificar por el profesor

PATHS = {
    "video_games": 'Video_Games_5.json',
    "digital_music": 'Digital_Music_5.json',
    "musical_instruments": 'Musical_Instruments_5.json',
    "toys_games": 'Toys_and_Games_5.json'
}

MYSQL_CONFIG = {
    "host": 'localhost',
    "user": 'Lucia',  #Añadir user
    "password": 'bAsesDeD4tos26', #Añadir contraseña
    "database": "Basic_Information"
}

MONGO_CONFIG = {
    "host": "mongodb://localhost:27017",
    "database": 'Reviews_Text',
    "collections": {
        "video_games": "Videogames",
        "digital_music": "Music",
        "musical_instruments": "Instruments",
        "toys_games": "Toys_Games"
    }
}