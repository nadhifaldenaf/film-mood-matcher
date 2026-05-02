# matcher.py — semua logika Film Mood Matcher
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")
OW_KEY   = os.getenv("OPENWEATHER_API_KEY")

def get_location_from_ip():
    """Deteksi kota dan timezone berdasarkan IP address pengunjung."""
    try:
        res  = requests.get("http://ip-api.com/json/")
        data = res.json()
        if data["status"] == "success":
            return data["city"], data["timezone"]
        else:
            return "Bandung", "Asia/Jakarta"
    except:
        return "Bandung", "Asia/Jakarta"

# ─────────────────────────────────────────
# 1. CUACA
# ─────────────────────────────────────────
def get_weather(city="Bandung"):
    url    = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q"    : city,
        "appid": OW_KEY,
        "units": "metric",
        "lang" : "id"
    }
    data = requests.get(url, params=params).json()

    # Kalau kota tidak ditemukan, fallback ke Bandung
    if data.get("cod") != 200:
        data = requests.get(url, params={**params, "q": "Bandung"}).json()

    return {
        "kota"      : data["name"],
        "cuaca"     : data["weather"][0]["description"],
        "suhu"      : data["main"]["temp"],
        "kelembaban": data["main"]["humidity"],
        "kode_cuaca": data["weather"][0]["id"]
    }

# ─────────────────────────────────────────
# 2. MOOD
# ─────────────────────────────────────────
def get_mood(kode_cuaca, jam=None):
    if jam is None:
        jam = datetime.now().hour
    if 5 <= jam < 12:
        waktu = "pagi"
    elif 12 <= jam < 17:
        waktu = "siang"
    elif 17 <= jam < 21:
        waktu = "sore"
    else:
        waktu = "malam"

    if kode_cuaca in range(200, 300):
        return "tegang", waktu
    elif kode_cuaca in range(300, 600):
        return ("melankolis" if waktu == "malam" else "cozy"), waktu
    elif kode_cuaca == 800:
        return ("semangat" if waktu in ["pagi", "siang"] else "romantis"), waktu
    elif kode_cuaca in range(801, 900):
        return "santai", waktu
    elif kode_cuaca in range(700, 800):
        return "misterius", waktu
    else:
        return "santai", waktu

# ─────────────────────────────────────────
# 3. REKOMENDASI FILM
# ─────────────────────────────────────────
MOOD_TO_GENRE = {
    "tegang"    : 28,
    "melankolis": 18,
    "cozy"      : 35,
    "semangat"  : 12,
    "romantis"  : 10749,
    "santai"    : 16,
    "misterius" : 9648,
}

LANGUAGE_CODE = {
    "Hollywood" : "en",
    "Indonesia" : "id",
    "Korea"     : "ko",
}

MAX_DURASI = {
    "Santai (~1 jam)"     : 90,
    "Standar (~2 jam)"    : 130,
    "Bebas"               : 999,
}

def get_movies(mood, bahasa="Hollywood", durasi="Bebas", is_weekend=False):
    genre_id    = MOOD_TO_GENRE.get(mood, 35)
    lang_code   = LANGUAGE_CODE.get(bahasa, "en")
    max_minutes = MAX_DURASI.get(durasi, 999)

    # Weekend → tambah genre Adventure/Action supaya lebih seru
    if is_weekend and mood in ["santai", "cozy"]:
        genre_id = 28

    url    = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key"          : TMDB_KEY,
        "with_genres"      : genre_id,
        "sort_by"          : "popularity.desc",
        "vote_average.gte" : 7.0,
        "with_original_language": lang_code,
        "page"             : 1,
    }

    results = requests.get(url, params=params).json().get("results", [])

    films = []
    for movie in results:
        # Filter durasi (butuh call detail per film)
        detail_url = f"https://api.themoviedb.org/3/movie/{movie['id']}"
        detail     = requests.get(detail_url, params={"api_key": TMDB_KEY}).json()
        durasi_film = detail.get("runtime", 0)

        if durasi_film and durasi_film <= max_minutes:
            films.append({
                "judul"  : movie["title"],
                "rating" : movie["vote_average"],
                "tahun"  : movie["release_date"][:4] if movie["release_date"] else "N/A",
                "sinopsis": movie["overview"][:150] + "..." if movie["overview"] else "Tidak ada sinopsis.",
                "poster" : ("https://image.tmdb.org/t/p/w300" + movie["poster_path"]) if movie["poster_path"] else None,
                "durasi" : durasi_film,
            })

        if len(films) == 5:  # cukup 5 film
            break

    return films