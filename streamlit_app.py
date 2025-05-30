import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# Tu API Key de Polygon.io
API_KEY = "CYHTweCGGnvgzISZl5rJKQ5lT8AtGVxR"

# Función para descargar datos por hora de hoy
def obtener_datos(par):
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.polygon.io/v2/aggs/ticker/{par}/range/1/hour/{fecha_hoy}/{fecha_hoy}?adjusted=true&sort=asc&limit=50000&apiKey={API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        res = r.json()
        resultados = res.get("results", [])
        if resultados:
            df = pd.DataFrame(resultados)
            df["datetime"] = pd.to_datetime(df["t"], unit="ms")
            df.set_index("datetime", inplace=True)
            df["rets"] = df["c"].pct_change()
            return df
    return pd.DataFrame()

# Interfaz de usuario
st.set_page_config(page_title="Divisas en Tiempo Real", layout="wide")
st.title("🌍 Seguimiento de Divisas en Tiempo Real")

# Entrada de usuario
par = st.text_input("Introduce el ticker del par de divisas (ej. C:EURUSD)", value="C:EURUSD")

# Botón para cargar datos
if st.button("🔄 Obtener datos"):
    df = obtener_datos(par)
    if not df.empty:
        st.subheader(f"📈 Precio horario para {par}")
        fig1 = px.line(df, x=df.index, y="c", labels={"c": "Precio Cierre", "datetime": "Hora"})
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 Rendimiento horario")
        fig2 = px.line(df, x=df.index, y="rets", labels={"rets": "Rendimiento", "datetime": "Hora"})
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df[["c", "rets"]].tail(10))
    else:
        st.warning("⚠️ No se encontraron datos o hubo error con la API.")
