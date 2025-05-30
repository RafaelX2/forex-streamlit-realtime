import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import re

# CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="Divisas en Tiempo Real", layout="wide")
st.title("💱 Seguimiento de Divisas en Tiempo Real")

# RECARGAR AUTOMÁTICAMENTE CADA 15 SEGUNDOS
st_autorefresh(interval=15000, key="auto_refresh")

# CLAVE API DE POLYGON.IO
API_KEY = "CYHTweCGGnvgzISZl5rJKQ5lT8AtGVxR"

# INPUT DEL PAR DE DIVISAS
par_input = st.text_input("Introduce el par de divisas (ej. EUR/USD o EUR USD)", value="EUR/USD")

# PROCESAR EL INPUT
tokens = re.split(r"[/\s]+", par_input.strip().upper())
if len(tokens) != 2:
    st.error("⚠️ Usa el formato correcto: EUR/USD o EUR USD")
    st.stop()

from_currency, to_currency = tokens

# FUNCION PARA OBTENER ÚLTIMA COTIZACIÓN USANDO EL ENDPOINT CORRECTO
def obtener_ultima_cotizacion(from_currency, to_currency):
    url = f"https://api.polygon.io/v1/last_quote/currencies/{from_currency}/{to_currency}?apiKey={API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if "last" in data:
            quote = data["last"]
            precio = quote.get("ask", None)
            timestamp = datetime.fromtimestamp(quote.get("timestamp", 0) / 1000)
            return precio, timestamp
    return None, None

# GUARDAR HISTORIAL EN LA SESIÓN
if "historial" not in st.session_state:
    st.session_state.historial = []

# OBTENER COTIZACIÓN Y ACTUALIZAR
precio, timestamp = obtener_ultima_cotizacion(from_currency, to_currency)

if precio is not None:
    st.session_state.historial.append({"hora": timestamp, "precio": precio})
    df = pd.DataFrame(st.session_state.historial)

    # MOSTRAR RESULTADOS
    st.subheader(f"📈 Cotización actual: {from_currency}/{to_currency}")
    st.metric("Precio (ask)", precio, help="Precio de venta más reciente")
    st.write("🕒 Última actualización:", timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    fig = px.line(df, x="hora", y="precio", title="Histórico de Cotizaciones en Tiempo Real")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.tail(10))

else:
    st.warning("❌ No se pudo obtener datos. Verifica el par o la API.")
