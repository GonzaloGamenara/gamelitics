import requests
import sqlite3

# Configuración
API_KEY = "d2de5157909940239e231629c51a38a1"
BASE_URL = "https://api.rawg.io/api/games"
DB_NAME = "videojuegos_analysis.db"

# Función para obtener datos de RAWG API
def obtener_videojuegos(pagina=1, limite=5):
    params = {
        "key": API_KEY,
        "page": pagina,
        "page_size": limite
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Lanza una excepción si hay un error
        data = response.json()

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
            rating REAL,
            plataformas TEXT,
            generos TEXT,
            metacritic INTEGER
        )
    ''')

    for juego in videojuegos:
        plataformas = ", ".join([p["platform"]["name"] for p in juego.get("platforms", [])]) if juego.get("platforms") else "No disponible"
        generos = ", ".join([g["name"] for g in juego.get("genres", [])]) if juego.get("genres") else "No disponible"

        cursor.execute('''
            INSERT OR IGNORE INTO videojuegos (id, nombre, fecha_lanzamiento, rating, plataformas, generos, metacritic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (juego.get("id"), juego.get("name"), juego.get("released", "No disponible"), 
              juego.get("rating", 0), plataformas, generos, juego.get("metacritic", None)))

    conn.commit()
    conn.close()

# Ejecutar proceso
videojuegos = obtener_videojuegos()
if videojuegos:
    guardar_en_sqlite(videojuegos)
    print("✅ Datos guardados en SQLite correctamente.")
else:
    print("⚠️ No se guardaron datos debido a errores en la API.")
