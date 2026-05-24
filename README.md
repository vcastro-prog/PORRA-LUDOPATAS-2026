# Porra Ludópatas Mundial 2026

App Streamlit pública para mostrar clasificación, apuestas, partidos y estadísticas de la Porra Ludópatas 2026.

## Cambio importante de esta versión

La app ya no tiene panel de administrador ni subida de archivos dentro de Streamlit. Los datos viven fuera de Streamlit para evitar pérdidas:

- **Apuestas**: Google Sheets.
- **Resultados**: Google Sheets ahora; SportMonks API más adelante.
- **Streamlit**: solo lee datos y recalcula la clasificación.

Así, aunque Streamlit Cloud reinicie la app o borre archivos temporales, los datos permanecen en Google Sheets.

## Imagen de cabecera

La imagen enviada por el usuario está incluida en:

```text
assets/logo_ludopatas.png
```

y se muestra en la esquina superior izquierda de la cabecera.

## Columnas esperadas en Google Sheets

### Hoja APUESTAS

Debe tener estas columnas:

```text
participante, partido_id, goles_local, goles_visitante
```

Ejemplo:

| participante | partido_id | goles_local | goles_visitante |
|---|---:|---:|---:|
| Vi | 1 | 2 | 1 |
| Vi | 2 | 0 | 0 |
| Marta | 1 | 1 | 1 |

### Hoja RESULTADOS

Debe tener estas columnas:

```text
partido_id, goles_local, goles_visitante
```

Ejemplo:

| partido_id | goles_local | goles_visitante |
|---:|---:|---:|
| 1 | 2 | 0 |
| 2 | 1 | 1 |

Los partidos pendientes pueden quedar vacíos.

## Configurar Google Sheets en Streamlit Cloud

En Streamlit Cloud:

```text
App > Settings > Secrets
```

Añade algo así:

```toml
APUESTAS_SHEET_URL = "https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0"
RESULTADOS_SHEET_URL = "https://docs.google.com/spreadsheets/d/XXXX/edit#gid=123456789"
```

También puedes usar un mismo archivo de Google Sheets con dos pestañas y poner el `gid` de cada pestaña.

## Importante sobre permisos

Esta versión lee Google Sheets como CSV. Para que funcione de forma simple, la hoja debe estar compartida como:

```text
Anyone with the link can view
```

Los participantes no necesitan recibir ese enlace. Solo ven la app Streamlit.

Más adelante se puede pasar a modo privado con Google Service Account si queréis máxima seguridad.

## Uso local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Sube estos archivos a GitHub.
2. Crea una app en Streamlit Cloud.
3. Main file path: `app.py`.
4. Añade los secretos de Google Sheets.
5. Deploy.

## Reglas de puntuación

- 1 punto por acertar el signo 1X2.
- Solo si se acierta el signo: +1 por acertar goles del local y +1 por acertar goles del visitante.
- Pleno exacto: 3 puntos.
- Si se falla el signo: 0 puntos.
