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
# CSS — Mobile-first, IMDB-inspired
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=IBM+Plex+Serif:ital,wght@0,300;1,300;1,400&display=swap');

:root {
    --bg:       #0f0f0f;
    --bg2:      #161616;
    --bg3:      #1e1e1e;
    --border:   rgba(255,255,255,0.07);
    --gold:     #f5c518;
    --gold-dim: rgba(245,197,24,0.15);
    --text:     #f0f0f0;
    --text-2:   #a0a0a0;
    --text-3:   #555;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
footer { display: none !important; }

.block-container {
    max-width: 480px !important;
    padding: 0 0 4rem !important;
    margin: 0 auto !important;
}

/* ── TOP NAV ── */
.topnav {
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    padding: 0.9rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}
.topnav-logo {
    font-family: 'IBM Plex Serif', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: var(--gold) !important;
}
.topnav-sub {
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-3) !important;
}

/* ── WEATHER STRIP ── */
.weather-strip {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 0.65rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.72rem;
    color: var(--text-2) !important;
    overflow-x: auto;
    white-space: nowrap;
    scrollbar-width: none;
}
.weather-strip::-webkit-scrollbar { display: none; }
.weather-strip b { color: var(--text) !important; font-weight: 500; }
.wdot {
    width: 3px; height: 3px;
    background: var(--text-3);
    border-radius: 50%;
    flex-shrink: 0;
    display: inline-block;
}

/* ── MOOD HERO ── */
.mood-hero {
    padding: 1.8rem 1rem 1.2rem;
    border-bottom: 1px solid var(--border);
}
.mood-label {
    font-size: 0.6rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--text-3) !important;
    margin-bottom: 0.35rem;
}
.mood-title {
    font-family: 'IBM Plex Serif', serif;
    font-style: italic;
    font-size: 2.8rem;
    font-weight: 300;
    color: var(--gold) !important;
    line-height: 1;
    margin-bottom: 0.7rem;
}
.mood-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}
.mood-tag {
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-3) !important;
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 0.15rem 0.45rem;
}

/* ── SECTION HEADER ── */
.section-head {
    padding: 0.9rem 1rem 0.6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
}
.section-head-title {
    font-size: 0.62rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--text-3) !important;
}
.section-head-count {
    font-size: 0.65rem;
    color: var(--text-3) !important;
}

/* ── FILM ITEM ── */
.film-item {
    display: flex;
    gap: 0.85rem;
    padding: 0.9rem 1rem;
    border-bottom: 1px solid var(--border);
    text-decoration: none !important;
    transition: background 0.12s;
}
.film-item:hover { background: var(--bg2); }

.film-rank {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-3) !important;
    min-width: 1.1rem;
    padding-top: 0.15rem;
}

.film-poster-wrap {
    flex-shrink: 0;
    width: 54px;
    height: 81px;
    border-radius: 3px;
    overflow: hidden;
    background: var(--bg3);
    border: 1px solid var(--border);
}
.film-poster-wrap img {
    width: 100%; height: 100%;
    object-fit: cover; display: block;
}
.film-no-poster {
    width: 100%; height: 100%;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}

.film-body { flex: 1; min-width: 0; }

.film-name {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text) !important;
    line-height: 1.25;
    margin-bottom: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.film-meta-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.4rem;
    flex-wrap: wrap;
}
.film-year { font-size: 0.7rem; color: var(--text-3) !important; }
.film-rating {
    display: flex; align-items: center; gap: 0.18rem;
    background: var(--gold-dim);
    border-radius: 2px; padding: 0.08rem 0.3rem;
}
.film-rating-star { color: var(--gold) !important; font-size: 0.62rem; }
.film-rating-val  { font-size: 0.7rem; font-weight: 600; color: var(--gold) !important; }

.film-synopsis {
    font-size: 0.73rem;
    line-height: 1.5;
    color: var(--text-2) !important;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.film-arrow {
    color: var(--text-3) !important;
    font-size: 1rem;
    align-self: center;
    flex-shrink: 0;
    margin-left: 0.2rem;
}

/* ── FORM ── */
.form-wrap { padding: 1.5rem 1rem 0.5rem; }
.form-title {
    font-family: 'IBM Plex Serif', serif;
    font-style: italic;
    font-size: 2rem;
    font-weight: 300;
    color: var(--text) !important;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}
.form-sub {
    font-size: 0.72rem;
    color: var(--text-3) !important;
    margin-bottom: 1.2rem;
}

[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--text-3) !important;
}
[data-testid="stTextInput"] input {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(245,197,24,0.35) !important;
    box-shadow: 0 0 0 2px rgba(245,197,24,0.07) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stSelectbox"] svg { fill: var(--text-3) !important; }

[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    background: var(--gold) !important;
    border: none !important;
    border-radius: 3px !important;
    color: #0f0f0f !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.7rem !important;
    margin-top: 0.5rem !important;
    transition: opacity 0.15s !important;
}
[data-testid="stFormSubmitButton"] button:hover { opacity: 0.85 !important; }

[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-3) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
}
[data-testid="stButton"] button:hover {
    border-color: var(--gold) !important;
    color: var(--gold) !important;
}

