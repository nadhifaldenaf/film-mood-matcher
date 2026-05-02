# app.py — tampilan web Film Mood Matcher
import streamlit as st
from datetime import datetime
import pytz
from matcher import get_weather, get_mood, get_movies, get_location_from_ip
from sheets import save_to_sheets

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
# DETEKSI LOKASI & WAKTU
# ─────────────────────────────────────────
city, timezone = get_location_from_ip()
tz  = pytz.timezone(timezone)
now = datetime.now(tz)

# ─────────────────────────────────────────
# KUESIONER
# ─────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    st.markdown("### 📋 Profil Kamu")
    st.caption("Isi dulu biar rekomendasinya makin pas!")

    with st.form("kuesioner"):
        nama  = st.text_input("Nama kamu")
        kota  = st.text_input("Kota kamu", value=city)
        genre = st.selectbox(
            "Genre favorit",
            ["Action", "Drama", "Comedy", "Adventure",
             "Romance", "Animation", "Mystery", "Horror"]
        )
        mood_pilihan = st.selectbox(
            "Mood kamu sekarang",
            ["Ikuti cuaca", "Tegang", "Melankolis", "Cozy",
             "Semangat", "Romantis", "Santai", "Misterius"]
        )
        durasi = st.selectbox(
            "Durasi nonton yang kamu punya",
            ["Santai (~1 jam)", "Standar (~2 jam)", "Bebas"]
        )

        submit = st.form_submit_button("🎬 Lihat Rekomendasi!")

    if submit:
        if not nama:
            st.warning("Nama tidak boleh kosong!")
        else:
            # Simpan ke Google Sheets
            with st.spinner("Menyimpan data..."):
                save_to_sheets(nama, kota, genre, mood_pilihan, durasi)

            # Simpan ke session state
            st.session_state.submitted    = True
            st.session_state.nama         = nama
            st.session_state.kota         = kota
            st.session_state.genre        = genre
            st.session_state.mood_pilihan = mood_pilihan
            st.session_state.durasi       = durasi
            st.rerun()

else:
    # ─────────────────────────────────────────
    # HASIL REKOMENDASI
    # ─────────────────────────────────────────
    nama         = st.session_state.nama
    kota         = st.session_state.kota
    genre        = st.session_state.genre
    mood_pilihan = st.session_state.mood_pilihan
    durasi       = st.session_state.durasi

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Preferensi")
        bahasa = st.selectbox("Bahasa Film", ["Hollywood", "Indonesia", "Korea"])
        st.divider()
        st.caption(f"👤 {nama}")
        st.caption(f"📍 {kota}")
        st.caption(f"🕐 {now.strftime('%H:%M')} ({timezone})")
        if st.button("🔄 Isi ulang kuesioner"):
            st.session_state.submitted = False
            st.rerun()

    # Ambil cuaca
    with st.spinner(f"📡 Mengambil data cuaca {kota}..."):
        cuaca = get_weather(kota)

    kode_cuaca = cuaca["kode_cuaca"]

    # Tentukan mood
    if mood_pilihan == "Ikuti cuaca":
        mood, waktu = get_mood(kode_cuaca, now.hour)
    else:
        mood  = mood_pilihan.lower()
        waktu = "manual"

    # Tampilkan cuaca
    col1, col2, col3 = st.columns(3)
    col1.metric("🌤️ Cuaca", cuaca["cuaca"].title())
    col2.metric("🌡️ Suhu", f"{cuaca['suhu']}°C")
    col3.metric("💧 Kelembaban", f"{cuaca['kelembaban']}%")

    st.divider()

    st.markdown(f"### 👋 Halo, {nama}!")
    st.markdown(f"🎭 Mood: `{mood.upper()}` | 🎬 Genre favorit: `{genre}`")

    st.divider()

    # Rekomendasi film
    st.markdown("### 🍿 Rekomendasi Film")
    is_weekend = now.weekday() >= 5

    with st.spinner("🎬 Mencari film untukmu..."):
        films = get_movies(mood, bahasa, durasi, is_weekend)

    if not films:
        st.warning("Tidak ada film yang cocok. Coba ubah preferensi di sidebar!")
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