import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Configuración de la app
st.set_page_config(page_title="Divisas en Tiempo Real", layout="wide")
st.title("💱 Seguimiento de Divisas en Tiempo Real")

# Refrescar automáticamente cada 15 segundos
st_autorefresh(interval=15000, key="refresh")

# API Key de Polygon.io
API_KEY = "CYHTweCGGnvgzISZl5rJKQ5lT8AtGVxR"

# Entrada del par de divisas
par_input = st.text_input("Introduce el par de divisas (ej. EUR/USD)", value="EUR/USD")

# Parseo del par
try:
    from_currency, to_currency = par_input.strip().upper().split("/")
except ValueError:
    st.error("⚠️ Usa el formato correcto: EUR/USD")
    st.stop()

# Función para obtener la última cotización
def obtener_ultima_cotizacion(from_currency, to_currency):
    url = f"https://api.polygon.io/v2/last/forex/{from_currency}/{to_currency}?apiKey={API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if "last" in data:
            quote = data["last"]
            precio = quote["ask"]
            timestamp = datetime.fromtimestamp(quote["timestamp"] / 1000)
            return precio, timestamp
    return None, None

# Inicializar historial en sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

# Obtener cotización actual
precio, timestamp = obtener_ultima_cotizacion(from_currency, to_currency)

if precio is not None:
    st.session_state.historial.append({"hora": timestamp, "precio": precio})
    df = pd.DataFrame(st.session_state.historial)

    st.subheader(f"📈 Cotización actual: {from_currency}/{to_currency}")
    st.metric("Precio (ask)", precio, help="Precio de venta más reciente")
    st.write("🕒 Última actualización:", timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    fig = px.line(df, x="hora", y="precio", title="Histórico en Tiempo Real")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.tail(10))
else:
    st.warning("❌ No se pudo obtener datos. Verifica el par o la API.")