[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stAlert"] {
    background: rgba(245,197,24,0.05) !important;
    border: 1px solid rgba(245,197,24,0.2) !important;
    color: var(--gold) !important;
    font-size: 0.78rem !important;
    border-radius: 3px !important;
    margin: 0.5rem 1rem !important;
}
[data-testid="stSpinner"] p {
    font-size: 0.72rem !important;
    color: var(--text-3) !important;
}
</style>
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
# TOP NAV
# ─────────────────────────────────────────
st.markdown("""
<div class="topnav">
    <div class="topnav-logo">Mood Matcher</div>
    <div class="topnav-sub">Film · Cuaca · Waktu</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# KUESIONER
# ─────────────────────────────────────────
if not st.session_state.submitted:
    st.markdown("""
    <div class="form-wrap">
        <div class="form-title">Halo,<br>siapa kamu?</div>
        <div class="form-sub">Isi profil singkat untuk rekomendasi yang pas.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("kuesioner"):
        st.markdown('<div style="padding:0 1rem 1rem;">', unsafe_allow_html=True)

        nama = st.text_input("Nama", placeholder="Nama kamu")
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
            bahasa = st.selectbox("Bahasa Film", [
                "Hollywood", "Indonesia", "Korea"
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

        submit = st.form_submit_button("Temukan Film →")
        st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        if not nama:
            st.warning("Nama tidak boleh kosong.")
        else:
            tz_key = timezone_pilihan.split(" ")[0]
            with st.spinner("Menyimpan..."):
                save_to_sheets(nama, kota, genre, mood_pilihan, bahasa)
            st.session_state.submitted    = True
            st.session_state.nama         = nama
            st.session_state.kota         = kota
            st.session_state.genre        = genre
            st.session_state.mood_pilihan = mood_pilihan
            st.session_state.bahasa       = bahasa
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
    bahasa       = st.session_state.bahasa
    tz_key       = st.session_state.timezone

    tz  = pytz.timezone(tz_key)
    now = datetime.now(tz)

    # Sidebar
    with st.sidebar:
        st.markdown('<div style="padding:1rem 0 0.5rem;font-size:0.6rem;letter-spacing:0.25em;text-transform:uppercase;color:#555;">Preferensi</div>', unsafe_allow_html=True)
        bahasa = st.selectbox("Bahasa Film", ["Hollywood", "Indonesia", "Korea"],
                              index=["Hollywood","Indonesia","Korea"].index(bahasa))
        st.markdown(f'<div style="margin-top:1rem;font-size:0.7rem;color:#555;line-height:2.2;">👤 {nama}<br>📍 {kota}<br>🕐 {now.strftime("%H:%M")} {tz_key.split("/")[-1]}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
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

    is_weekend = now.weekday() >= 5
    hari_label = "Weekend" if is_weekend else now.strftime("%A")

    # Weather strip
    st.markdown(f"""
    <div class="weather-strip">
        <b>{kota}</b>
        <span class="wdot"></span>
        {cuaca['cuaca'].title()}
        <span class="wdot"></span>
        <b>{cuaca['suhu']}°C</b>
        <span class="wdot"></span>
        {cuaca['kelembaban']}% lembab
        <span class="wdot"></span>
        {now.strftime('%H:%M')} {tz_key.split('/')[-1]}
        <span class="wdot"></span>
        {hari_label}
    </div>
    """, unsafe_allow_html=True)

    # Mood hero
    st.markdown(f"""
    <div class="mood-hero">
        <div class="mood-label">Mood kamu sekarang</div>
        <div class="mood-title">{mood.title()}</div>
        <div class="mood-tags">
            <span class="mood-tag">{genre}</span>
            <span class="mood-tag">{bahasa}</span>
            <span class="mood-tag">{nama}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cari film
    with st.spinner("Mencari film..."):
        films = get_movies(mood, bahasa, is_weekend, genre_favorit=genre)

    if not films:
        st.warning("Tidak ada film yang cocok. Coba ubah preferensi di sidebar.")
    else:
        st.markdown(f"""
        <div class="section-head">
            <span class="section-head-title">Rekomendasi</span>
            <span class="section-head-count">{len(films)} film</span>
        </div>
        """, unsafe_allow_html=True)

        for i, film in enumerate(films, start=1):
            tmdb_url    = f"https://www.themoviedb.org/movie/{film.get('id', '')}"
            poster_html = (
                f'<img src="{film["poster"]}" alt="{film["judul"]}">'
                if film["poster"] else '<div class="film-no-poster">🎞</div>'
            )
            st.markdown(f"""
            <a class="film-item" href="{tmdb_url}" target="_blank">
                <div class="film-rank">{i}</div>
                <div class="film-poster-wrap">{poster_html}</div>
                <div class="film-body">
                    <div class="film-name">{film['judul']}</div>
                    <div class="film-meta-row">
                        <span class="film-year">{film['tahun']}</span>
                        <div class="film-rating">
                            <span class="film-rating-star">★</span>
                            <span class="film-rating-val">{film['rating']}</span>
                        </div>
                    </div>
                    <div class="film-synopsis">{film['sinopsis']}</div>
                </div>
                <div class="film-arrow">›</div>
            </a>
            """, unsafe_allow_html=True)