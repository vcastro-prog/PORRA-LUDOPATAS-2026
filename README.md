# Porra Ludópatas · Simulación Eurocopa 2024

Esta versión carga las apuestas reales del Excel de la Eurocopa 2024 y aplica los resultados reales de la fase de grupos.

## Resultado simulado

Ganador de la porra: **Many** con **46 puntos**.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Archivos de datos

- `data/apuestas.csv`: apuestas extraídas del Excel.
- `data/resultados.csv`: resultados reales Eurocopa 2024, fase de grupos.
- `data/partidos.csv`: calendario usado por la app.
- `data/clasificacion_simulada_euro2024.csv`: clasificación calculada.
- `data/detalle_puntos_euro2024.csv`: detalle apuesta a apuesta.
