import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

# Zugriff auf st.secrets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Verbindung zur Tabelle & Worksheet
try:
    sheet = client.open("Provisionsdaten 2025").worksheet("Umsätze")
    sheet.append_row(["✅ Verbindung erfolgreich!", "", "", "", "", ""])
    st.success("✅ Verbindung zur Tabelle steht und Testzeile wurde eingetragen.")
except Exception as e:
    st.error("❌ Fehler beim Zugriff auf Google Sheet:")
    st.error(e)
