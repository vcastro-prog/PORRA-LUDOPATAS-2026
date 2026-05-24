# Porra Ludópatas Mundial 2026

App Streamlit para convertir una porra de Excel en una experiencia tipo marcador deportivo: portada impactante, ranking en directo, podio, apuestas visibles, resultados editables y estadísticas.

## Datos oficiales usados como contexto visual

El Mundial 2026 se juega en Canadá, México y Estados Unidos, con 48 selecciones, 16 sedes, 104 partidos y fechas del 11 de junio al 19 de julio de 2026. La app evita logos oficiales y material protegido; usa estética inspirada en fútbol, banderas y datos generales del torneo.

## Reglas de puntuación

- 1 punto por acertar el signo 1X2.
- Solo si se acierta el signo: +1 por acertar goles del local y +1 por acertar goles del visitante.
- Pleno exacto: 3 puntos.
- Si se falla el signo: 0 puntos.

## Uso local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Crea un repo en GitHub, por ejemplo `porra-mundial-2026`.
2. Sube todos los archivos de esta carpeta.
3. En Streamlit Community Cloud, crea una app nueva desde ese repo.
4. Main file path: `app.py`.
5. Deploy.

## Flujo recomendado

1. Activa `Modo demo impactante` para enseñar la web y atraer participantes.
2. Cuando recibas Excel reales, súbelos en la barra lateral.
3. Mete resultados en la tabla editable o sube un CSV de resultados.
4. Descarga `resultados_porra_2026.csv` para conservar los marcadores entre sesiones.

## Estructura

- `app.py`: interfaz visual Streamlit.
- `excel_parser.py`: lee los Excel participantes.
- `scoring.py`: cálculo de puntos, clasificación y estadísticas.
- `data/partidos.csv`: partidos extraídos de la plantilla original.
- `data/resultados.csv`: plantilla de resultados.

La app lee el nombre del participante de `B3` y los goles en las celdas vacías después de cada equipo.


## Versión impactante incluida

Esta versión está pensada para captar participantes desde el primer día:

- Home tipo evento deportivo, con estética oscura, cards y llamadas a participar.
- Modo demo para enseñar la experiencia aunque todavía no haya Excel reales.
- Podio visual y ranking descargable.
- Bloque “La jornada” para destacar mejor jugador y batacazo.
- Bloque “La comunidad opina” para ver tendencias de apuestas por partido.
- Editor de resultados en la barra lateral.
- Diseño mobile-first para compartirlo por WhatsApp.

## Recomendación para el grupo

Primero publica la app con el modo demo activado para enseñar cómo se verá. Cuando empiecen a llegar Excels reales, desactiva el modo demo y sube los archivos de participantes desde la barra lateral.
