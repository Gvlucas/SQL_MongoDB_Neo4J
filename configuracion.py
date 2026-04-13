#CONFIGURACIÓN INICIAL DE LOS DATOS

#A modificar por el profesor

PATHS = {
    "video_games": 'Video_Games_5.json',
    "digital_music": 'Digital_Music_5.json',
    "musical_instruments": 'Musical_Instruments_5.json',
    "toys_games": 'Toys_and_Games_5.json'
}
PATHS2={
    "sports_outdoors":"Sports_and_Outdoors_5.json"
}

MYSQL_CONFIG = {
    "host": 'localhost',
    "user": 'root',  #Añadir user
    "password": '', #Añadir contraseña
    "database": "Basic_Information"
}

MONGO_CONFIG = {
    "host": "mongodb://localhost:27017",
    "database": 'Reviews_Text',
    "collections": {
        "video_games": "Videogames",
        "digital_music": "Music",
        "musical_instruments": "Instruments",
        "toys_games": "Toys_Games",
    }
}
MONGO_CONFIG2 = {
    "host": "mongodb://localhost:27017",
    "database": 'Reviews_Text',
    "collections": {
        "sports_outdoors": "Sports_Outdoors"
    }
}

NEO4J_CONFIG ={
    "uri": "neo4j://localhost:7687",
    "user": "neo4j",
    "password": ""
}