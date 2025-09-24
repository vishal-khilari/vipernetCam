# src/app.py
import streamlit as st
import pandas as pd
import sqlite3
import os
from encrypt_alert import decrypt_alert_bytes

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'forensics.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

st.set_page_config(layout='wide', page_title='ViperNet Dashboard')
st.title("ViperNet Dashboard — Forensics & Alerts")

df = pd.read_sql_query("SELECT * FROM intrusion_logs ORDER BY id DESC LIMIT 200", conn)
st.subheader("Recent logs")
st.dataframe(df[['id','timestamp','zone','anomaly','ipfs_cid','tx_hash']])

if not df.empty:
    # map requires lat/lon columns present and not null
    map_df = df[['latitude','longitude']].dropna().astype(float)
    if not map_df.empty:
        st.map(map_df)

st.subheader("Decrypt an alert token (hex)")
token_hex = st.text_area("Paste alert_token_hex value here")
if token_hex:
    try:
        token_bytes = bytes.fromhex(token_hex.strip())
        plaintext = decrypt_alert_bytes(token_bytes)
        st.markdown("**Alert JSON:**")
        st.json(plaintext.decode())
    except Exception as e:
        st.error("Decryption failed: " + str(e))
