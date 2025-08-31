import os
import time
import pandas as pd
import streamlit as st
import httpx

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
SYMBOLS = [s.strip() for s in os.environ.get("SUBSCRIBE_SYMBOLS", "AAPL,MSFT").split(",") if s.strip()]

st.set_page_config(page_title="Market Dashboard", layout="wide")
st.title("📈 Real‑Time Market Dashboard")

cols = st.columns(len(SYMBOLS))
for i, sym in enumerate(SYMBOLS):
    try:
        r = httpx.get(f"{API_BASE}/latest", params={"symbol": sym}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            cols[i].metric(label=sym, value=f"{data['price']:.2f}")
        else:
            cols[i].metric(label=sym, value="—")
    except Exception:
        cols[i].metric(label=sym, value="—")

symbol = st.selectbox("Symbol", SYMBOLS)
minutes = st.slider("Minutes", 5, 240, 60, step=5)
placeholder = st.empty()

while True:
    try:
        r = httpx.get(f"{API_BASE}/candles", params={"symbol": symbol, "minutes": minutes}, timeout=10)
        if r.status_code == 200:
            candles = r.json()
            if candles:
                df = pd.DataFrame(candles)
                df["t"] = pd.to_datetime(df["t"])  # ensure datetime
                df.set_index("t", inplace=True)
                with placeholder.container():
                    st.line_chart(df["c"], height=300, use_container_width=True)
            else:
                placeholder.info("No candle data yet. Waiting for ticks…")
        else:
            placeholder.error("API error fetching candles")
    except Exception as e:
        placeholder.warning(f"Fetching error: {e}")
    time.sleep(2)  # refresh interval
