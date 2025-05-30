import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="Divisas en Tiempo Real", layout="wide")
st.title("💱 Seguimiento de Pares de Divisas en Tiempo Real")

# RECARGAR AUTOMÁTICAMENTE CADA 15 SEGUNDOS
st_autorefresh(interval=15000, key="auto_refresh")

# API KEY
API_KEY = "CYHTweCGGnvgzISZl5rJKQ5lT8AtGVxR"

# Lista de pares en formato (from_currency, to_currency)
pares = [
    ("EUR", "USD"),
    ("MXN", "ZAR"),
    ("USD", "JPY"),
    ("GBP", "USD"),
]

# Función para obtener la última cotización
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

# Historial para todos los pares
if "historial" not in st.session_state:
    st.session_state.historial = {f"{a}/{b}": [] for a, b in pares}

# Mostrar resultados
for from_currency, to_currency in pares:
    pair_name = f"{from_currency}/{to_currency}"
    precio, timestamp = obtener_ultima_cotizacion(from_currency, to_currency)

    st.markdown(f"---")
    st.subheader(f"📈 Cotización actual: {pair_name}")

    if precio is not None:
        st.session_state.historial[pair_name].append({"hora": timestamp, "precio": precio})
        df = pd.DataFrame(st.session_state.historial[pair_name])

        st.metric("Precio (ask)", precio)
        st.caption(f"🕒 Última actualización: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        fig = px.line(df, x="hora", y="precio", title=f"Histórico de {pair_name}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.tail(5))
    else:
        st.warning(f"❌ No se pudo obtener datos para {pair_name}. Verifica la API o el par.")

