# app.py — tampilan web Film Mood Matcher
import streamlit as st
from datetime import datetime
from matcher import get_weather, get_mood, get_movies, get_city_from_ip

# ─────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Film Mood Matcher",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Film Mood Matcher")
st.caption("Rekomendasi film berdasarkan cuaca, waktu, dan seleramu")

# ─────────────────────────────────────────
# SIDEBAR — PREFERENSI USER
# ─────────────────────────────────────────

city = get_city_from_ip()

with st.sidebar:
    st.header("⚙️ Preferensi")

    bahasa = st.selectbox(
        "Bahasa Film",
        ["Hollywood", "Indonesia", "Korea"]
    )

    durasi = st.selectbox(
        "Durasi yang kamu punya",
        ["Santai (~1 jam)", "Standar (~2 jam)", "Bebas"]
    )

    st.divider()
    st.caption(f"📍 Lokasi: {city}")
    st.caption(f"🕐 Waktu: {datetime.now().strftime('%H:%M')}")

# ─────────────────────────────────────────
# MAIN — CUACA & MOOD
# ─────────────────────────────────────────
city = get_city_from_ip()

with st.spinner(f"📡 Mengambil data cuaca {city}..."):
    cuaca = get_weather(city)

kode_cuaca = cuaca["kode_cuaca"]
mood, waktu = get_mood(kode_cuaca)

# Tampilkan info cuaca
col1, col2, col3 = st.columns(3)
col1.metric("🌤️ Cuaca", cuaca["cuaca"].title())
col2.metric("🌡️ Suhu", f"{cuaca['suhu']}°C")
col3.metric("💧 Kelembaban", f"{cuaca['kelembaban']}%")

st.divider()

# Tampilkan mood
is_weekend = datetime.now().weekday() >= 5  # Sabtu = 5, Minggu = 6
hari       = "Weekend 🎉" if is_weekend else "Weekday"

st.markdown(f"### 🎭 Mood kamu: `{mood.upper()}`")
st.markdown(f"**Waktu:** {waktu.title()} &nbsp;|&nbsp; **Hari:** {hari}")

st.divider()

# ─────────────────────────────────────────
# MAIN — REKOMENDASI FILM
# ─────────────────────────────────────────
st.markdown("### 🍿 Rekomendasi Film")

with st.spinner("🎬 Mencari film untukmu..."):
    films = get_movies(mood, bahasa, durasi, is_weekend)

if not films:
    st.warning("Tidak ada film yang cocok dengan filtermu. Coba ubah preferensi di sidebar!")
else:
    for film in films:
        with st.container():
            col_poster, col_info = st.columns([1, 3])

            with col_poster:
                if film["poster"]:
                    st.image(film["poster"], width=120)
                else:
                    st.markdown("🎞️ No Poster")

            with col_info:
                st.markdown(f"#### {film['judul']} ({film['tahun']})")
                st.markdown(f"⭐ {film['rating']} &nbsp;|&nbsp; ⏱️ {film['durasi']} menit")
                st.caption(film["sinopsis"])

        st.divider()