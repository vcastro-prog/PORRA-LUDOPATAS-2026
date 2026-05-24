import streamlit as st

st.set_page_config(
    page_title="Porra Ludópatas 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top right, rgba(255,215,0,0.10), transparent 28%),
        linear-gradient(135deg, #020617 0%, #071133 45%, #0f172a 100%);
    color:white;
}

section[data-testid="stSidebar"] {
    display:none;
}

.block-container {
    padding-top: 1.5rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1600px;
}

.hero-card {
    background: linear-gradient(90deg, rgba(2,6,23,0.96), rgba(12,20,55,0.94));
    border:1px solid rgba(255,255,255,0.10);
    border-radius:30px;
    padding:42px 48px;
    margin-bottom:30px;
    box-shadow:0 12px 45px rgba(0,0,0,0.38);
}

.hero-grid {
    display:grid;
    grid-template-columns: minmax(0, 2.2fr) minmax(280px, 0.8fr);
    gap:32px;
    align-items:center;
}

.mini-title {
    color:#38e8ff;
    font-size:1.05rem;
    font-weight:800;
    letter-spacing:5px;
    margin-bottom:18px;
}

.hero-title {
    font-size:5.4rem;
    line-height:0.95;
    font-weight:950;
    letter-spacing:1px;
    margin:0 0 28px 0;
    color:white;
}

.hero-title span {
    background: linear-gradient(90deg,#ffd76a,#67e8f9,#22d3ee);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-subtitle {
    font-size:1.35rem;
    color:#cbd5e1;
    margin-bottom:34px;
}

.stats-row {
    display:flex;
    gap:16px;
    flex-wrap:wrap;
}

.stat-pill {
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.12);
    padding:15px 22px;
    border-radius:999px;
    font-weight:800;
    color:white;
    font-size:1rem;
}

.header-logo-box {
    display:flex;
    align-items:center;
    justify-content:center;
    height:100%;
    min-height:340px;
    padding:12px 8px;
}

.header-logo-box img {
    width:100%;
    max-width:340px;
    height:auto;
    object-fit:contain;
    filter: drop-shadow(0 0 26px rgba(255,215,0,0.25));
}

@media (max-width: 1000px) {
    .hero-grid {
        grid-template-columns:1fr;
        text-align:left;
    }

    .hero-title {
        font-size:3.8rem;
    }

    .header-logo-box {
        min-height:auto;
        justify-content:center;
        padding-top:20px;
    }

    .header-logo-box img {
        max-width:230px;
    }
}

@media (max-width: 600px) {
    .block-container {
        padding-left:1rem;
        padding-right:1rem;
    }

    .hero-card {
        padding:28px 24px;
    }

    .hero-title {
        font-size:2.9rem;
    }

    .hero-subtitle {
        font-size:1.05rem;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="hero-grid">
        <div>
            <div class="mini-title">CANADA · MÉXICO · USA 2026</div>
            <div class="hero-title">PORRA <span>LUDÓPATAS</span><br>2026</div>
            <div class="hero-subtitle">Clasificación, apuestas y resultados de la Porra Ludópatas durante el Mundial 2026.</div>
            <div class="stats-row">
                <div class="stat-pill">🌍 48 selecciones</div>
                <div class="stat-pill">🏟️ 16 sedes</div>
                <div class="stat-pill">📅 11 junio – 19 julio</div>
                <div class="stat-pill">⚡ 104 partidos</div>
            </div>
        </div>
        <div class="header-logo-box">
            <img src="app/static/worldcup_2026_transparent.png" alt="World Cup 2026">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🏆 Clasificación General")

st.dataframe(
    {
        "Pos": [1, 2, 3, 4, 5],
        "Jugador": ["Gonzalo", "Carlos", "Marta", "Javi", "Laura"],
        "Puntos": [13, 12, 11, 10, 9],
        "Aciertos": [5, 4, 4, 3, 3],
    },
    use_container_width=True,
    hide_index=True
)
