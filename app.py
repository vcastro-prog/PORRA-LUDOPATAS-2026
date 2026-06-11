from __future__ import annotations

from pathlib import Path
import base64
import random
import re
from io import BytesIO
import requests

import pandas as pd
import streamlit as st
import plotly.express as px

from scoring import calcular_puntos, clasificacion, estadisticas_participantes, resumen_partido

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="Porra Ludópatas 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
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
  padding: 34px 34px 38px 34px;
  border-radius: 34px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.18);
  background:
    linear-gradient(115deg, rgba(6,12,34,.96), rgba(20,25,55,.82)),
    radial-gradient(circle at 75% 30%, rgba(255,209,102,.28), transparent 30%);
  box-shadow: 0 25px 80px rgba(0,0,0,.38);
}
@media (max-width: 900px) {}

.hero-content {
  position: relative;
  z-index: 3;
  padding-right: 0;
}
.hero-title {
  white-space: nowrap;
  font-family: 'Bebas Neue', 'Inter', sans-serif;
  font-size: clamp(56px, 7.2vw, 104px);
  line-height: .90;
  margin: 8px 0 12px 0;
  letter-spacing: .02em;
}
.hero-badges {
  display:flex;
  gap:10px;
  flex-wrap:nowrap;
  margin-top:18px;
  align-items:center;
}
.hero-badges .badge {
  white-space:nowrap;
}
.hero-right-logo {
  position: absolute;
  right: 42px;
  top: 50%;
  transform: translateY(-50%);
  width: 165px;
  max-width: 18%;
  z-index: 2;
  display: flex;
  justify-content: center;
  align-items: center;
}
.hero-right-logo img {
  width: 100%;
  height: auto;
  object-fit: contain;
  filter:
    drop-shadow(0 0 18px rgba(255,255,255,.16))
    drop-shadow(0 0 34px rgba(255,209,102,.25));
}
@media (max-width: 1100px) {
  .hero-content {
    padding-right: 0;
  }
  .hero-title {
    font-size: clamp(48px, 6.2vw, 82px);
  }
  .hero-right-logo {
    width: 170px;
    max-width: 22%;
  }
  .hero-badges {
    flex-wrap:wrap;
  }
}
@media (max-width: 900px) {
  .hero-content {
    padding-right: 0;
  }
  .hero-title {
    white-space: normal;
    font-size: 56px;
  }
  .hero-right-logo {
    position: relative;
    right: auto;
    top: auto;
    transform: none;
    width: 165px;
    max-width: 65%;
    margin: 24px auto 0 auto;
  }
  .hero-badges {
    flex-wrap:wrap;
  }
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

/* ===== AJUSTES FINALES PARA ENVIAR AL PROPIETARIO ===== */
.hero {
  min-height: 285px;
}

.hero-title {
  white-space: nowrap;
}

.hero-right-logo {
  overflow: visible;
}

.hero-right-logo img {
  max-height: 230px;
}

/* Métricas superiores más consistentes */
.metric-strip {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

/* Versión tablet */
@media (max-width: 1100px) {
  .block-container {
    padding-left: 1.25rem;
    padding-right: 1.25rem;
  }

  .hero {
    padding: 28px 28px 32px 28px;
  }

  .hero-content {
    padding-right: 0;
  }

  .hero-title {
    font-size: clamp(46px, 6.2vw, 76px);
  }

  .hero-sub {
    max-width: 620px;
  }

  .hero-right-logo {
    width: 145px;
    max-width: 18%;
  }

  .hero-right-logo img {
    max-height: 210px;
  }

  .hero-badges {
    flex-wrap: wrap;
  }

  .metric-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Versión móvil: mobile first para compartir por WhatsApp */
@media (max-width: 760px) {
  .block-container {
    padding-top: .7rem;
    padding-left: .75rem;
    padding-right: .75rem;
  }

  .hero {
    padding: 22px 20px 24px 20px;
    border-radius: 26px;
    text-align: center;
    min-height: auto;
  }

  .hero-content {
    padding-right: 0;
  }

  .kicker {
    font-size: .70rem;
    letter-spacing: .14em;
  }

  .hero-title {
    white-space: normal;
    font-size: clamp(44px, 17vw, 64px);
    line-height: .88;
    margin-top: 10px;
  }

  .hero-sub {
    font-size: .98rem;
    line-height: 1.35;
    max-width: none;
    margin-left: auto;
    margin-right: auto;
  }

  .hero-badges,
  .badge-row {
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .badge,
  .hero-badges .badge {
    font-size: .84rem;
    padding: 8px 10px;
    white-space: nowrap;
  }

  .hero-right-logo {
    position: relative;
    right: auto;
    top: auto;
    transform: none;
    width: 138px;
    max-width: 58%;
    margin: 18px auto 0 auto;
  }

  .hero-right-logo img {
    max-height: 170px;
  }

  .metric-strip {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .card {
    border-radius: 22px;
    padding: 18px 18px;
  }

  .stat-value {
    font-size: 1.85rem;
  }

  .podium {
    grid-template-columns: 1fr;
  }

  .podium-card.first {
    padding-top: 18px;
  }

  .match-card {
    padding: 13px 14px;
  }

  h2 {
    font-size: 1.55rem !important;
  }

  h3 {
    font-size: 1.25rem !important;
  }

  div[data-testid="stHorizontalBlock"] {
    gap: .75rem;
  }
}

/* Móviles muy pequeños */
@media (max-width: 420px) {
  .hero-title {
    font-size: 46px;
  }

  .hero-right-logo {
    width: 125px;
  }

  .badge,
  .hero-badges .badge {
    font-size: .78rem;
    padding: 7px 9px;
  }

  .hero-sub {
    font-size: .92rem;
  }
}


.flag-img {
  width: 24px;
  height: 18px;
  object-fit: cover;
  border-radius: 3px;
  vertical-align: -3px;
  margin-right: 6px;
  box-shadow: 0 0 0 1px rgba(255,255,255,.22);
}
.flag-img + span,
.flag-img-fallback {
  margin-right: 4px;
}


.table-card {
  overflow-x: auto;
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.045);
}
.pretty-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .95rem;
}
.pretty-table th {
  color: var(--muted);
  text-align: left;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255,255,255,.16);
  background: rgba(255,255,255,.05);
}
.pretty-table td {
  padding: 13px 16px;
  border-bottom: 1px solid rgba(255,255,255,.08);
  vertical-align: middle;
}
.pretty-table tr:last-child td {
  border-bottom: none;
}
.pretty-table .flag-img {
  margin-right: 7px;
}
@media (max-width: 760px) {
  .pretty-table {
    font-size: .84rem;
  }
  .pretty-table th,
  .pretty-table td {
    padding: 10px 11px;
  }
}


.prediction-card {
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.055);
  padding: 16px 18px;
  margin-bottom: 16px;
  box-shadow: 0 14px 40px rgba(0,0,0,.18);
}
.prediction-title {
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 10px;
}
.prediction-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .94rem;
}
.prediction-table th {
  color: var(--muted);
  text-align: left;
  padding: 10px 8px;
  border-bottom: 1px solid rgba(255,255,255,.14);
}
.prediction-table td {
  padding: 10px 8px;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.prediction-table tr:last-child td {
  border-bottom: none;
}
.prediction-table tr.clasificado td {
  background: rgba(71,245,155,.08);
}
.prediction-table tr.clasificado td:first-child {
  color: var(--green);
  font-weight: 900;
}


@media (max-width: 760px) {
  .prediction-card {
    padding: 12px 14px;
  }
  .prediction-table {
    font-size: .82rem;
  }
}


/* ===== HERO PREMIUM LIMPIO: sin banner duplicado ===== */
.hero-pro {
  min-height: 410px;
  padding: 38px 42px;
  isolation: isolate;
}

.hero-pro::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 72% 44%, rgba(255,209,102,.23), transparent 26%),
    radial-gradient(circle at 88% 22%, rgba(31,228,255,.20), transparent 28%),
    linear-gradient(115deg, rgba(5,10,27,.98), rgba(13,18,45,.94) 55%, rgba(25,16,50,.88));
  z-index: 0;
}

.hero-pro::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(150deg, transparent 0 42%, rgba(31,228,255,.13) 43%, transparent 46%),
    linear-gradient(25deg, transparent 0 58%, rgba(255,78,205,.10) 59%, transparent 62%);
  opacity: .65;
  z-index: 1;
  pointer-events: none;
}

.hero-inner-pro {
  position: relative;
  z-index: 3;
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(260px, .75fr);
  gap: 28px;
  align-items: center;
}

.hero-main-pro {
  position: relative;
  z-index: 4;
}

.hero-title-pro {
  font-family: 'Bebas Neue', 'Inter', sans-serif;
  font-size: clamp(76px, 9vw, 138px);
  line-height: .82;
  letter-spacing: .018em;
  margin: 8px 0 16px 0;
  text-transform: uppercase;
  text-shadow: 0 12px 34px rgba(0,0,0,.35);
}

.hero-title-pro .line1 {
  color: #fff;
}

.hero-title-pro .line2 {
  display: block;
}

.hero-title-pro .gold {
  background: linear-gradient(90deg, #FFD166, #fff4c2 45%, #22E6FF);
  -webkit-background-clip: text;
  color: transparent;
}

.hero-title-pro .year {
  color: #fff;
  margin-left: 18px;
}

.hero-sub-pro {
  max-width: 780px;
  color: var(--muted);
  font-size: clamp(1rem, 1.5vw, 1.22rem);
  line-height: 1.45;
}

.hero-badges-pro {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 24px;
}

.hero-badges-pro .badge {
  background: rgba(255,255,255,.105);
  border: 1px solid rgba(255,255,255,.19);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
}

.hero-trophy-zone {
  position: relative;
  min-height: 330px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-trophy-zone::before {
  content: "";
  position: absolute;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(255,209,102,.20), transparent 58%),
    radial-gradient(circle, rgba(31,228,255,.10), transparent 72%);
  filter: blur(2px);
  animation: trophyAura 4.5s ease-in-out infinite;
}

.hero-trophy-pro {
  position: relative;
  z-index: 2;
  width: min(285px, 72%);
  max-height: 340px;
  object-fit: contain;
  filter:
    drop-shadow(0 0 16px rgba(255,209,102,.34))
    drop-shadow(0 0 36px rgba(31,228,255,.13));
  animation: trophyGlow 4.2s ease-in-out infinite;
}

.participants-burst {
  position: absolute;
  top: 18px;
  right: 4px;
  z-index: 4;
  transform: rotate(-7deg);
  padding: 10px 16px 12px 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(31,228,255,.18), rgba(255,78,205,.18));
  border: 1px solid rgba(255,255,255,.18);
  box-shadow: 0 14px 44px rgba(0,0,0,.26);
}

