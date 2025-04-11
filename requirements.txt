
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Google Sheets Setup ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)

# Beispiel: Zugriff auf die Tabelle
sheet = client.open("Provisionsdaten 2025").worksheet("Umsätze")

# === Streamlit App ===
st.set_page_config(page_title="Test mit Dateiimport", layout="centered")
st.title("📊 Provisionsrechner – Test mit JSON-Datei")

if st.button("💾 Testdaten speichern"):
    sheet.append_row(["Testuser", "April", "DL", 500, "VK", 100])
    st.success("Testdaten erfolgreich gespeichert!")
