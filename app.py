# app.py — Film Mood Matcher
import streamlit as st
from datetime import datetime
import pytz
from matcher import get_weather, get_mood, get_movies, get_location_from_ip
from sheets import save_to_sheets

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Film Mood Matcher",
    page_icon="🎬",
    layout="centered"
)

# ─────────────────────────────────────────
# CUSTOM CSS — Cinematic Minimalist
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Outfit:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0a !important;
    color: #e8e0d5 !important;
}

[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(180,140,90,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(120,90,60,0.05) 0%, transparent 60%);
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { display: none !important; }

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Cormorant Garamond', serif !important;
    color: #e8e0d5 !important;
    letter-spacing: 0.02em;
}

p, li, span, label, div {
    font-family: 'Outfit', sans-serif !important;
    color: #b0a898 !important;
}

/* ── Main container ── */
.block-container {
    max-width: 680px !important;
    padding: 4rem 2rem !important;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 1px solid rgba(180,140,90,0.15);
    margin-bottom: 3rem;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.2rem;
    font-weight: 300;
    color: #e8e0d5;
    letter-spacing: 0.08em;
    line-height: 1.1;
    margin: 0;
}
.hero-title span {
    font-style: italic;
    color: #c4a96e !important;
}
.hero-sub {
    font-family: 'Outfit', sans-serif;
    font-size: 0.78rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #6b6058 !important;
    margin-top: 0.8rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'Outfit', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #c4a96e !important;
    margin-bottom: 1.5rem;
    display: block;
}

/* ── Form inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(180,140,90,0.2) !important;
    border-radius: 4px !important;
    color: #e8e0d5 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s ease;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(196,169,110,0.5) !important;
    box-shadow: 0 0 0 1px rgba(196,169,110,0.15) !important;
}

/* Input labels */
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
    font-size: 0.68rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #6b6058 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Submit button ── */
[data-testid="stFormSubmitButton"] button {
    background: transparent !important;
    border: 1px solid rgba(196,169,110,0.4) !important;
    color: #c4a96e !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.3em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 2.5rem !important;
    border-radius: 2px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    margin-top: 1rem !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: rgba(196,169,110,0.08) !important;
    border-color: rgba(196,169,110,0.7) !important;
}

/* ── Regular button (reset) ── */
[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid rgba(180,140,90,0.2) !important;
    color: #6b6058 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] button:hover {
    border-color: rgba(196,169,110,0.4) !important;
    color: #c4a96e !important;
}

/* ── Weather bar ── */
.weather-bar {
    display: flex;
    gap: 0;
    border: 1px solid rgba(180,140,90,0.15);
    border-radius: 4px;
    overflow: hidden;
    margin: 1.5rem 0;
}
.weather-item {
    flex: 1;
    padding: 1rem;
    text-align: center;
    border-right: 1px solid rgba(180,140,90,0.1);
}
.weather-item:last-child { border-right: none; }
.weather-val {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    font-weight: 300;
    color: #e8e0d5;
    display: block;
    line-height: 1;
}
.weather-key {
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a4540 !important;
    display: block;
    margin-top: 0.3rem;
}

/* ── Mood display ── */
.mood-display {
    text-align: center;
    padding: 2.5rem 0;
    border-bottom: 1px solid rgba(180,140,90,0.1);
    margin-bottom: 2.5rem;
}
.mood-word {
    font-family: 'Cormorant Garamond', serif;
    font-size: 4rem;
    font-weight: 300;
    font-style: italic;
    color: #c4a96e;
    display: block;
    letter-spacing: 0.05em;
    line-height: 1;
}
.mood-meta {
    font-size: 0.68rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #4a4540 !important;
    margin-top: 0.6rem;
}

/* ── Film card ── */
.film-card {
    display: flex;
    gap: 1.5rem;
    padding: 1.5rem 0;
    border-bottom: 1px solid rgba(180,140,90,0.08);
}
.film-card:last-child { border-bottom: none; }
.film-poster {
    width: 80px;
    flex-shrink: 0;
}
.film-poster img {
    width: 80px;
    border-radius: 2px;
    display: block;
}
.film-no-poster {
    width: 80px;
    height: 120px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(180,140,90,0.1);
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}
.film-info { flex: 1; }
.film-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    font-weight: 400;
    color: #e8e0d5;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.film-meta {
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    color: #c4a96e !important;
    margin-bottom: 0.6rem;
}
.film-synopsis {
    font-size: 0.82rem;
    line-height: 1.6;
    color: #5a5450 !important;
}

/* ── Divider ── */
.gold-divider {
    border: none;
    border-top: 1px solid rgba(180,140,90,0.12);
    margin: 2rem 0;
}

/* ── Info row (nama, kota, waktu) ── */
.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid rgba(180,140,90,0.1);
    margin-bottom: 2rem;
}
.info-item {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4a4540 !important;
}
.info-item span {
    color: #8a7e72 !important;
}