.participants-burst .num {
  display: block;
  font-family: 'Bebas Neue', 'Inter', sans-serif;
  font-size: clamp(42px, 5vw, 70px);
  line-height: .8;
  color: var(--cyan);
  text-shadow: 0 0 22px rgba(31,228,255,.42);
}

.participants-burst .txt {
  display: block;
  font-weight: 900;
  font-style: italic;
  color: #fff;
  letter-spacing: .04em;
}

.hero-slogan {
  position: absolute;
  left: 50%;
  bottom: 4px;
  transform: translateX(-50%);
  z-index: 4;
  white-space: nowrap;
  padding: 10px 18px;
  border-radius: 999px;
  background: rgba(7,10,19,.58);
  border: 1px solid rgba(255,255,255,.14);
  font-weight: 900;
  letter-spacing: .04em;
}

.hero-slogan .cyan { color: var(--cyan); }
.hero-slogan .gold { color: var(--gold); }

@keyframes trophyGlow {
  0%, 100% {
    filter:
      drop-shadow(0 0 14px rgba(255,209,102,.28))
      drop-shadow(0 0 28px rgba(31,228,255,.10));
  }
  50% {
    filter:
      drop-shadow(0 0 24px rgba(255,209,102,.46))
      drop-shadow(0 0 42px rgba(31,228,255,.18));
  }
}

@keyframes trophyAura {
  0%, 100% { opacity: .72; transform: scale(.98); }
  50% { opacity: 1; transform: scale(1.04); }
}

@media (max-width: 900px) {
  .hero-pro {
    padding: 28px 22px 32px 22px;
    text-align: center;
  }

  .hero-inner-pro {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .hero-title-pro {
    font-size: clamp(58px, 16vw, 86px);
  }

  .hero-title-pro .year {
    display: block;
    margin-left: 0;
  }

  .hero-sub-pro {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-badges-pro {
    justify-content: center;
  }

  .hero-trophy-zone {
    min-height: 270px;
  }

  .hero-trophy-zone::before {
    width: 270px;
    height: 270px;
  }

  .hero-trophy-pro {
    width: min(210px, 58%);
  }

  .participants-burst {
    top: 0;
    right: 12%;
    transform: rotate(-5deg) scale(.86);
  }

  .hero-slogan {
    position: relative;
    left: auto;
    bottom: auto;
    transform: none;
    display: inline-block;
    margin-top: 12px;
    white-space: normal;
  }
}


/* ===== TARJETAS RESUMEN DENTRO DE LA PORTADA ===== */
.hero-summary-inline {
  position: relative;
  z-index: 4;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 26px;
}

.hero-summary-inline .summary-card {
  border-radius: 22px;
  padding: 15px 16px;
  text-align: left;
  background:
    linear-gradient(135deg, rgba(31,228,255,.13), rgba(255,78,205,.10)),
    rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.18);
  box-shadow:
    0 16px 40px rgba(0,0,0,.22),
    inset 0 1px 0 rgba(255,255,255,.08);
}

.hero-summary-inline .summary-card.highlight {
  background:
    linear-gradient(135deg, rgba(255,209,102,.19), rgba(31,228,255,.10)),
    rgba(255,255,255,.08);
}

.hero-summary-inline .summary-label {
  color: var(--muted);
  font-size: .68rem;
  text-transform: uppercase;
  letter-spacing: .13em;
  font-weight: 900;
}

.hero-summary-inline .summary-value {
  color: #fff;
  font-size: clamp(1.35rem, 2.2vw, 2.05rem);
  line-height: 1.08;
  font-weight: 900;
  margin-top: 7px;
  word-break: break-word;
}

.hero-summary-inline .summary-note {
  color: var(--muted);
  font-size: .78rem;
  margin-top: 5px;
}

@media (max-width: 1100px) {
  .hero-summary-inline {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .hero-summary-inline {
    grid-template-columns: 1fr;
    gap: 10px;
    margin-top: 18px;
  }

  .hero-summary-inline .summary-card {
    padding: 16px 17px;
  }

  .hero-summary-inline .summary-value {
    font-size: 1.85rem;
  }
}


/* ===== TARJETAS FLOTANTES JUNTO A LA COPA ===== */
.hero-trophy-zone {
  min-height: 390px;
}

.floating-stat {
  position: absolute;
  z-index: 5;
  padding: 10px 16px 12px 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(31,228,255,.18), rgba(255,78,205,.18));
  border: 1px solid rgba(255,255,255,.18);
  box-shadow: 0 14px 44px rgba(0,0,0,.26);
  text-align: center;
  min-width: 145px;
  backdrop-filter: blur(6px);
}

.floating-stat .num {
  display: block;
  font-family: 'Bebas Neue', 'Inter', sans-serif;
  font-size: clamp(32px, 3.2vw, 52px);
  line-height: .86;
  color: var(--cyan);
  text-shadow: 0 0 22px rgba(31,228,255,.42);
}

.floating-stat .txt {
  display: block;
  font-weight: 900;
  font-style: italic;
  color: #fff;
  letter-spacing: .03em;
  font-size: .92rem;
  margin-top: 4px;
}

.floating-stat .note {
  display: block;
  color: var(--muted);
  font-size: .72rem;
  margin-top: 2px;
  white-space: nowrap;
}

/* Conservamos la tarjeta de participantes pero usando la misma base */
.participants-burst {
  min-width: 150px;
}

/* Posiciones escritorio */
.stat-participantes {
  top: 18px;
  right: 4px;
  transform: rotate(-7deg);
}

.stat-jugados {
  top: 88px;
  left: -12px;
  transform: rotate(5deg);
}

.stat-lider {
  bottom: 34px;
  right: -10px;
  transform: rotate(4deg);
  min-width: 190px;
}

.stat-maximo {
  bottom: 18px;
  left: 0;
  transform: rotate(-5deg);
}

/* Ya no usamos las tarjetas resumen inferiores dentro del hero */
.hero-summary-inline {
  display: none !important;
}

@media (max-width: 900px) {
  .hero-trophy-zone {
    min-height: 430px;
  }

  .floating-stat {
    min-width: 132px;
    padding: 9px 13px 11px 13px;
  }

  .floating-stat .num {
    font-size: 40px;
  }

  .floating-stat .txt {
    font-size: .84rem;
  }

  .floating-stat .note {
    font-size: .66rem;
  }

  .stat-participantes {
    top: 0;
    right: 8%;
    transform: rotate(-5deg) scale(.86);
  }

  .stat-jugados {
    top: 92px;
    left: 3%;
    transform: rotate(5deg) scale(.82);
  }

  .stat-lider {
    bottom: 34px;
    right: 1%;
    transform: rotate(4deg) scale(.80);
    min-width: 170px;
  }

  .stat-maximo {
    bottom: 20px;
    left: 3%;
    transform: rotate(-5deg) scale(.82);
  }

  .hero-trophy-pro {
    width: min(205px, 54%);
  }
}

@media (max-width: 420px) {
  .hero-trophy-zone {
    min-height: 455px;
  }

  .stat-jugados {
    top: 88px;
    left: -2%;
  }

  .stat-lider {
    bottom: 42px;
    right: -5%;
  }

  .stat-maximo {
    bottom: 18px;
    left: -1%;
  }
}


/* ===== MÓVIL TIPO ESCRITORIO: COPA GRANDE + TARJETAS FLOTANTES ===== */
@media (max-width: 760px) {
  .hero-trophy-zone {
    position: relative !important;
    display: block !important;
    min-height: 430px !important;
    margin-top: 18px;
  }

  .hero-trophy-zone::before {
    width: 310px !important;
    height: 310px !important;
    left: 50%;
    top: 95px;
    transform: translateX(-50%);
    opacity: .95;
  }

  .hero-trophy-pro {
    position: absolute !important;
    z-index: 3;
    width: 215px !important;
    max-height: 285px !important;
    left: 50%;
    top: 130px;
    transform: translateX(-50%);
  }

  .floating-stat,
  .participants-burst {
    position: absolute !important;
    z-index: 5;
    min-width: 128px !important;
    width: auto !important;
    max-width: 190px !important;
    padding: 9px 13px 11px 13px;
    border-radius: 19px;
  }

  .floating-stat .num,
  .participants-burst .num {
    font-size: 37px !important;
    line-height: .84;
  }

  .floating-stat .txt,
  .participants-burst .txt {
    font-size: .80rem !important;
    margin-top: 3px;
  }

  .floating-stat .note {
    font-size: .64rem !important;
    margin-top: 2px;
  }

  .stat-participantes {
    top: 8px !important;
    right: 4% !important;
    left: auto !important;
    bottom: auto !important;
    transform: rotate(-7deg) !important;
  }

  .stat-jugados {
    top: 74px !important;
    left: 2% !important;
    right: auto !important;
    bottom: auto !important;
    transform: rotate(6deg) !important;
  }

  .stat-maximo {
    bottom: 18px !important;
    left: 3% !important;
    top: auto !important;
    right: auto !important;
    transform: rotate(-6deg) !important;
  }

  .stat-lider {
    bottom: 16px !important;
    right: 1% !important;
    top: auto !important;
    left: auto !important;
    transform: rotate(5deg) !important;
    min-width: 175px !important;
    max-width: 205px !important;
  }

  .stat-lider .num {
    font-size: 28px !important;
    white-space: nowrap;
  }
}

@media (max-width: 420px) {
  .hero-trophy-zone {
    min-height: 410px !important;
  }

  .hero-trophy-zone::before {
    width: 285px !important;
    height: 285px !important;
    top: 92px;
  }

  .hero-trophy-pro {
    width: 198px !important;
    max-height: 265px !important;
    top: 128px;
  }

  .floating-stat,
  .participants-burst {
    min-width: 118px !important;
    max-width: 172px !important;
    padding: 8px 11px 10px 11px;
  }

  .floating-stat .num,
  .participants-burst .num {
    font-size: 34px !important;
  }

  .stat-lider {
    min-width: 160px !important;
    max-width: 185px !important;
  }

  .stat-lider .num {
    font-size: 24px !important;
  }

  .stat-participantes {
    right: 1% !important;
  }

  .stat-jugados {
    left: -1% !important;
  }

  .stat-maximo {
    left: -1% !important;
  }

  .stat-lider {
    right: -2% !important;
  }
}


/* ===== MÓVIL MÁS COMPACTO: TARJETAS PEGADAS A LA COPA ===== */
@media (max-width: 760px) {
  .hero-trophy-zone {
    min-height: 330px !important;
    margin-top: 8px !important;
  }

  .hero-trophy-zone::before {
    width: 270px !important;
    height: 270px !important;
    top: 58px !important;
  }

  .hero-trophy-pro {
    width: 190px !important;
    max-height: 250px !important;
    top: 86px !important;
  }

  .floating-stat,
  .participants-burst {
    padding: 8px 11px 9px 11px !important;
    border-radius: 18px !important;
    min-width: 116px !important;
    max-width: 172px !important;
  }

  .floating-stat .num,
  .participants-burst .num {
    font-size: 33px !important;
  }

  .floating-stat .txt,
  .participants-burst .txt {
    font-size: .75rem !important;
  }

  .floating-stat .note {
    font-size: .60rem !important;
  }

  .stat-participantes {
    top: 12px !important;
    right: 6% !important;
    transform: rotate(-7deg) !important;
  }

  .stat-jugados {
    top: 58px !important;
    left: 4% !important;
    transform: rotate(6deg) !important;
  }

  .stat-maximo {
    bottom: 18px !important;
    left: 4% !important;
    transform: rotate(-6deg) !important;
  }

  .stat-lider {
    bottom: 18px !important;
    right: 3% !important;
    min-width: 158px !important;
    max-width: 184px !important;
    transform: rotate(5deg) !important;
  }

  .stat-lider .num {
    font-size: 23px !important;
  }
}

@media (max-width: 420px) {
  .hero-trophy-zone {
    min-height: 315px !important;
  }

  .hero-trophy-zone::before {
    width: 250px !important;
    height: 250px !important;
    top: 56px !important;
  }

  .hero-trophy-pro {
    width: 176px !important;
    max-height: 232px !important;
    top: 84px !important;
  }

  .floating-stat,
  .participants-burst {
    min-width: 108px !important;
    max-width: 160px !important;
    padding: 7px 10px 8px 10px !important;
  }

  .floating-stat .num,
  .participants-burst .num {
    font-size: 30px !important;
  }

  .stat-lider .num {
    font-size: 21px !important;
  }

  .stat-participantes {
    top: 10px !important;
    right: 2% !important;
  }

  .stat-jugados {
    top: 54px !important;
    left: 0 !important;
  }

  .stat-maximo {
    bottom: 14px !important;
    left: 0 !important;
  }

  .stat-lider {
    bottom: 14px !important;
    right: -1% !important;
  }
}


/* ===== AJUSTE FINAL: COPA MÁS GRANDE EN MÓVIL ===== */
@media (max-width: 760px) {
  .hero-trophy-zone {
    min-height: 360px !important;
    margin-top: 6px !important;
  }

  .hero-trophy-zone::before {
    width: 335px !important;
    height: 335px !important;
    top: 30px !important;
  }

  .hero-trophy-pro {
    width: 255px !important;
    max-height: 340px !important;
    top: 52px !important;
  }

  .stat-participantes {
    top: 8px !important;
    right: 3% !important;
  }

  .stat-jugados {
    top: 58px !important;
    left: 2% !important;
  }

  .stat-maximo {
    bottom: 18px !important;
    left: 2% !important;
  }

  .stat-lider {
    bottom: 18px !important;
    right: 1% !important;
  }
}

@media (max-width: 420px) {
  .hero-trophy-zone {
    min-height: 345px !important;
  }

  .hero-trophy-zone::before {
    width: 310px !important;
    height: 310px !important;
    top: 30px !important;
  }

  .hero-trophy-pro {
    width: 235px !important;
    max-height: 315px !important;
    top: 54px !important;
  }

  .stat-participantes {
    top: 8px !important;
    right: 0 !important;
  }

  .stat-jugados {
    top: 54px !important;
    left: -1% !important;
  }

  .stat-maximo {
    bottom: 14px !important;
    left: -1% !important;
  }

  .stat-lider {
    bottom: 14px !important;
    right: -2% !important;
  }
}

/* ===== AJUSTE FINAL DE ESCRITORIO ===== */
@media (min-width: 901px) {
  .hero-inner-pro {
    grid-template-columns: minmax(0, 1.35fr) minmax(470px, .85fr);
    gap: 34px;
  }

  .hero-title-pro {
    font-size: clamp(72px, 6.5vw, 104px);
    line-height: .88;
  }

  .hero-title-pro .line1,
  .hero-title-pro .line2 {
    display: block;
  }

  .hero-title-pro .line2 {
    white-space: nowrap;
  }

  .hero-title-pro .year {
    margin-left: 16px;
  }

  .hero-trophy-zone {
    min-height: 410px;
  }

  .hero-trophy-pro {
    width: min(245px, 55%);
    max-height: 320px;
  }

  .stat-participantes {
    top: 8px;
    right: 0;
  }

  .stat-jugados {
    top: 78px;
    left: 0;
  }

  .stat-maximo {
    bottom: 6px;
    left: 0;
  }

  .stat-lider {
    right: 0;
    bottom: 4px;
    width: 245px;
    min-width: 0;
  }

  .stat-lider .num {
    font-size: clamp(27px, 2.2vw, 36px);
    line-height: .94;
    overflow-wrap: anywhere;
  }
}

/* ===== NAVEGACION PRINCIPAL EN MOVIL ===== */
@media (max-width: 760px) {
  div[data-testid="stRadio"][aria-label="Sección"] > div {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 8px !important;
    width: 100% !important;
  }

  div[data-testid="stRadio"][aria-label="Sección"] label {
    width: 100% !important;
    min-height: 46px !important;
    margin: 0 !important;
    padding: 9px 13px !important;
    border: 1px solid rgba(255,255,255,.14) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,.055) !important;
    align-items: center !important;
  }

  div[data-testid="stRadio"][aria-label="Sección"] label:has(input:checked) {
    border-color: rgba(255,209,102,.72) !important;
    background:
      linear-gradient(90deg, rgba(255,209,102,.16), rgba(31,228,255,.10)),
      rgba(255,255,255,.075) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.20) !important;
  }

  div[data-testid="stRadio"][aria-label="Sección"] label > div:first-child {
    flex: 0 0 auto !important;
    margin-right: 10px !important;
  }

  div[data-testid="stRadio"][aria-label="Sección"] label p {
    margin: 0 !important;
    font-size: .98rem !important;
    line-height: 1.2 !important;
    white-space: normal !important;
  }
}

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




