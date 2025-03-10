import requests
import sqlite3
import json

# Variables de paginas
i=1 #pagina inicial
e=40 #numero de juegos x pagina
f=250 #pagina final

# Configuración
API_KEY = "d2de5157909940239e231629c51a38a1"
BASE_URL = "https://api.rawg.io/api/games?exclude_additions=true"
DB_NAME = "videojuegos_analysis.db"

# Función para obtener datos de RAWG API
def obtener_videojuegos(pagina=1, limite=40):

    params = {
        "key": API_KEY,
        "page": pagina,
        "page_size": limite
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Lanza una excepción si hay un error
        data = response.json()

        with open("respuesta_api.json", "w", encoding="utf-8") as archivo:
                    json.dump(data, archivo, indent=4, ensure_ascii=False)  # Guardar con formato legible

        if "results" in data:
            return data["results"]
        else:
            print("⚠️ No se encontraron resultados en la API.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud a la API: {e}")
        return []

# Función para guardar los datos en SQLite
def guardar_en_sqlite(videojuegos):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videojuegos (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            fecha_lanzamiento TEXT,
            desarrolladores TEXT, 
            distribuidor TEXT, 
            plataformas TEXT,
            generos TEXT,
            metacritic INTEGER,
            rating REAL,
            rating_numbers REAL,
            positive_rating_steam REAL,
            negative_rating_steam REAL,
            ratings_rawg TEXT,
            tiempo_jugado REAL,
            tags TEXT,
            jugadores_activos REAL,
            average_players REAL,
            ventas REAL,
            precio REAL
        )
    ''')

    for juego in videojuegos:
        app_id = get_steam_appid(juego.get("name"))
        steamspy=get_steamspy_data(app_id)

        if app_id == 0:
            app_id=juego.get("id")

        plataformas = ", ".join([p["platform"]["name"] for p in juego.get("platforms", [])]) if juego.get("platforms") else "No disponible"
        generos = ", ".join([g["name"] for g in juego.get("genres", [])]) if juego.get("genres") else "No disponible"
        ratings_rawg = ",".join([f"{f['title']}:{f['count']}" for f in juego.get("ratings",[])]) if juego.get("ratings") else "No disponible"
        tags = ", ".join([t["name"] for t in juego.get("tags", [])]) if juego.get("tags") else "No disponible"
        rating_numbers = juego.get("ratings_count", 0) + steamspy.get("positive", 0) + steamspy.get("negative" , 0)
       

        cursor.execute('''
            INSERT OR IGNORE INTO videojuegos (id, nombre, fecha_lanzamiento, desarrolladores , distribuidor, plataformas, generos, metacritic, 
            rating, rating_numbers, positive_rating_steam, negative_rating_steam, ratings_rawg, tiempo_jugado, tags, jugadores_activos, average_players, ventas, precio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (app_id, juego.get("name"), juego.get("released", "No disponible") , steamspy.get("developer","No disponible"),steamspy.get("publisher","No disponible"), 
              plataformas, generos, juego.get("metacritic", None), juego.get("rating", 0), rating_numbers, steamspy.get("positive"), steamspy.get("negative"), ratings_rawg, 
                juego.get("playtime", "No disponible"), tags, steamspy.get("median_forever", 0), steamspy.get("average_forever",  0), steamspy.get("owners", 0), steamspy.get("price", 0)))
        
    conn.commit()
    conn.close()


def get_steam_appid(game_name):
    url = "https://store.steampowered.com/api/storesearch"
    params = {
        "term" :game_name ,
        "l":"english",
        "cc":"us"
    }
    response = requests.get(url, params=params)

    if response.status_code==200:
        data2 = response.json()
        if data2 ["total"] > 0:
            return data2["items"][0]["id"]
    return None


def get_steamspy_data(app_id):
    url = f"https://steamspy.com/api.php?request=appdetails&appid={app_id}"
    response = requests.get(url)


    if response.status_code==200:
        return response.json()
    return {}


# Ejecutar
print("🔎 Obteniendo Datos...")
while i <= f:
    videojuegos = obtener_videojuegos(i,e)
    if videojuegos:
        guardar_en_sqlite(videojuegos)
        print(f"✅ Datos pagina {i}/{f} guardados en SQLite correctamente.")
    else:
        print("⚠️ No se guardaron datos debido a errores en la API.")
    i+=1
print("👌 Todos los datos guardados correctamente")
print("📜 Respuesta de la API guardada en 'respuesta_api.json'.")



input("Presiona Enter para salir...")


