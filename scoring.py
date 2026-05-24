from __future__ import annotations

import pandas as pd


def signo(goles_local: int, goles_visitante: int) -> str:
    if goles_local > goles_visitante:
        return "1"
    if goles_local < goles_visitante:
        return "2"
    return "X"


def calcular_puntos(apuestas: pd.DataFrame, resultados: pd.DataFrame) -> pd.DataFrame:
    if apuestas.empty:
        return pd.DataFrame()
    resultados = resultados.dropna(subset=["goles_local", "goles_visitante"]).copy()
    if resultados.empty:
        out = apuestas.copy()
        out["puntos"] = 0
        out["acierta_1x2"] = False
        out["real_local"] = pd.NA
        out["real_visitante"] = pd.NA
        return out
    for col in ["goles_local", "goles_visitante"]:
        resultados[col] = resultados[col].astype(int)
    df = apuestas.merge(
        resultados.rename(columns={"goles_local": "real_local", "goles_visitante": "real_visitante"}),
        on="partido_id",
        how="left",
    )
    pendientes = df["real_local"].isna() | df["real_visitante"].isna()
    df["signo_apuesta"] = df.apply(lambda r: signo(int(r["goles_local"]), int(r["goles_visitante"])), axis=1)
    df["signo_real"] = df.apply(
        lambda r: signo(int(r["real_local"]), int(r["real_visitante"]))
        if not pd.isna(r["real_local"]) and not pd.isna(r["real_visitante"])
        else None,
        axis=1,
    )
    df["acierta_1x2"] = (~pendientes) & (df["signo_apuesta"] == df["signo_real"])
    df["puntos"] = 0
    df.loc[df["acierta_1x2"], "puntos"] = 1
    df.loc[df["acierta_1x2"] & (df["goles_local"] == df["real_local"]), "puntos"] += 1
    df.loc[df["acierta_1x2"] & (df["goles_visitante"] == df["real_visitante"]), "puntos"] += 1
    return df


def clasificacion(detalle: pd.DataFrame) -> pd.DataFrame:
    if detalle.empty:
        return pd.DataFrame(columns=["posición", "participante", "puntos", "plenos", "aciertos_1x2", "partidos_puntuados"])
    tabla = (
        detalle.groupby("participante", as_index=False)
        .agg(
            puntos=("puntos", "sum"),
            plenos=("puntos", lambda s: int((s == 3).sum())),
            aciertos_1x2=("acierta_1x2", "sum"),
            partidos_puntuados=("puntos", lambda s: int((s > 0).sum())),
        )
        .sort_values(["puntos", "plenos", "aciertos_1x2", "participante"], ascending=[False, False, False, True])
    )
    tabla.insert(0, "posición", range(1, len(tabla) + 1))
    return tabla


def estadisticas_participantes(detalle: pd.DataFrame) -> pd.DataFrame:
    if detalle.empty:
        return pd.DataFrame()
    jugados = detalle.dropna(subset=["real_local", "real_visitante"])
    if jugados.empty:
        return pd.DataFrame(columns=["participante", "media_puntos", "% 1X2", "plenos"])
    out = (
        jugados.groupby("participante", as_index=False)
        .agg(
            puntos=("puntos", "sum"),
            partidos=("partido_id", "count"),
            plenos=("puntos", lambda s: int((s == 3).sum())),
            aciertos_1x2=("acierta_1x2", "sum"),
        )
    )
    out["media_puntos"] = (out["puntos"] / out["partidos"]).round(2)
    out["% 1X2"] = (100 * out["aciertos_1x2"] / out["partidos"]).round(1)
    return out.sort_values(["media_puntos", "plenos", "puntos"], ascending=False)


def resumen_partido(apuestas: pd.DataFrame, resultados: pd.DataFrame, partidos: pd.DataFrame) -> pd.DataFrame:
    if apuestas.empty:
        return pd.DataFrame()
    tmp = apuestas.copy()
    tmp["signo"] = tmp.apply(lambda r: signo(int(r["goles_local"]), int(r["goles_visitante"])), axis=1)
    dist = tmp.groupby(["partido_id", "signo"], as_index=False).size()
    pivot = dist.pivot(index="partido_id", columns="signo", values="size").fillna(0).reset_index()
    for c in ["1", "X", "2"]:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot["total"] = pivot[["1", "X", "2"]].sum(axis=1)
    for c in ["1", "X", "2"]:
        pivot[f"{c}%"] = (100 * pivot[c] / pivot["total"]).round(1)
    out = partidos[["partido_id", "grupo", "local", "visitante"]].merge(pivot, on="partido_id", how="left").fillna(0)
    out["partido"] = out["local"] + " vs " + out["visitante"]
    return out[["partido_id", "grupo", "partido", "1%", "X%", "2%", "total"]].sort_values("total", ascending=False)