def normalizar_texto_bandera(valor: str) -> str:
    """Normaliza nombres de selecciones para encontrar banderas."""
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    reemplazos = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "À": "A", "È": "E", "Ì": "I", "Ò": "O", "Ù": "U",
        "Ü": "U", "Ñ": "N", "Ç": "C",
        ".": "", ",": "", "-": " ", "_": " ",
    }
    for origen, destino in reemplazos.items():
        texto = texto.replace(origen, destino)

    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def equipo_canonico(nombre: str) -> str:
    """Unifica variantes/erratas habituales de selecciones.

    Evita duplicados en grupos:
    - COSTA DE MARFIL / COSTA DEMARFIL
    - R.D.CONGO / R.D. CONGO
    - CROACIA / CROCIA
    """
    if pd.isna(nombre):
        return ""

    texto = normalizar_texto_bandera(nombre)

    equivalencias = {
        "COSTA DEMARFIL": "COSTA DE MARFIL",
        "COSTA DE MARFIL": "COSTA DE MARFIL",
        "RD CONGO": "R.D. CONGO",
        "R D CONGO": "R.D. CONGO",
        "RDCONGO": "R.D. CONGO",
        "R.D.CONGO": "R.D. CONGO",
        "R.D. CONGO": "R.D. CONGO",
        "CROCIA": "CROACIA",
        "CROACIA": "CROACIA",
        "REP CHECA": "REP. CHECA",
        "REPUBLICA CHECA": "REP. CHECA",
        "CHEQUIA": "REP. CHECA",
        "ESPANA": "ESPAÑA",
        "TURQUIA": "TURQUÍA",
        "BELGICA": "BÉLGICA",
        "JAPON": "JAPÓN",
        "TUNEZ": "TÚNEZ",
        "IRAN": "IRÁN",
        "ARABIA SAUDI": "ARABIA SAUDÍ",
        "UZBEKISTAN": "UZBEKISTÁN",
        "PANAMA": "PANAMÁ",
    }

    return equivalencias.get(texto, str(nombre).strip())


