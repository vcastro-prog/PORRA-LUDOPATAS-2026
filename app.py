from __future__ import annotations

from io import BytesIO
from pathlib import Path
from datetime import datetime, date
import random

import pandas as pd
import streamlit as st
import plotly.express as px

from excel_parser import leer_apuesta_excel
from scoring import calcular_puntos, clasificacion, estadisticas_participantes, resumen_partido

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="Porra Ludópatas 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Estilo visual
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;800;900&display=swap');
:root {
  --bg1: #070A13;
  --bg2: #14182C;
  --card: rgba(255,255,255,.075);
  --card2: rgba(255,255,255,.12);
  --line: rgba(255,255,255,.18);
  --text: #F8FAFC;
  --muted: #C9D4E5;
  --gold: #FFD166;
  --cyan: #1FE4FF;
  --pink: #FF4ECD;
  --green: #47F59B;
}
.stApp {
  color: var(--text);
  background:
    radial-gradient(circle at 20% 0%, rgba(31,228,255,.22), transparent 34%),
    radial-gradient(circle at 80% 10%, rgba(255,78,205,.18), transparent 31%),
    linear-gradient(145deg, var(--bg1), var(--bg2) 55%, #090C19);
}
.block-container {padding-top: 1.2rem; max-width: 1400px;}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(0,0,0,.72), rgba(13,17,34,.88));
  border-right: 1px solid var(--line);
}
h1, h2, h3 {font-family: 'Inter', sans-serif; font-weight: 900; letter-spacing: -0.03em;}
.hero {
  position: relative;
  padding: 34px 34px 30px 34px;
  border-radius: 34px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.18);
  background:
    linear-gradient(115deg, rgba(6,12,34,.96), rgba(20,25,55,.82)),
    radial-gradient(circle at 75% 30%, rgba(255,209,102,.28), transparent 30%);
  box-shadow: 0 25px 80px rgba(0,0,0,.38);
}
.hero:after {
  content: "⚽";
  position: absolute;
  right: 28px;
  top: 12px;
  font-size: 138px;
  opacity: .12;
  filter: blur(.2px);
}
.kicker {color: var(--cyan); text-transform: uppercase; font-weight: 900; letter-spacing: .18em; font-size: .86rem;}
.hero-title {font-family: 'Bebas Neue', 'Inter', sans-serif; font-size: clamp(58px, 8vw, 116px); line-height: .85; margin: 8px 0 12px 0; letter-spacing: .02em;}
.hero-title span {background: linear-gradient(90deg, var(--gold), #fff, var(--cyan)); -webkit-background-clip: text; color: transparent;}
.hero-sub {font-size: 1.12rem; color: var(--muted); max-width: 760px;}
.badge-row {display:flex; gap:10px; flex-wrap:wrap; margin-top:18px;}
.badge {padding: 9px 13px; border-radius: 999px; background: rgba(255,255,255,.11); border: 1px solid rgba(255,255,255,.17); font-weight: 800;}
.card {
  padding: 21px 22px; border-radius: 25px;
  background: var(--card); border: 1px solid var(--line);
  box-shadow: 0 18px 55px rgba(0,0,0,.20);
}
.stat-label {color: var(--muted); font-size: .82rem; text-transform: uppercase; letter-spacing:.12em; font-weight: 900;}
.stat-value {font-size: 2.25rem; font-weight: 900; margin-top: 4px;}
.stat-note {color: var(--muted); font-size: .9rem;}
.podium {display:grid; grid-template-columns: repeat(3, 1fr); gap:14px; align-items:end; margin: 12px 0 20px 0;}
.podium-card {text-align:center; border-radius:26px; padding:18px 12px; background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.18);}
.podium-card.first {padding-top: 34px; background: linear-gradient(180deg, rgba(255,209,102,.25), rgba(255,255,255,.08));}
.medal {font-size: 2.4rem;}
.player {font-weight: 900; font-size: 1.1rem; margin-top: 4px;}
.points {font-weight: 900; color: var(--gold); font-size: 1.6rem;}
.match-card {padding: 14px 16px; border-radius: 20px; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14); margin-bottom: 10px;}
.team-line {font-size: 1.05rem; font-weight: 900;}
.small-muted {color: var(--muted); font-size: .84rem;}
.callout {border-radius: 24px; padding: 18px 20px; background: linear-gradient(90deg, rgba(255,78,205,.18), rgba(31,228,255,.15)); border: 1px solid rgba(255,255,255,.18);}
.stDataFrame, [data-testid="stDataFrame"] {border-radius: 22px; overflow:hidden;}
button[kind="primary"] {border-radius: 999px;}
.metric-strip {display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:14px;}
.flash {animation: pulseGlow 2.4s infinite;}
@keyframes pulseGlow {0%{box-shadow:0 0 0 rgba(31,228,255,0)} 50%{box-shadow:0 0 34px rgba(31,228,255,.30)} 100%{box-shadow:0 0 0 rgba(31,228,255,0)}}
.ribbon {display:inline-block; padding:6px 10px; border-radius:999px; background:rgba(71,245,155,.13); border:1px solid rgba(71,245,155,.28); color:#74ffb4; font-weight:900;}
.big-cta {padding:22px 26px; border-radius:28px; background:linear-gradient(90deg, rgba(255,209,102,.22), rgba(255,78,205,.18), rgba(31,228,255,.16)); border:1px solid rgba(255,255,255,.20);}
@media (max-width: 900px) {.metric-strip {grid-template-columns: repeat(2, 1fr);} .hero-title {font-size: 56px;}}
</style>
""",
    unsafe_allow_html=True,
)

FLAG = {
    "MEXICO":"🇲🇽", "SUDÁFRICA":"🇿🇦", "COREA DEL SUR":"🇰🇷", "REP. CHECA":"🇨🇿", "CANADA":"🇨🇦",
    "BOSNIA":"🇧🇦", "QATAR":"🇶🇦", "SUIZA":"🇨🇭", "BRASIL":"🇧🇷", "MARRUECOS":"🇲🇦",
    "HAITI":"🇭🇹", "ESCOCIA":"🏴", "ESTADOS UNIDOS":"🇺🇸", "PARAGUAY":"🇵🇾", "AUSTRALIA":"🇦🇺",
    "TURQUÍA":"🇹🇷", "ALEMANIA":"🇩🇪", "CURAÇAO":"🇨🇼", "COSTA DEMARFIL":"🇨🇮", "COSTA DE MARFIL":"🇨🇮",
    "ECUADOR":"🇪🇨", "PAISES BAJOS":"🇳🇱", "JAPÓN":"🇯🇵", "SUECIA":"🇸🇪", "TÚNEZ":"🇹🇳",
    "BÉLGICA":"🇧🇪", "EGIPTO":"🇪🇬", "IRÁN":"🇮🇷", "NUEVA ZELANDA":"🇳🇿", "ARABIA SAUDÍ":"🇸🇦",
    "URUGUAY":"🇺🇾", "ESPAÑA":"🇪🇸", "CABO VERDE":"🇨🇻", "FRANCIA":"🇫🇷", "SENEGAL":"🇸🇳",
    "IRAQ":"🇮🇶", "NORUEGA":"🇳🇴", "ARGENTINA":"🇦🇷", "ARGELIA":"🇩🇿", "AUSTRIA":"🇦🇹",
    "JORDANIA":"🇯🇴", "PORTUGAL":"🇵🇹", "R.D.CONGO":"🇨🇩", "R.D. CONGO":"🇨🇩", "UZBEKISTÁN":"🇺🇿",
    "COLOMBIA":"🇨🇴", "INGLATERRA":"🏴", "CROCIA":"🇭🇷", "CROACIA":"🇭🇷", "GHANA":"🇬🇭", "PANAMÁ":"🇵🇦",
}

SLOGANS = [
    "El Excel era solo el principio. Ahora empieza la guerra psicológica.",
    "No hace falta saber de fútbol. Hace falta acertar cuando todos fallan.",
    "Cada gol mueve la clasificación. Cada empate destruye una ilusión.",
    "123 participantes es el récord. 2026 pide algo más grande.",
]

@st.cache_data
def cargar_partidos() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "partidos.csv")
    df["local_flag"] = df["local"].map(FLAG).fillna("🏳️")
    df["visitante_flag"] = df["visitante"].map(FLAG).fillna("🏳️")
    return df


def demo_apuestas(partidos: pd.DataFrame, n: int = 24) -> pd.DataFrame:
    nombres = ["Vi", "Carlos", "Marta", "Ana", "Javi", "Laura", "Sergio", "Elena", "David", "Nuria", "Pablo", "Bea", "Rafa", "Cris", "Gonzalo", "Silvia", "Mario", "Alba", "Dani", "Irene", "Óscar", "Patri", "Nacho", "Lola"][:n]
    rows = []
    rnd = random.Random(2026)
    for nombre in nombres:
        for _, p in partidos.iterrows():
            rows.append({
                "participante": nombre,
                "partido_id": int(p.partido_id),
                "goles_local": rnd.choice([0,1,1,1,2,2,3]),
                "goles_visitante": rnd.choice([0,0,1,1,2,2,3]),
            })
    return pd.DataFrame(rows)


def html_kpis(participantes: int, jugados: int, partidos_total: int, lider: str, lider_pts: int):
    c1, c2, c3, c4 = st.columns(4)
    items = [
        ("Participantes", participantes, "La grada de la porra"),
        ("Partidos jugados", f"{jugados}/{partidos_total}", "Se recalcula al instante"),
        ("Líder actual", lider, f"{lider_pts} puntos" if lider else "Sin líder todavía"),
        ("Máximo posible", partidos_total * 3, "3 puntos por pleno"),
    ]
    for col, (label, value, note) in zip([c1,c2,c3,c4], items):
        col.markdown(f"<div class='card'><div class='stat-label'>{label}</div><div class='stat-value'>{value}</div><div class='stat-note'>{note}</div></div>", unsafe_allow_html=True)


def podium(tabla: pd.DataFrame):
    if tabla.empty:
        st.markdown("<div class='callout'>Sube apuestas para encender el marcador. La clasificación aparecerá aquí.</div>", unsafe_allow_html=True)
        return
    top = tabla.head(3).copy()
    while len(top) < 3:
        top.loc[len(top)] = {"participante": "-", "puntos": 0, "plenos": 0, "aciertos_1x2": 0, "partidos_puntuados": 0, "posición": len(top)+1}
    order = [1,0,2]
    medals = ["🥈", "👑", "🥉"]
    classes = ["", "first", ""]
    html = "<div class='podium'>"
    for medal, idx, klass in zip(medals, order, classes):
        r = top.iloc[idx]
        html += f"<div class='podium-card {klass}'><div class='medal'>{medal}</div><div class='player'>{r['participante']}</div><div class='points'>{int(r['puntos'])} pts</div><div class='small-muted'>{int(r.get('plenos',0))} plenos · {int(r.get('aciertos_1x2',0))} 1X2</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def proximo_partido(partidos: pd.DataFrame, resultados_df: pd.DataFrame):
    jugados = set(resultados_df.dropna(subset=["goles_local", "goles_visitante"])["partido_id"].astype(int))
    pendientes = partidos[~partidos["partido_id"].astype(int).isin(jugados)].head(3)
    if pendientes.empty:
        st.success("Todos los partidos de la fase de grupos están cerrados. ¡A revisar el campeón de la porra!")
        return
    for _, p in pendientes.iterrows():
        st.markdown(
            f"<div class='match-card'><div class='small-muted'>{p['fecha']} · {p['grupo']} · Partido {int(p['partido_id'])}</div>"
            f"<div class='team-line'>{p['local_flag']} {p['local']} <span style='color:#FFD166'>vs</span> {p['visitante_flag']} {p['visitante']}</div></div>",
            unsafe_allow_html=True,
        )


def bloque_comunidad(apuestas: pd.DataFrame, partidos: pd.DataFrame):
    if apuestas.empty:
        st.info("Aún no hay apuestas para leer el pulso de la comunidad.")
        return
    resumen = resumen_partido(apuestas, pd.DataFrame(columns=["partido_id", "goles_local", "goles_visitante"]), partidos)
    if resumen.empty:
        return
    partido = resumen.sort_values("total", ascending=False).iloc[0]
    vals = pd.DataFrame({"signo": ["Gana local", "Empate", "Gana visitante"], "porcentaje": [partido["1%"], partido["X%"], partido["2%"]]})
    st.markdown(f"<div class='card'><div class='stat-label'>Partido con más apuestas</div><div class='team-line'>{partido['partido']}</div><div class='small-muted'>Así piensa la comunidad antes de que ruede el balón.</div></div>", unsafe_allow_html=True)
    fig = px.bar(vals, x="signo", y="porcentaje", text="porcentaje", range_y=[0, 100])
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=10,r=10,t=20,b=10), showlegend=False)
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

partidos = cargar_partidos()

# -----------------------------
# Sidebar: carga de datos
# -----------------------------
st.sidebar.title("⚙️ Centro de mando")
st.sidebar.caption("Sube Excels, mete resultados y deja que la porra haga ruido.")

demo_mode = st.sidebar.toggle("Modo demo impactante", value=True, help="Muestra la web con participantes ficticios si aún no has subido Excels.")

uploaded = st.sidebar.file_uploader("1) Sube los Excel rellenados", type=["xlsx"], accept_multiple_files=True)

apuestas = []
for f in uploaded:
    try:
        df = leer_apuesta_excel(BytesIO(f.getvalue()), partidos)
        if len(df) < len(partidos):
            st.sidebar.warning(f"{f.name}: leídos {len(df)} de {len(partidos)} partidos.")
        apuestas.append(df)
    except Exception as e:
        st.sidebar.error(f"No pude leer {f.name}: {e}")

apuestas_df = pd.concat(apuestas, ignore_index=True) if apuestas else pd.DataFrame(columns=["participante", "partido_id", "goles_local", "goles_visitante"])
if apuestas_df.empty and demo_mode:
    apuestas_df = demo_apuestas(partidos)
    st.sidebar.info("Estás viendo datos ficticios para enseñar la experiencia. Desactiva el modo demo cuando subas apuestas reales.")

st.sidebar.markdown("---")
st.sidebar.subheader("2) Resultados")
resultados_upload = st.sidebar.file_uploader("Opcional: subir resultados CSV", type=["csv"])
resultados_base = partidos[["partido_id", "grupo", "fecha", "local", "visitante"]].copy()
resultados_base["goles_local"] = pd.NA
resultados_base["goles_visitante"] = pd.NA
if resultados_upload is not None:
    try:
        prev = pd.read_csv(resultados_upload)
        resultados_base = resultados_base.drop(columns=["goles_local", "goles_visitante"]).merge(prev, on="partido_id", how="left")
    except Exception as e:
        st.sidebar.error(f"No pude leer el CSV de resultados: {e}")

with st.sidebar.expander("Editar resultados", expanded=True):
    resultados_editados = st.data_editor(
        resultados_base,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "partido_id": st.column_config.NumberColumn("#", disabled=True),
            "grupo": st.column_config.TextColumn("Grupo", disabled=True),
            "fecha": st.column_config.TextColumn("Fecha", disabled=True),
            "local": st.column_config.TextColumn("Local", disabled=True),
            "visitante": st.column_config.TextColumn("Visitante", disabled=True),
            "goles_local": st.column_config.NumberColumn("GL", min_value=0, step=1),
            "goles_visitante": st.column_config.NumberColumn("GV", min_value=0, step=1),
        },
    )

resultados_df = resultados_editados[["partido_id", "goles_local", "goles_visitante"]]
if demo_mode and uploaded == [] and resultados_df.dropna(subset=["goles_local", "goles_visitante"]).empty:
    # Para que el modo demo tenga vida desde el primer click.
    demo_res = partidos.head(10)[["partido_id"]].copy()
    rnd = random.Random(101)
    demo_res["goles_local"] = [rnd.choice([0,1,1,2,2,3]) for _ in range(len(demo_res))]
    demo_res["goles_visitante"] = [rnd.choice([0,0,1,1,2]) for _ in range(len(demo_res))]
    resultados_df = resultados_df.drop(columns=["goles_local", "goles_visitante"]).merge(demo_res, on="partido_id", how="left")

csv_resultados = resultados_df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("Descargar resultados CSV", csv_resultados, "resultados_porra_2026.csv", "text/csv")

# -----------------------------
# Cálculo
# -----------------------------
detalle = calcular_puntos(apuestas_df, resultados_df)
tabla = clasificacion(detalle)
stats = estadisticas_participantes(detalle)
partidos_jugados = resultados_df.dropna(subset=["goles_local", "goles_visitante"]).shape[0]
lider = tabla.iloc[0]["participante"] if not tabla.empty else ""
lider_pts = int(tabla.iloc[0]["puntos"]) if not tabla.empty else 0

# -----------------------------
# Portada
# -----------------------------
st.markdown(
    f"""
<div class='hero'>
  <div class='kicker'>Canada · México · USA 2026</div>
  <div class='hero-title'>PORRA <span>LUDÓPATAS</span> 2026</div>
  <div class='hero-sub'>{random.choice(SLOGANS)} Ranking en vivo, apuestas visibles, piques diarios y cada gol moviendo la tabla.</div>
  <div class='badge-row'>
    <div class='badge'>🌎 48 selecciones</div>
    <div class='badge'>🏟️ 16 sedes</div>
    <div class='badge'>📅 11 junio – 19 julio</div>
    <div class='badge'>⚡ 104 partidos</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")
html_kpis(apuestas_df["participante"].nunique() if not apuestas_df.empty else 0, partidos_jugados, len(partidos), lider, lider_pts)

st.write("")
left, right = st.columns([1.7, 1])
with left:
    st.subheader("🏆 Podio en directo")
    podium(tabla)
with right:
    st.subheader("⏭️ Próximos partidos")
    proximo_partido(partidos, resultados_df)

st.write("")
a, b = st.columns([1.1, 1])
with a:
    st.markdown("### 🔥 La jornada")
    if not detalle.empty and partidos_jugados > 0:
        jornada = detalle.dropna(subset=["real_local", "real_visitante"]).groupby("participante", as_index=False).agg(puntos=("puntos", "sum"), plenos=("puntos", lambda s: int((s == 3).sum())))
        if not jornada.empty:
            best = jornada.sort_values(["puntos", "plenos"], ascending=False).iloc[0]
            worst = jornada.sort_values(["puntos", "plenos"], ascending=True).iloc[0]
            st.markdown(f"<div class='big-cta'><span class='ribbon'>Mejor de la jornada</span><h2>{best['participante']} · +{int(best['puntos'])} pts</h2><p>Batacazo provisional: <strong>{worst['participante']}</strong> con {int(worst['puntos'])} puntos. Esto es gasolina para el grupo de WhatsApp.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='big-cta'><span class='ribbon'>Calienta motores</span><h2>La jornada explotará cuando metas el primer resultado</h2><p>La app detectará líderes, batacazos y plenos automáticamente.</p></div>", unsafe_allow_html=True)
with b:
    st.markdown("### 🧠 La comunidad opina")
    bloque_comunidad(apuestas_df, partidos)

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 Clasificación", "⚽ Partidos", "👀 Apuestas", "📊 Estadísticas", "📣 Cómo participar"])

with tab1:
    st.markdown("### La tabla que va a doler")
    if tabla.empty:
        st.info("Sube apuestas para ver la clasificación.")
    else:
        tabla_view = tabla.copy()
        tabla_view["estado"] = tabla_view["posición"].map({1:"👑 líder", 2:"🥈 acechando", 3:"🥉 podio"}).fillna("⚔️ en pelea")
        st.dataframe(
            tabla_view[["posición", "estado", "participante", "puntos", "plenos", "aciertos_1x2", "partidos_puntuados"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "posición": st.column_config.NumberColumn("Pos."),
                "puntos": st.column_config.ProgressColumn("Puntos", min_value=0, max_value=max(1, len(partidos)*3)),
            },
        )
        st.download_button("Descargar clasificación CSV", tabla.to_csv(index=False).encode("utf-8"), "clasificacion_porra_2026.csv", "text/csv")

with tab2:
    st.markdown("### Calendario de la fase de grupos")
    partidos_resultados = partidos[["partido_id", "grupo", "fecha", "local_flag", "local", "visitante_flag", "visitante"]].merge(resultados_df, on="partido_id", how="left")
    partidos_resultados["partido"] = partidos_resultados["local_flag"] + " " + partidos_resultados["local"] + " vs " + partidos_resultados["visitante_flag"] + " " + partidos_resultados["visitante"]
    partidos_resultados["resultado"] = partidos_resultados.apply(lambda r: "Pendiente" if pd.isna(r["goles_local"]) or pd.isna(r["goles_visitante"]) else f"{int(r['goles_local'])}-{int(r['goles_visitante'])}", axis=1)
    st.dataframe(partidos_resultados[["partido_id", "grupo", "fecha", "partido", "resultado"]], hide_index=True, use_container_width=True)

with tab3:
    st.markdown("### Apuestas del resto: transparencia total")
    if apuestas_df.empty:
        st.info("Sube uno o varios Excel para ver las apuestas.")
    else:
        participante_sel = st.selectbox("Participante", ["Todos"] + sorted(apuestas_df["participante"].unique().tolist()))
        vista = apuestas_df.merge(partidos[["partido_id", "grupo", "local_flag", "local", "visitante_flag", "visitante"]], on="partido_id", how="left")
        if participante_sel != "Todos":
            vista = vista[vista["participante"] == participante_sel]
        vista["partido"] = vista["local_flag"] + " " + vista["local"] + " vs " + vista["visitante_flag"] + " " + vista["visitante"]
        vista["apuesta"] = vista["goles_local"].astype(str) + " - " + vista["goles_visitante"].astype(str)
        st.dataframe(vista[["participante", "partido_id", "grupo", "partido", "apuesta"]].sort_values(["participante", "partido_id"]), hide_index=True, use_container_width=True)

with tab4:
    st.markdown("### Radiografía de la porra")
    if detalle.empty:
        st.info("Aún no hay puntos que mostrar.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Jugadores más finos")
            st.dataframe(stats.sort_values(["media_puntos", "plenos"], ascending=False).head(10), hide_index=True, use_container_width=True)
        with col_b:
            st.markdown("#### Partido más discutido")
            resumen = resumen_partido(apuestas_df, resultados_df, partidos)
            st.dataframe(resumen.head(12), hide_index=True, use_container_width=True)
        st.markdown("#### Detalle punto a punto")
        detalle_vista = detalle.merge(partidos[["partido_id", "grupo", "local", "visitante"]], on="partido_id", how="left")
        cols = ["participante", "partido_id", "grupo", "local", "visitante", "goles_local", "goles_visitante", "real_local", "real_visitante", "puntos"]
        st.dataframe(detalle_vista[cols].sort_values(["participante", "partido_id"]), hide_index=True, use_container_width=True)

with tab5:
    st.markdown(
        """
<div class='callout'>
<strong>¿Quieres enganchar a más gente?</strong><br>
Mándales el Excel, enséñales esta web en modo demo y promételes una cosa: podrán ver todas las apuestas, el ranking y los piques desde el móvil durante todo el Mundial.
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("""
### Reglas ultra claras
- 1 punto por acertar el signo: gana local, empate o gana visitante.
- Solo si aciertas el signo: +1 por acertar goles del local y +1 por acertar goles del visitante.
- Pleno exacto: 3 puntos.
- Si fallas el signo: 0 puntos, aunque aciertes algún gol.

### Frase para compartir
**Rellena tu Excel y entra en la Porra Ludópatas 2026. No hace falta saber de fútbol: hace falta tener más suerte que tus amigos.**
""")

st.caption("Diseño inspirado en el ambiente del Mundial 2026. No usa logos oficiales ni material protegido de FIFA.")