/* ── Selectbox dropdown ── */
[data-testid="stSelectbox"] svg { fill: #6b6058 !important; }

/* ── Warning ── */
[data-testid="stAlert"] {
    background: rgba(196,169,110,0.05) !important;
    border: 1px solid rgba(196,169,110,0.2) !important;
    border-radius: 4px !important;
    color: #c4a96e !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #c4a96e !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #080808 !important;
    border-right: 1px solid rgba(180,140,90,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1 class="hero-title">Film <span>Mood</span> Matcher</h1>
    <p class="hero-sub">Cuaca · Waktu · Selera</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DETEKSI LOKASI
# ─────────────────────────────────────────
city, _ = get_location_from_ip()

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ─────────────────────────────────────────
# KUESIONER
# ─────────────────────────────────────────
if not st.session_state.submitted:
    st.markdown('<span class="section-label">Profil Kamu</span>', unsafe_allow_html=True)

    with st.form("kuesioner"):
        nama = st.text_input("Nama", placeholder="Siapa kamu?")
        kota = st.text_input("Kota", value=city, placeholder="Kota tempat kamu berada")

        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox("Genre Favorit", [
                "Action", "Drama", "Comedy", "Adventure",
                "Romance", "Animation", "Mystery", "Horror"
            ])
        with col2:
            mood_pilihan = st.selectbox("Mood Sekarang", [
                "Ikuti cuaca", "Tegang", "Melankolis", "Cozy",
                "Semangat", "Romantis", "Santai", "Misterius"
            ])

        col3, col4 = st.columns(2)
        with col3:
            durasi = st.selectbox("Durasi Nonton", [
                "Santai (~1 jam)", "Standar (~2 jam)", "Bebas"
            ])
        with col4:
            timezone_pilihan = st.selectbox("Zona Waktu", [
                "Asia/Jakarta (WIB)",
                "Asia/Makassar (WITA)",
                "Asia/Jayapura (WIT)",
                "Asia/Kuala_Lumpur",
                "Asia/Singapore",
                "Asia/Tokyo",
                "Europe/London",
                "America/New_York",
                "America/Los_Angeles"
            ])

        submit = st.form_submit_button("Temukan Film")

    if submit:
        if not nama:
            st.warning("Nama tidak boleh kosong.")
        else:
            tz_key = timezone_pilihan.split(" ")[0]
            with st.spinner("Menyimpan..."):
                save_to_sheets(nama, kota, genre, mood_pilihan, durasi)

            st.session_state.submitted    = True
            st.session_state.nama         = nama
            st.session_state.kota         = kota
            st.session_state.genre        = genre
            st.session_state.mood_pilihan = mood_pilihan
            st.session_state.durasi       = durasi
            st.session_state.timezone     = tz_key
            st.rerun()

# ─────────────────────────────────────────
# HASIL REKOMENDASI
# ─────────────────────────────────────────
else:
    nama         = st.session_state.nama
    kota         = st.session_state.kota
    genre        = st.session_state.genre
    mood_pilihan = st.session_state.mood_pilihan
    durasi       = st.session_state.durasi
    tz_key       = st.session_state.timezone

    tz  = pytz.timezone(tz_key)
    now = datetime.now(tz)

    # Sidebar — preferensi bahasa
    with st.sidebar:
        st.markdown('<span class="section-label">Preferensi</span>', unsafe_allow_html=True)
        bahasa = st.selectbox("Bahasa Film", ["Hollywood", "Indonesia", "Korea"])
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        st.markdown(f'<p class="info-item">👤 <span>{nama}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-item">📍 <span>{kota}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-item">🕐 <span>{now.strftime("%H:%M")} {tz_key.split("/")[-1]}</span></p>', unsafe_allow_html=True)
        st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
        if st.button("↩ Isi Ulang"):
            st.session_state.submitted = False
            st.rerun()

    # Ambil cuaca
    with st.spinner(f"Mengambil cuaca {kota}..."):
        cuaca = get_weather(kota)

    kode_cuaca = cuaca["kode_cuaca"]

    # Tentukan mood
    if mood_pilihan == "Ikuti cuaca":
        mood, waktu = get_mood(kode_cuaca, now.hour)
    else:
        mood  = mood_pilihan.lower()
        waktu = now.strftime("%H:%M")

    # Weather bar
    st.markdown(f"""
    <div class="weather-bar">
        <div class="weather-item">
            <span class="weather-val">{cuaca['cuaca'].title()}</span>
            <span class="weather-key">Cuaca</span>
        </div>
        <div class="weather-item">
            <span class="weather-val">{cuaca['suhu']}°</span>
            <span class="weather-key">Celsius</span>
        </div>
        <div class="weather-item">
            <span class="weather-val">{cuaca['kelembaban']}%</span>
            <span class="weather-key">Kelembaban</span>
        </div>
        <div class="weather-item">
            <span class="weather-val">{now.strftime('%H:%M')}</span>
            <span class="weather-key">{tz_key.split('/')[-1]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mood display
    is_weekend  = now.weekday() >= 5
    hari_label  = "Weekend" if is_weekend else now.strftime("%A")

    st.markdown(f"""
    <div class="mood-display">
        <span class="mood-word">{mood.title()}</span>
        <p class="mood-meta">{kota} · {hari_label} · {waktu if mood_pilihan == 'Ikuti cuaca' else 'Pilihan sendiri'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Rekomendasi film
    st.markdown('<span class="section-label">Rekomendasi Film</span>', unsafe_allow_html=True)

    with st.spinner("Mencari film..."):
        films = get_movies(mood, bahasa, durasi, is_weekend)

    if not films:
        st.warning("Tidak ada film yang cocok. Coba ubah preferensi di sidebar.")
    else:
        for film in films:
            poster_html = (
                f'<img src="{film["poster"]}" alt="{film["judul"]}">'
                if film["poster"]
                else '<div class="film-no-poster">🎞</div>'
            )
            st.markdown(f"""
            <div class="film-card">
                <div class="film-poster">{poster_html}</div>
                <div class="film-info">
                    <div class="film-title">{film['judul']}</div>
                    <div class="film-meta">{film['tahun']} &nbsp;·&nbsp; ⭐ {film['rating']} &nbsp;·&nbsp; {film['durasi']} min</div>
                    <div class="film-synopsis">{film['sinopsis']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)