def canonizar_partidos_df(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica nombres canónicos a columnas local/visitante si existen."""
    out = df.copy()
    if "local" in out.columns:
        out["local"] = out["local"].apply(equipo_canonico)
    if "visitante" in out.columns:
        out["visitante"] = out["visitante"].apply(equipo_canonico)
    return out


FLAG_NORMALIZADO = {
    "RD CONGO": "🇨🇩",
    "R.D. CONGO": "🇨🇩",
    "ALEMANIA": "🇩🇪",
    "ESCOCIA": "🏴",
    "HUNGRIA": "🇭🇺",
    "SUIZA": "🇨🇭",
    "ESPANA": "🇪🇸",
    "CROACIA": "🇭🇷",
    "CROCIA": "🇭🇷",
    "ITALIA": "🇮🇹",
    "ALBANIA": "🇦🇱",
    "POLONIA": "🇵🇱",
    "PAISES BAJOS": "🇳🇱",
    "HOLANDA": "🇳🇱",
    "ESLOVENIA": "🇸🇮",
    "DINAMARCA": "🇩🇰",
    "SERBIA": "🇷🇸",
    "INGLATERRA": "🏴",
    "RUMANIA": "🇷🇴",
    "UCRANIA": "🇺🇦",
    "BELGICA": "🇧🇪",
    "ESLOVAQUIA": "🇸🇰",
    "AUSTRIA": "🇦🇹",
    "FRANCIA": "🇫🇷",
    "TURQUIA": "🇹🇷",
    "GEORGIA": "🇬🇪",
    "PORTUGAL": "🇵🇹",
    "CHEQUIA": "🇨🇿",
    "REPUBLICA CHECA": "🇨🇿",
    "REP CHECA": "🇨🇿",

    "MEXICO": "🇲🇽",
    "SUDAFRICA": "🇿🇦",
    "COREA DEL SUR": "🇰🇷",
    "CANADA": "🇨🇦",
    "BOSNIA": "🇧🇦",
    "QATAR": "🇶🇦",
    "BRASIL": "🇧🇷",
    "MARRUECOS": "🇲🇦",
    "HAITI": "🇭🇹",
    "ESTADOS UNIDOS": "🇺🇸",
    "USA": "🇺🇸",
    "PARAGUAY": "🇵🇾",
    "AUSTRALIA": "🇦🇺",
    "COSTA DE MARFIL": "🇨🇮",
    "COSTA DEMARFIL": "🇨🇮",
    "ECUADOR": "🇪🇨",
    "JAPON": "🇯🇵",
    "SUECIA": "🇸🇪",
    "TUNEZ": "🇹🇳",
    "EGIPTO": "🇪🇬",
    "IRAN": "🇮🇷",
    "NUEVA ZELANDA": "🇳🇿",
    "ARABIA SAUDI": "🇸🇦",
    "URUGUAY": "🇺🇾",
    "CABO VERDE": "🇨🇻",
    "SENEGAL": "🇸🇳",
    "IRAQ": "🇮🇶",
    "NORUEGA": "🇳🇴",
    "ARGENTINA": "🇦🇷",
    "ARGELIA": "🇩🇿",
    "JORDANIA": "🇯🇴",
    "R D CONGO": "🇨🇩",
    "RDCONGO": "🇨🇩",
    "UZBEKISTAN": "🇺🇿",
    "COLOMBIA": "🇨🇴",
    "GHANA": "🇬🇭",
    "PANAMA": "🇵🇦",
}


def bandera_equipo(nombre: str) -> str:
    return FLAG_NORMALIZADO.get(normalizar_texto_bandera(nombre), "🏳️")


ISO_BANDERAS = {
    "ALEMANIA": "de",
    "ESCOCIA": "gb-sct",
    "HUNGRIA": "hu",
    "SUIZA": "ch",
    "ESPANA": "es",
    "CROACIA": "hr",
    "CROCIA": "hr",
    "ITALIA": "it",
    "ALBANIA": "al",
    "POLONIA": "pl",
    "PAISES BAJOS": "nl",
    "HOLANDA": "nl",
    "ESLOVENIA": "si",
    "DINAMARCA": "dk",
    "SERBIA": "rs",
    "INGLATERRA": "gb-eng",
    "RUMANIA": "ro",
    "UCRANIA": "ua",
    "BELGICA": "be",
    "ESLOVAQUIA": "sk",
    "AUSTRIA": "at",
    "FRANCIA": "fr",
    "TURQUIA": "tr",
    "GEORGIA": "ge",
    "PORTUGAL": "pt",
    "CHEQUIA": "cz",
    "REPUBLICA CHECA": "cz",
    "REP CHECA": "cz",

    "MEXICO": "mx",
    "CANADA": "ca",
    "ESTADOS UNIDOS": "us",
    "USA": "us",
    "BRASIL": "br",
    "ARGENTINA": "ar",
    "URUGUAY": "uy",
    "COLOMBIA": "co",
    "ECUADOR": "ec",
    "PARAGUAY": "py",
    "AUSTRALIA": "au",
    "JAPON": "jp",
    "COREA DEL SUR": "kr",
    "MARRUECOS": "ma",
    "SENEGAL": "sn",
    "GHANA": "gh",
    "TUNEZ": "tn",
    "ARGELIA": "dz",
    "EGIPTO": "eg",
    "SUDAFRICA": "za",
    "QATAR": "qa",
    "IRAN": "ir",
    "ARABIA SAUDI": "sa",
    "NUEVA ZELANDA": "nz",
    "NORUEGA": "no",
    "SUECIA": "se",
    "PANAMA": "pa",
    "HAITI": "ht",
    "CABO VERDE": "cv",
    "COSTA DE MARFIL": "ci",
    "COSTA DEMARFIL": "ci",
    "BOSNIA": "ba",
    "JORDANIA": "jo",
    "UZBEKISTAN": "uz",
    "IRAQ": "iq",
    "R.D. CONGO": "cd",
    "RD CONGO": "cd",
}



def partido_html(local: str, visitante: str) -> str:
    """Devuelve partido con imágenes de banderas para HTML."""
    return f"{bandera_html(local)} {local} <span style='color:#FFD166'>vs</span> {bandera_html(visitante)} {visitante}"


def partido_texto_con_banderas(local: str, visitante: str) -> str:
    """Versión para tablas/dataframes. Usa emoji si el sistema lo soporta."""
    return f"{bandera_equipo(local)} {local} vs {bandera_equipo(visitante)} {visitante}"


def bandera_html(nombre: str) -> str:
    """Devuelve una imagen de bandera para escritorio.

    Los emoji de banderas no se renderizan bien en muchos equipos de escritorio
    y aparecen como SK, RO, GE... Por eso en las tarjetas usamos imágenes.
    """
    codigo = ISO_BANDERAS.get(normalizar_texto_bandera(nombre), "")
    if not codigo:
        return "<span class='flag-img-fallback'>🏳️</span>"
    return (
        f"<img class='flag-img' "
        f"src='https://flagcdn.com/24x18/{codigo}.png' "
        f"srcset='https://flagcdn.com/48x36/{codigo}.png 2x' "
        f"alt='{nombre}'>"
    )


@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def cargar_partidos() -> pd.DataFrame:
    """Carga el calendario y los grupos.

    Si GOOGLE_SHEET_ID está configurado, los partidos se generan desde la
    propia hoja definitiva del Mundial, no desde data/partidos.csv.

    La hoja tiene bloques como:
        Gp. A | 11 de Junio | PARTIDO 1 | MEXICO | 2 | SUDÁFRICA | 0

    El grupo se toma de la columna A y se arrastra hasta el siguiente grupo.
    """
    sheet_id = obtener_google_sheet_id() if "obtener_google_sheet_id" in globals() else ""

    if sheet_id:
        try:
            xls = leer_excel_google_sheet(sheet_id)

            hojas_excluidas = {
                "RESULTADOS", "CLASIFICACION", "CLASIFICACIÓN", "RESUMEN",
                "INSTRUCCIONES", "PARTIDOS", "CONFIG", "CONFIGURACION", "CONFIGURACIÓN"
            }

            hoja_base = None
            for sheet_name in xls.sheet_names:
                if sheet_name.strip().upper() not in hojas_excluidas:
                    hoja_base = sheet_name
                    break

            if hoja_base is None:
                raise ValueError("No encuentro ninguna hoja de participante para extraer partidos y grupos.")

            df = pd.read_excel(xls, sheet_name=hoja_base, header=None)

            registros = []
            grupo_actual = ""

            n_rows, n_cols = df.shape

            for r in range(n_rows):
                if n_cols > 0:
                    valor_grupo = df.iat[r, 0]
                    if not pd.isna(valor_grupo):
                        texto_grupo = str(valor_grupo).strip()
                        if texto_grupo.upper().startswith("GP"):
                            grupo_actual = texto_grupo

                for c in range(n_cols):
                    valor = df.iat[r, c]

                    if pd.isna(valor):
                        continue

                    texto = str(valor).strip().upper()
                    match = re.search(r"PARTIDO\s*([0-9]+)", texto)

                    if not match:
                        continue

                    partido_id = int(match.group(1))

                    if c - 1 < 0 or c + 3 >= n_cols:
                        continue

                    fecha = limpiar_nombre_equipo(df.iat[r, c - 1])
                    local = limpiar_nombre_equipo(df.iat[r, c + 1])
                    visitante = limpiar_nombre_equipo(df.iat[r, c + 3])

                    if not local or not visitante:
                        continue

                    registros.append({
                        "partido_id": partido_id,
                        "grupo": grupo_actual,
                        "fecha": fecha,
                        "local": local,
                        "visitante": visitante,
                    })

            partidos_google = pd.DataFrame(registros)

            if partidos_google.empty:
                raise ValueError("No he podido extraer partidos desde la hoja de participante.")

            partidos_google = (
                partidos_google
                .drop_duplicates(subset=["partido_id"], keep="first")
                .sort_values("partido_id")
                .reset_index(drop=True)
            )

            partidos_google = canonizar_partidos_df(partidos_google)
            partidos_google["local_flag"] = partidos_google["local"].apply(lambda x: bandera_equipo(str(x)))
            partidos_google["visitante_flag"] = partidos_google["visitante"].apply(lambda x: bandera_equipo(str(x)))

            return partidos_google

        except Exception as e:
            st.error(
                "No pude generar partidos y grupos desde la Google Sheet configurada. "
                "No usaré data/partidos.csv para evitar mostrar grupos antiguos."
            )
            st.exception(e)
            st.stop()

    df = pd.read_csv(DATA_DIR / "partidos.csv")
    df = canonizar_partidos_df(df)
    df["local_flag"] = df["local"].apply(lambda x: bandera_equipo(str(x)))
    df["visitante_flag"] = df["visitante"].apply(lambda x: bandera_equipo(str(x)))
    return df





def leer_secret(nombre: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(nombre, default)).strip()
    except Exception:
        return default


def obtener_google_sheet_id() -> str:
    """Lee el ID de la Google Sheet desde Streamlit Secrets.

    Ejemplo:
        GOOGLE_SHEET_ID = "1_3apexP0SaMJ9RPlyd4Tyr39DAWpBBXK"

    También acepta una URL completa por compatibilidad.
    """
    valor = leer_secret("GOOGLE_SHEET_ID") or leer_secret("GOOGLE_SHEET_URL")
    if not valor:
        return ""

    match = re.search(r"/d/([a-zA-Z0-9-_]+)", valor)
    return match.group(1) if match else valor.strip()


@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def descargar_google_sheet_como_excel(sheet_id: str) -> bytes:
    """Descarga una Google Sheet pública como archivo XLSX.

    La hoja debe estar compartida como:
        Cualquiera con el enlace -> Lector
    """
    if not sheet_id:
        return b""

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    response = requests.get(url, timeout=45)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "html" in content_type.lower():
        raise RuntimeError(
            "Google devolvió HTML en lugar de XLSX. Revisa que la hoja sea pública con permiso de lectura."
        )

    return response.content


def leer_excel_google_sheet(sheet_id: str) -> pd.ExcelFile:
    excel_bytes = descargar_google_sheet_como_excel(sheet_id)
    return pd.ExcelFile(BytesIO(excel_bytes), engine="openpyxl")


def limpiar_nombre_equipo(valor) -> str:
    if pd.isna(valor):
        return ""
    texto = str(valor).strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def extraer_apuestas_de_hoja_excel(df: pd.DataFrame, nombre_hoja: str, partidos_ref: pd.DataFrame) -> pd.DataFrame:
    """Extrae apuestas de una hoja de participante del formato real Mundial 2026.

    - Nombre real del participante en B3.
    - Bloques por partido:
      FECHA | PARTIDO X | LOCAL | GOLES_LOCAL | VISITANTE | GOLES_VISITANTE
    """
    columnas = ["participante", "partido_id", "goles_local", "goles_visitante"]

    if df.empty:
        return pd.DataFrame(columns=columnas)

    try:
        participante = str(df.iat[2, 1]).strip()  # B3
    except Exception:
        participante = ""

    if not participante or participante.lower() in ["nan", "none"]:
        participante = str(nombre_hoja).strip()

    rows = []
    n_rows, n_cols = df.shape

    for r in range(n_rows):
        for c in range(n_cols):
            valor = df.iat[r, c]

            if pd.isna(valor):
                continue

            texto = str(valor).strip().upper()
            match = re.search(r"PARTIDO\s*([0-9]+)", texto)

            if not match:
                continue

            partido_id = int(match.group(1))

            # c = PARTIDO X
            # c+1 = local
            # c+2 = goles local
            # c+3 = visitante
            # c+4 = goles visitante
            if c + 4 >= n_cols:
                continue

            local = limpiar_nombre_equipo(df.iat[r, c + 1])
            gl = pd.to_numeric(df.iat[r, c + 2], errors="coerce")
            visitante = limpiar_nombre_equipo(df.iat[r, c + 3])
            gv = pd.to_numeric(df.iat[r, c + 4], errors="coerce")

            if not local or not visitante:
                continue

            if pd.isna(gl) or pd.isna(gv):
                continue

            rows.append({
                "participante": participante,
                "partido_id": partido_id,
                "goles_local": int(gl),
                "goles_visitante": int(gv),
            })

    out = pd.DataFrame(rows, columns=columnas)

    if not out.empty:
        out = (
            out
            .drop_duplicates(subset=["participante", "partido_id"], keep="first")
            .sort_values(["participante", "partido_id"])
            .reset_index(drop=True)
        )

    return out



@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def cargar_apuestas_desde_google_multipestana(partidos: pd.DataFrame) -> pd.DataFrame:
    """Carga apuestas desde Google Sheets multipestaña.

    Estructura:
        RESULTADOS
        hoja participante 1
        hoja participante 2
        ...

    El nombre del participante está en B3.
    """
    sheet_id = obtener_google_sheet_id()
    if not sheet_id:
        return pd.DataFrame(columns=["participante", "partido_id", "goles_local", "goles_visitante"])

    xls = leer_excel_google_sheet(sheet_id)

    hojas_excluidas = {
        "RESULTADOS", "CLASIFICACION", "CLASIFICACIÓN", "RESUMEN",
        "INSTRUCCIONES", "PARTIDOS", "CONFIG", "CONFIGURACION", "CONFIGURACIÓN"
    }

    apuestas = []
    for sheet_name in xls.sheet_names:
        if sheet_name.strip().upper() in hojas_excluidas:
            continue

        try:
            df_sheet = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            parsed = extraer_apuestas_de_hoja_excel(df_sheet, sheet_name, partidos)
            if not parsed.empty:
                apuestas.append(parsed)
        except Exception as e:
            st.warning(f"No pude leer la hoja '{sheet_name}'. Detalle: {e}")

    if not apuestas:
        return pd.DataFrame(columns=["participante", "partido_id", "goles_local", "goles_visitante"])

    return pd.concat(apuestas, ignore_index=True)


@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def cargar_resultados_desde_google_resultados() -> pd.DataFrame:
    """Carga resultados desde la pestaña RESULTADOS."""
    sheet_id = obtener_google_sheet_id()
    if not sheet_id:
        return pd.DataFrame(columns=["partido_id", "goles_local", "goles_visitante"])

    xls = leer_excel_google_sheet(sheet_id)

    resultado_sheet = None
    for sheet_name in xls.sheet_names:
        if sheet_name.strip().upper() == "RESULTADOS":
            resultado_sheet = sheet_name
            break

    if resultado_sheet is None:
        raise ValueError("No existe una pestaña llamada RESULTADOS.")

    df = pd.read_excel(xls, sheet_name=resultado_sheet)
    return normalizar_resultados(df)




def obtener_google_sheet_id() -> str:
    """Lee el ID de Google Sheet desde secrets.

    Recomendado:
      GOOGLE_SHEET_ID = "xxxxx"

    Compatibilidad:
      APUESTAS_SHEET_URL, RESULTADOS_SHEET_URL o GOOGLE_SHEET_URL.
    """
    sheet_id = leer_secret("GOOGLE_SHEET_ID")
    if sheet_id:
        return sheet_id

    for key in ["APUESTAS_SHEET_URL", "RESULTADOS_SHEET_URL", "GOOGLE_SHEET_URL"]:
        valor = leer_secret(key)
        if valor:
            m = re.search(r"/d/([a-zA-Z0-9-_]+)", valor)
            return m.group(1) if m else valor

    return ""


@st.cache_data(ttl=300, show_spinner=False)
def obtener_gid_por_nombre_pestana(sheet_id: str, nombre_pestana: str) -> str:
    """Obtiene el gid de la pestaña por su nombre visible."""
    if not sheet_id:
        return ""

    metadata_url = f"https://spreadsheets.google.com/feeds/worksheets/{sheet_id}/public/basic?alt=json"
    response = requests.get(metadata_url, timeout=20)
    response.raise_for_status()
    data = response.json()

    for entry in data.get("feed", {}).get("entry", []):
        title = entry.get("title", {}).get("$t", "").strip()
        if title.lower() == nombre_pestana.strip().lower():
            for link in entry.get("link", []):
                href = link.get("href", "")
                match = re.search(r"gid=([0-9]+)", href)
                if match:
                    return match.group(1)

    raise ValueError(f"No encuentro la pestaña '{nombre_pestana}' en la Google Sheet.")


def construir_csv_url_por_pestana(nombre_pestana: str) -> str:
    """Construye URL CSV usando GOOGLE_SHEET_ID y una pestaña llamada APUESTAS o RESULTADOS."""
    sheet_id = obtener_google_sheet_id()
    if not sheet_id:
        return ""

    gid = obtener_gid_por_nombre_pestana(sheet_id, nombre_pestana)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(ttl=300, show_spinner=False)
def leer_csv_externo(csv_url: str) -> pd.DataFrame:
    return pd.read_csv(csv_url)


def normalizar_apuestas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["participante", "partido_id", "goles_local", "goles_visitante"])
    cols = {c.strip().lower(): c for c in df.columns}
    aliases = {
        "participante": ["participante", "jugador", "nombre", "usuario"],
        "partido_id": ["partido_id", "id_partido", "partido", "match_id"],
        "goles_local": ["goles_local", "local_goles", "gl", "pronostico_local", "apuesta_local"],
        "goles_visitante": ["goles_visitante", "visitante_goles", "gv", "pronostico_visitante", "apuesta_visitante"],
    }
    ren = {}
    for target, posibles in aliases.items():
        for p in posibles:
            if p in cols:
                ren[cols[p]] = target
                break
    out = df.rename(columns=ren)
    required = ["participante", "partido_id", "goles_local", "goles_visitante"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        st.warning(f"La hoja APUESTAS no tiene las columnas esperadas: {', '.join(missing)}")
        return pd.DataFrame(columns=required)
    out = out[required].copy()
    out["participante"] = out["participante"].astype(str).str.strip()
    for c in ["partido_id", "goles_local", "goles_visitante"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["participante", "partido_id", "goles_local", "goles_visitante"])
    out["partido_id"] = out["partido_id"].astype(int)
    out["goles_local"] = out["goles_local"].astype(int)
    out["goles_visitante"] = out["goles_visitante"].astype(int)
    return out


def normalizar_resultados(df: pd.DataFrame) -> pd.DataFrame:
    required = ["partido_id", "goles_local", "goles_visitante"]
    if df.empty:
        return pd.DataFrame(columns=required)
    cols = {c.strip().lower(): c for c in df.columns}
    aliases = {
        "partido_id": ["partido_id", "id_partido", "partido", "match_id"],
        "goles_local": ["goles_local", "local_goles", "gl", "resultado_local"],
        "goles_visitante": ["goles_visitante", "visitante_goles", "gv", "resultado_visitante"],
    }
    ren = {}
    for target, posibles in aliases.items():
        for p in posibles:
            if p in cols:
                ren[cols[p]] = target
                break
    out = df.rename(columns=ren)
    missing = [c for c in required if c not in out.columns]
    if missing:
        st.warning(f"La hoja RESULTADOS no tiene las columnas esperadas: {', '.join(missing)}")
        return pd.DataFrame(columns=required)
    out = out[required].copy()
    for c in required:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["partido_id"])
    out["partido_id"] = out["partido_id"].astype(int)
    return out


def cargar_apuestas_desde_fuente(partidos: pd.DataFrame | None = None) -> pd.DataFrame:
    """Carga apuestas desde Google Sheets multipestaña o CSV local.

    Si GOOGLE_SHEET_ID está configurado, no se permite volver silenciosamente
    a CSV local, para evitar mostrar participantes antiguos.
    """
    if partidos is None:
        partidos = cargar_partidos()

    sheet_id = obtener_google_sheet_id()

    if sheet_id:
        try:
            apuestas_google = cargar_apuestas_desde_google_multipestana(partidos)
        except Exception as e:
            st.error(
                "No pude leer las apuestas desde la Google Sheet configurada. "
                "No usaré la copia local para evitar mostrar participantes antiguos."
            )
            st.exception(e)
            st.stop()

        if apuestas_google.empty:
            st.error(
                "La Google Sheet configurada se ha leído, pero no he encontrado apuestas válidas. "
                "Revisa que haya una hoja por participante, nombre en B3 y bloques "
                "FECHA | PARTIDO X | LOCAL | GOLES LOCAL | VISITANTE | GOLES VISITANTE."
            )
            st.stop()

        return apuestas_google

    for filename in ["apuestas.csv", "apuestas_reales.csv"]:
        apuestas_csv = DATA_DIR / filename
        if apuestas_csv.exists():
            return normalizar_apuestas(pd.read_csv(apuestas_csv))

    return pd.DataFrame(
        columns=["participante", "partido_id", "goles_local", "goles_visitante"]
    )



def cargar_resultados_desde_fuente(partidos: pd.DataFrame) -> pd.DataFrame:
    """Carga resultados desde Google Sheets o CSV local.

    Si GOOGLE_SHEET_ID está configurado, no se usa CSV local si falla Google.
    """
    base = partidos[["partido_id"]].copy()
    base["goles_local"] = pd.NA
    base["goles_visitante"] = pd.NA

    loaded = pd.DataFrame(columns=["partido_id", "goles_local", "goles_visitante"])

    sheet_id = obtener_google_sheet_id()

    if sheet_id:
        try:
            loaded = cargar_resultados_desde_google_resultados()
        except Exception as e:
            st.error(
                "No pude leer la pestaña RESULTADOS desde la Google Sheet configurada. "
                "No usaré la copia local para evitar resultados antiguos."
            )
            st.exception(e)
            st.stop()

        if loaded.empty:
            st.warning(
                "La pestaña RESULTADOS existe, pero no tiene resultados válidos todavía."
            )

    else:
        resultados_csv = DATA_DIR / "resultados.csv"
        if resultados_csv.exists():
            loaded = normalizar_resultados(pd.read_csv(resultados_csv))

    if not loaded.empty:
        base = base.drop(columns=["goles_local", "goles_visitante"]).merge(loaded, on="partido_id", how="left")

    return base



def logo_base64() -> str:
    p = ASSETS_DIR / "logo_ludopatas.png"
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode("utf-8")


@st.cache_data(show_spinner=False)
def imagen_asset_base64(nombre_archivo: str) -> str:
    p = ASSETS_DIR / nombre_archivo
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode("utf-8")

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



@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def generar_excel_apuestas_transparencia(apuestas: pd.DataFrame, partidos: pd.DataFrame) -> bytes:
    """Genera un Excel amigable con todas las apuestas para transparencia."""
    output = BytesIO()

    if apuestas.empty:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame({"mensaje": ["No hay apuestas cargadas."]}).to_excel(writer, index=False, sheet_name="Sin apuestas")
        return output.getvalue()

    detalle_apuestas = apuestas.merge(
        partidos[["partido_id", "grupo", "fecha", "local", "visitante"]],
        on="partido_id",
        how="left"
    ).copy()

    detalle_apuestas["partido"] = detalle_apuestas["local"].astype(str) + " vs " + detalle_apuestas["visitante"].astype(str)
    detalle_apuestas["apuesta"] = detalle_apuestas["goles_local"].astype(str) + " - " + detalle_apuestas["goles_visitante"].astype(str)

    detalle_apuestas = detalle_apuestas[
        ["participante", "partido_id", "grupo", "fecha", "partido", "local", "visitante", "goles_local", "goles_visitante", "apuesta"]
    ].sort_values(["participante", "partido_id"])

    resumen = (
        detalle_apuestas
        .groupby("participante", as_index=False)
        .agg(
            apuestas_registradas=("partido_id", "count"),
            primer_partido=("partido_id", "min"),
            ultimo_partido=("partido_id", "max"),
        )
        .sort_values("participante")
    )

    # Formato ancho: una fila por participante y una columna por partido.
    matriz = detalle_apuestas.pivot_table(
        index="participante",
        columns="partido_id",
        values="apuesta",
        aggfunc="first"
    ).reset_index()

    matriz.columns = [
        "participante" if c == "participante" else f"Partido {int(c)}"
        for c in matriz.columns
    ]

    calendario = partidos[["partido_id", "grupo", "fecha", "local", "visitante"]].copy()
    calendario["partido"] = calendario["local"].astype(str) + " vs " + calendario["visitante"].astype(str)
    calendario = calendario[["partido_id", "grupo", "fecha", "partido", "local", "visitante"]].sort_values("partido_id")

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        resumen.to_excel(writer, index=False, sheet_name="Resumen")
        detalle_apuestas.to_excel(writer, index=False, sheet_name="Detalle apuestas")
        matriz.to_excel(writer, index=False, sheet_name="Vista participantes")
        calendario.to_excel(writer, index=False, sheet_name="Calendario")

        # Formato visual básico
        for sheet_name in writer.book.sheetnames:
            ws = writer.book[sheet_name]
            ws.freeze_panes = "A2"

            for cell in ws[1]:
                cell.font = cell.font.copy(bold=True)
                cell.alignment = cell.alignment.copy(horizontal="center")

            for column_cells in ws.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter
                for cell in column_cells:
                    try:
                        max_length = max(max_length, len(str(cell.value)) if cell.value is not None else 0)
                    except Exception:
                        pass
                ws.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 38)

    return output.getvalue()


def html_kpis(participantes: int, jugados: int, partidos_total: int, lider: str, lider_pts: int, maximo_posible: int):
    c1, c2, c3, c4 = st.columns(4)
    partidos_pendientes = max(partidos_total - jugados, 0)
    items = [
        ("Participantes", participantes, "La grada de la porra"),
        ("Partidos jugados", f"{jugados}/{partidos_total}", "Se recalcula al instante"),
        ("Líder actual", lider, f"{lider_pts} puntos" if lider else "Sin líder todavía"),
        ("Máximo posible", maximo_posible, f"Líder + {partidos_pendientes * 3} pts pendientes"),
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
    jugados = set(
        resultados_df.dropna(subset=["goles_local", "goles_visitante"])["partido_id"].astype(int)
    )
    pendientes = partidos[~partidos["partido_id"].astype(int).isin(jugados)].head(3)

    if pendientes.empty:
        st.success("Todos los partidos están cerrados. ¡A revisar el campeón de la porra!")
        return

    html = ""
    for _, p in pendientes.iterrows():
        local = str(p["local"])
        visitante = str(p["visitante"])
        html += (
            "<div class='match-card'>"
            f"<div class='small-muted'>{p['fecha']} · {p['grupo']} · Partido {int(p['partido_id'])}</div>"
            "<div class='team-line'>"
            f"{bandera_html(local)} {local} "
            "<span style='color:#FFD166'>vs</span> "
            f"{bandera_html(visitante)} {visitante}"
            "</div>"
            "</div>"
        )

    st.markdown(html, unsafe_allow_html=True)




def bloque_comunidad(apuestas: pd.DataFrame, partidos: pd.DataFrame):
    """Muestra el pulso de la comunidad para un partido seleccionable."""
    if apuestas.empty:
        st.info("Aún no hay apuestas para leer el pulso de la comunidad.")
        return

    resumen = resumen_partido(
        apuestas,
        pd.DataFrame(columns=["partido_id", "goles_local", "goles_visitante"]),
        partidos
    )

    if resumen.empty:
        return

    resumen = resumen.copy()

    # Añadimos local/visitante para poder mostrar banderas como imágenes.
    equipos = partidos[["partido_id", "local", "visitante"]].copy()
    resumen = resumen.merge(equipos, on="partido_id", how="left")

    resumen["selector"] = resumen["partido_id"].astype(str) + " · " + resumen["local"] + " vs " + resumen["visitante"]

    idx_default = int(resumen["total"].idxmax()) if "total" in resumen.columns else 0
    opciones = resumen["selector"].tolist()
    default_label = resumen.loc[idx_default, "selector"] if idx_default in resumen.index else opciones[0]
    default_index = opciones.index(default_label) if default_label in opciones else 0

    partido_sel = st.selectbox(
        "Elige partido para ver cómo apostó la comunidad",
        opciones,
        index=default_index,
        key="selector_comunidad_partido"
    )

    partido = resumen[resumen["selector"] == partido_sel].iloc[0]

    local = str(partido["local"])
    visitante = str(partido["visitante"])

    vals = pd.DataFrame({
        "signo": [f"Gana {local}", "Empate", f"Gana {visitante}"],
        "porcentaje": [partido["1%"], partido["X%"], partido["2%"]]
    })

    st.markdown(
        f"<div class='card'><div class='stat-label'>Pulso de la comunidad</div>"
        f"<div class='team-line'>{partido_html(local, visitante)}</div>"
        f"<div class='small-muted'>{int(partido['total'])} apuestas registradas para este partido.</div></div>",
        unsafe_allow_html=True
    )

    fig = px.bar(vals, x="signo", y="porcentaje", text="porcentaje", range_y=[0, 100])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=270,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "staticPlot": True,
            "responsive": True,
        }
    )



def prediccion_clasificados_por_grupo(apuestas: pd.DataFrame, partidos: pd.DataFrame, resultados: pd.DataFrame | None = None) -> pd.DataFrame:
    """Calcula previsión de clasificados y situación real por grupo.

    - Antes de que haya resultados: ordena por predicción de la comunidad.
    - Cuando haya resultados en un grupo: ordena por puntos reales.
    - Mantiene siempre la predicción de la comunidad como contexto.
    """
    columnas = ["grupo", "equipo", "pts_reales", "pj_reales", "puntos_medios", "top2_pct", "prediccion_pos"]

    if apuestas.empty or partidos.empty:
        return pd.DataFrame(columns=columnas)

    partidos_base = canonizar_partidos_df(partidos[["partido_id", "grupo", "local", "visitante"]])

    base = apuestas.merge(partidos_base, on="partido_id", how="inner")

    if base.empty:
        return pd.DataFrame(columns=columnas)

    registros = []

    for participante, df_part in base.groupby("participante"):
        for grupo, df_grupo in df_part.groupby("grupo"):
            puntos = {}

            equipos = sorted(
                set(df_grupo["local"].dropna().astype(str)).union(
                    set(df_grupo["visitante"].dropna().astype(str))
                )
            )

            for equipo in equipos:
                puntos[equipo] = 0

            for _, r in df_grupo.iterrows():
                local = str(r["local"])
                visitante = str(r["visitante"])
                gl = int(r["goles_local"])
                gv = int(r["goles_visitante"])

                if gl > gv:
                    puntos[local] = puntos.get(local, 0) + 3
                    puntos[visitante] = puntos.get(visitante, 0) + 0
                elif gl < gv:
                    puntos[local] = puntos.get(local, 0) + 0
                    puntos[visitante] = puntos.get(visitante, 0) + 3
                else:
                    puntos[local] = puntos.get(local, 0) + 1
                    puntos[visitante] = puntos.get(visitante, 0) + 1

            ranking = sorted(puntos.items(), key=lambda x: (-x[1], x[0]))

            for pos, (equipo, pts) in enumerate(ranking, start=1):
                registros.append({
                    "participante": participante,
                    "grupo": grupo,
                    "equipo": equipo,
                    "puntos_previstos": pts,
                    "top2": 1 if pos <= 2 else 0,
                })

    pred = pd.DataFrame(registros)

    if pred.empty:
        return pd.DataFrame(columns=columnas)

    resumen = (
        pred
        .groupby(["grupo", "equipo"], as_index=False)
        .agg(
            puntos_medios=("puntos_previstos", "mean"),
            top2_pct=("top2", "mean"),
        )
    )

    resumen["top2_pct"] = resumen["top2_pct"] * 100

    reales_rows = []

    if resultados is not None and not resultados.empty:
        partidos_resultados = partidos_base.merge(resultados, on="partido_id", how="left")

        for _, r in partidos_resultados.dropna(subset=["goles_local", "goles_visitante"]).iterrows():
            grupo = r["grupo"]
            local = str(r["local"])
            visitante = str(r["visitante"])
            gl = int(r["goles_local"])
            gv = int(r["goles_visitante"])

            if gl > gv:
                reales_rows.append({"grupo": grupo, "equipo": local, "pts": 3, "pj": 1})
                reales_rows.append({"grupo": grupo, "equipo": visitante, "pts": 0, "pj": 1})
            elif gl < gv:
                reales_rows.append({"grupo": grupo, "equipo": local, "pts": 0, "pj": 1})
                reales_rows.append({"grupo": grupo, "equipo": visitante, "pts": 3, "pj": 1})
            else:
                reales_rows.append({"grupo": grupo, "equipo": local, "pts": 1, "pj": 1})
                reales_rows.append({"grupo": grupo, "equipo": visitante, "pts": 1, "pj": 1})

    if reales_rows:
        reales = (
            pd.DataFrame(reales_rows)
            .groupby(["grupo", "equipo"], as_index=False)
            .agg(
                pts_reales=("pts", "sum"),
                pj_reales=("pj", "sum"),
            )
        )
        resumen = resumen.merge(reales, on=["grupo", "equipo"], how="left")
    else:
        resumen["pts_reales"] = 0
        resumen["pj_reales"] = 0

    resumen["pts_reales"] = resumen["pts_reales"].fillna(0).astype(int)
    resumen["pj_reales"] = resumen["pj_reales"].fillna(0).astype(int)

    # Si el grupo tiene algún partido jugado, ordena por puntos reales.
    resumen["_hay_reales_grupo"] = resumen.groupby("grupo")["pj_reales"].transform("sum") > 0

    resumen = resumen.sort_values(
        ["grupo", "_hay_reales_grupo", "pts_reales", "top2_pct", "puntos_medios", "equipo"],
        ascending=[True, False, False, False, False, True],
    )

    resumen["prediccion_pos"] = resumen.groupby("grupo").cumcount() + 1
    resumen = resumen.drop(columns=["_hay_reales_grupo"])

    return resumen[columnas]



def render_prediccion_grupos(pred: pd.DataFrame):
    """Renderiza predicción + puntos reales de grupos."""
    if pred.empty:
        st.info("Aún no hay apuestas suficientes para calcular la previsión de grupos.")
        return

    grupos = list(pred["grupo"].dropna().unique())

    for grupo in grupos:
        df_g = pred[pred["grupo"] == grupo].copy().sort_values("prediccion_pos")
        hay_reales = int(df_g["pj_reales"].sum()) > 0 if "pj_reales" in df_g.columns else False

        filas = ""
        for _, r in df_g.iterrows():
            equipo = str(r["equipo"])
            pos = int(r["prediccion_pos"])
            top2 = float(r["top2_pct"])
            pts_prev = float(r["puntos_medios"])
            pts_real = int(r.get("pts_reales", 0))
            pj_real = int(r.get("pj_reales", 0))
            clase = "clasificado" if pos <= 2 else ""

            filas += (
                f"<tr class='{clase}'>"
                f"<td>{pos}</td>"
                f"<td>{bandera_html(equipo)} {equipo}</td>"
                f"<td>{pts_real}</td>"
                f"<td>{pj_real}</td>"
                f"<td>{top2:.1f}%</td>"
                f"<td>{pts_prev:.2f}</td>"
                f"</tr>"
            )

        subtitulo = "Ordenado por puntos reales" if hay_reales else "Ordenado por predicción de la comunidad"

        st.markdown(
            f"""
            <div class="prediction-card">
              <div class="prediction-title">Grupo {grupo}</div>
              <div class="small-muted" style="margin-bottom:10px;">{subtitulo}</div>
              <table class="prediction-table">
                <thead>
                  <tr>
                    <th>Pos.</th>
                    <th>Equipo</th>
                    <th>Pts reales</th>
                    <th>PJ</th>
                    <th>Top 2 comunidad</th>
                    <th>Pts medios comunidad</th>
                  </tr>
                </thead>
                <tbody>
                  {filas}
                </tbody>
              </table>
            </div>
            """,
            unsafe_allow_html=True
        )


@st.cache_data(ttl=300, show_spinner=False, max_entries=2)
def calcular_datos_panel(
    apuestas: pd.DataFrame,
    resultados: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calcula una sola vez los datos comunes para todas las sesiones."""
    detalle_calculado = calcular_puntos(apuestas, resultados)
    tabla_calculada = clasificacion(detalle_calculado)
    stats_calculadas = estadisticas_participantes(detalle_calculado)
    return detalle_calculado, tabla_calculada, stats_calculadas


partidos = cargar_partidos()

# -----------------------------
# Carga de datos: Google Sheets / CSV local / demo
# -----------------------------
# La web es pública y limpia. Los datos se gestionan fuera: Google Sheets para apuestas/resultados
# y, más adelante, SportMonks para resultados automáticos. Streamlit solo lee y calcula.

apuestas_df = cargar_apuestas_desde_fuente(partidos)
resultados_df = cargar_resultados_desde_fuente(partidos)

demo_mode = apuestas_df.empty
if demo_mode:
    apuestas_df = demo_apuestas(partidos)
    demo_res = partidos.head(10)[["partido_id"]].copy()
    rnd = random.Random(101)
    demo_res["goles_local"] = [rnd.choice([0,1,1,2,2,3]) for _ in range(len(demo_res))]
    demo_res["goles_visitante"] = [rnd.choice([0,0,1,1,2]) for _ in range(len(demo_res))]
    resultados_df = partidos[["partido_id"]].merge(demo_res, on="partido_id", how="left")

# -----------------------------
# Cálculo
# -----------------------------
detalle, tabla, stats = calcular_datos_panel(apuestas_df, resultados_df)
partidos_jugados = resultados_df.dropna(subset=["goles_local", "goles_visitante"]).shape[0]
lider = tabla.iloc[0]["participante"] if not tabla.empty else ""
lider_pts = int(tabla.iloc[0]["puntos"]) if not tabla.empty else 0
puntos_pendientes = max(len(partidos) - partidos_jugados, 0) * 3
maximo_posible = lider_pts + puntos_pendientes

# -----------------------------
# Portada
# -----------------------------
worldcup_b64 = imagen_asset_base64("worldcup_2026_clean.png")

participantes_total = apuestas_df["participante"].nunique() if not apuestas_df.empty else 0
partidos_pendientes = max(len(partidos) - partidos_jugados, 0)

hero_html = (
    f'<div class="hero hero-pro">'
    f'<div class="hero-inner-pro">'
    f'<div class="hero-main-pro">'
    f'<div class="kicker">Canadá · México · USA 2026</div>'
    f'<div class="hero-title-pro">'
    f'<span class="line1">PORRA</span> '
    f'<span class="line2"><span class="gold">LUDÓPATAS</span>'
    f'<span class="year">2026</span></span>'
    f'</div>'
    f'<div class="hero-sub-pro">La gran porra del Mundial 2026. Compite, apuesta y demuestra que sabes de fútbol.</div>'
    f'<div class="hero-badges-pro">'
    f'<div class="badge">🌎 48 selecciones</div>'
    f'<div class="badge">🏆 12 grupos</div>'
    f'<div class="badge">📅 11 junio – 28 junio</div>'
    f'<div class="badge">⚡ 72 partidos</div>'
    f'</div>'
    f'</div>'
    f'<div class="hero-trophy-zone">'
    f'<div class="participants-burst floating-stat stat-participantes"><span class="num">{participantes_total}</span><span class="txt">participantes</span></div>'
    f'<div class="floating-stat stat-jugados"><span class="num">{partidos_jugados}/{len(partidos)}</span><span class="txt">jugados</span><span class="note">al instante</span></div>'
    f'<div class="floating-stat stat-lider"><span class="num">{lider if lider else "—"}</span><span class="txt">líder actual</span><span class="note">{lider_pts} puntos</span></div>'
    f'<div class="floating-stat stat-maximo"><span class="num">{maximo_posible}</span><span class="txt">máximo posible</span><span class="note">+{partidos_pendientes * 3} pendientes</span></div>'
    f'<img class="hero-trophy-pro" src="data:image/png;base64,{worldcup_b64}" alt="Copa Porra Ludópatas 2026">'
    f'</div>'
    f'</div>'
    f'</div>'
)

st.markdown(hero_html, unsafe_allow_html=True)

st.write("")
left, right = st.columns([1.7, 1])
with left:
    st.subheader("🏆 Podio en directo")
    podium(tabla)
with right:
    st.subheader("⏭️ Próximos partidos")
    proximo_partido(partidos, resultados_df)

st.write("")
st.markdown("### 🔥 La jornada")
if not detalle.empty and partidos_jugados > 0:
    jornada = detalle.dropna(subset=["real_local", "real_visitante"]).groupby("participante", as_index=False).agg(puntos=("puntos", "sum"), plenos=("puntos", lambda s: int((s == 3).sum())))
    if not jornada.empty:
        best = jornada.sort_values(["puntos", "plenos"], ascending=False).iloc[0]
        worst = jornada.sort_values(["puntos", "plenos"], ascending=True).iloc[0]
        st.markdown(f"<div class='big-cta'><span class='ribbon'>Mejor de la jornada</span><h2>{best['participante']} · +{int(best['puntos'])} pts</h2><p>Batacazo provisional: <strong>{worst['participante']}</strong> con {int(worst['puntos'])} puntos. Cada partido puede mover el ranking.</p></div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='big-cta'><span class='ribbon'>Calienta motores</span><h2>La jornada explotará cuando metas el primer resultado</h2><p>La app detectará líderes, batacazos y plenos automáticamente.</p></div>", unsafe_allow_html=True)


# -----------------------------
# Navegacion bajo demanda
# -----------------------------
st.write("")
seccion = st.radio(
    "Sección",
    [
        "🔥 Clasificación",
        "⚽ Resultados",
        "🧠 Comunidad",
        "🔮 Predicción",
        "👀 Apuestas",
        "📊 Estadísticas",
        "📣 Cómo participar",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="navegacion_principal",
)

if seccion == "🔥 Clasificación":
    st.markdown("### Clasificación general")
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
                "puntos": st.column_config.NumberColumn("Puntos", format="%d pts"),
            },
        )
        st.download_button("Descargar clasificación CSV", tabla.to_csv(index=False).encode("utf-8"), "clasificacion_porra_2026.csv", "text/csv")

elif seccion == "🧠 Comunidad":
    st.markdown("### 🧠 La comunidad opina")
    bloque_comunidad(apuestas_df, partidos)

elif seccion == "🔮 Predicción":
    st.markdown("## 🔮 La comunidad predice")
    st.caption("Predicción de clasificados por grupo según la tendencia global de las apuestas de la porra.")
    pred_grupos = prediccion_clasificados_por_grupo(apuestas_df, partidos, resultados_df)
    render_prediccion_grupos(pred_grupos)

elif seccion == "⚽ Resultados":
    st.markdown("### Calendario de la fase de grupos")
    partidos_resultados = partidos[["partido_id", "grupo", "fecha", "local", "visitante"]].merge(
        resultados_df, on="partido_id", how="left"
    )

    def resultado_texto(r):
        if pd.isna(r["goles_local"]) or pd.isna(r["goles_visitante"]):
            return "Pendiente"
        return f"{int(r['goles_local'])}-{int(r['goles_visitante'])}"

    rows_html = ""
    for _, r in partidos_resultados.iterrows():
        rows_html += (
            "<tr>"
            f"<td>{int(r['partido_id'])}</td>"
            f"<td>{r['grupo']}</td>"
            f"<td>{r['fecha']}</td>"
            f"<td>{partido_html(str(r['local']), str(r['visitante']))}</td>"
            f"<td><strong>{resultado_texto(r)}</strong></td>"
            "</tr>"
        )

    st.markdown(
        f"""
        <div class="table-card">
          <table class="pretty-table">
            <thead>
              <tr>
                <th>Partido</th>
                <th>Grupo</th>
                <th>Fecha</th>
                <th>Encuentro</th>
                <th>Resultado</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


elif seccion == "👀 Apuestas":
    st.markdown("### Apuestas de los participantes")
    if apuestas_df.empty:
        st.info("Sube uno o varios Excel para ver las apuestas.")
    else:
        if st.button(
            "📦 Preparar todas las apuestas en Excel",
            key="preparar_apuestas_tab",
            help="El Excel solo se genera cuando alguien lo solicita.",
        ):
            with st.spinner("Preparando el Excel de apuestas..."):
                st.session_state["excel_apuestas_completo"] = generar_excel_apuestas_transparencia(
                    apuestas_df,
                    partidos,
                )

        if "excel_apuestas_completo" in st.session_state:
            st.download_button(
                "📥 Descargar todas las apuestas en Excel",
                data=st.session_state["excel_apuestas_completo"],
                file_name="apuestas_porra_ludopatas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga todas las apuestas para comprobar la transparencia de la porra.",
            )

        st.caption("El Excel incluye resumen, detalle completo, vista por participante y calendario.")

        vista = apuestas_df.merge(
            partidos[["partido_id", "grupo", "local_flag", "local", "visitante_flag", "visitante"]],
            on="partido_id",
            how="left"
        )

        vista["partido"] = vista.apply(
            lambda r: partido_texto_con_banderas(str(r["local"]), str(r["visitante"])),
            axis=1
        )
        vista["partido_selector"] = (
            vista["partido_id"].astype(str)
            + " · "
            + vista["local"].astype(str)
            + " vs "
            + vista["visitante"].astype(str)
        )
        vista["apuesta"] = vista["goles_local"].astype(str) + " - " + vista["goles_visitante"].astype(str)

        st.markdown("#### 🔎 Filtros de consulta")

        f1, f2, f3 = st.columns([1.1, 1, 1.6])
        with f1:
            participante_sel = st.selectbox(
                "Participante",
                ["Todos"] + sorted(vista["participante"].dropna().unique().tolist()),
                key="filtro_apuestas_participante"
            )
        with f2:
            grupo_sel = st.selectbox(
                "Grupo",
                ["Todos"] + sorted(vista["grupo"].dropna().unique().tolist()),
                key="filtro_apuestas_grupo"
            )
        with f3:
            partidos_opciones = ["Todos"] + (
                vista[["partido_id", "partido_selector"]]
                .drop_duplicates()
                .sort_values("partido_id")["partido_selector"]
                .tolist()
            )
            partido_sel = st.selectbox(
                "Partido",
                partidos_opciones,
                key="filtro_apuestas_partido"
            )

        f4, f5, f6 = st.columns([1, 1, 1])
        with f4:
            signo_sel = st.selectbox(
                "Signo apostado",
                ["Todos", "Gana local", "Empate", "Gana visitante"],
                key="filtro_apuestas_signo"
            )
        with f5:
            marcador_busqueda = st.text_input(
                "Marcador exacto",
                placeholder="Ej: 2-1",
                key="filtro_apuestas_marcador"
            )
        with f6:
            ordenar_por = st.selectbox(
                "Ordenar por",
                ["participante", "partido_id", "grupo", "apuesta"],
                key="filtro_apuestas_orden"
            )

        filtrada = vista.copy()

        if participante_sel != "Todos":
            filtrada = filtrada[filtrada["participante"] == participante_sel]

        if grupo_sel != "Todos":
            filtrada = filtrada[filtrada["grupo"] == grupo_sel]

        if partido_sel != "Todos":
            partido_id_sel = int(str(partido_sel).split(" · ")[0])
            filtrada = filtrada[filtrada["partido_id"] == partido_id_sel]

        if signo_sel != "Todos":
            if signo_sel == "Gana local":
                filtrada = filtrada[filtrada["goles_local"] > filtrada["goles_visitante"]]
            elif signo_sel == "Empate":
                filtrada = filtrada[filtrada["goles_local"] == filtrada["goles_visitante"]]
            elif signo_sel == "Gana visitante":
                filtrada = filtrada[filtrada["goles_local"] < filtrada["goles_visitante"]]

        marcador_limpio = marcador_busqueda.strip().replace(" ", "")
        if marcador_limpio:
            match = re.match(r"^(\d+)-(\d+)$", marcador_limpio)
            if match:
                gl_b, gv_b = int(match.group(1)), int(match.group(2))
                filtrada = filtrada[
                    (filtrada["goles_local"] == gl_b)
                    & (filtrada["goles_visitante"] == gv_b)
                ]
            else:
                st.warning("Formato de marcador no válido. Usa por ejemplo: 2-1")

        st.markdown(
            f"<div class='card'><div class='stat-label'>Apuestas encontradas</div>"
            f"<div class='stat-value'>{len(filtrada)}</div>"
            f"<div class='stat-note'>de {len(vista)} apuestas totales</div></div>",
            unsafe_allow_html=True
        )

        columnas_vista = ["participante", "partido_id", "grupo", "partido", "apuesta"]

        if filtrada.empty:
            st.info("No hay apuestas que coincidan con los filtros seleccionados.")
        else:
            filtrada_ordenada = filtrada[columnas_vista].sort_values(ordenar_por)
            filas_por_pagina = 200
            total_paginas = max(
                (len(filtrada_ordenada) + filas_por_pagina - 1) // filas_por_pagina,
                1,
            )
            pagina = st.selectbox(
                "Página de resultados",
                options=list(range(1, total_paginas + 1)),
                format_func=lambda p: f"Página {p} de {total_paginas}",
                key="pagina_apuestas",
            )
            inicio = (pagina - 1) * filas_por_pagina
            fin = inicio + filas_por_pagina

            st.caption(
                f"Mostrando filas {inicio + 1}-{min(fin, len(filtrada_ordenada))} "
                f"de {len(filtrada_ordenada)}."
            )
            st.dataframe(
                filtrada_ordenada.iloc[inicio:fin],
                hide_index=True,
                use_container_width=True
            )

            st.download_button(
                "📥 Descargar apuestas filtradas CSV",
                data=filtrada_ordenada.to_csv(index=False).encode("utf-8"),
                file_name="apuestas_filtradas.csv",
                mime="text/csv"
            )

elif seccion == "📊 Estadísticas":
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


elif seccion == "📣 Cómo participar":
    st.markdown(
        """
<div class='callout'>
<strong>Participa en la Porra Ludópatas 2026</strong><br>
Rellena el Excel, envíalo al organizador y sigue aquí la clasificación durante todo el Mundial.
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
**Rellena tu Excel y entra en la Porra Ludópatas 2026. Cada resultado actualizará la clasificación.**
""")

st.caption("Diseño inspirado en el ambiente del Mundial 2026. No usa logos oficiales ni material protegido de FIFA.")
