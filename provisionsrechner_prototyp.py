
import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd
import os

DATA_FILE = "mitarbeiterdaten_voll.csv"
UMSATZ_FILE = "umsatzverlauf_voll.csv"

def speichere_eintrag(name, monat, tag, dl, vk):
    eintrag = pd.DataFrame([{"Name": name, "Monat": monat, "Tag": tag, "DL": dl, "VK": vk}])
    if os.path.exists(UMSATZ_FILE):
        alt = pd.read_csv(UMSATZ_FILE)
        df = pd.concat([alt, eintrag], ignore_index=True)
    else:
        df = eintrag
    df.to_csv(UMSATZ_FILE, index=False)

def lade_umsatzliste(name, monat):
    if os.path.exists(UMSATZ_FILE):
        df = pd.read_csv(UMSATZ_FILE)
        gefiltert = df[(df["Name"] == name) & (df["Monat"] == monat)]
        gesamt = gefiltert["DL"].sum() + gefiltert["VK"].sum()
        return gesamt, gefiltert["DL"].sum(), gefiltert["VK"].sum()
    return 0, 0, 0

def speichere_daten(name, daten):
    df_neu = pd.DataFrame([daten])
    if os.path.exists(DATA_FILE):
        df_alt = pd.read_csv(DATA_FILE)
        df_alt = df_alt[df_alt["Name"] != name]
        df = pd.concat([df_alt, df_neu], ignore_index=True)
    else:
        df = df_neu
    df.to_csv(DATA_FILE, index=False)

def lade_daten(name):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        eintrag = df[df["Name"] == name]
        if not eintrag.empty:
            return eintrag.iloc[-1].to_dict()
    return {}

# Feiertage Rheinland-Pfalz 2025
feiertage_rlp_2025 = {
    date(2025, 1, 1), date(2025, 3, 21), date(2025, 4, 21), date(2025, 5, 1),
    date(2025, 5, 29), date(2025, 6, 9), date(2025, 6, 19), date(2025, 10, 3),
    date(2025, 11, 1), date(2025, 12, 25), date(2025, 12, 26)
}

st.set_page_config(page_title="Provisionsrechner", layout="centered")
st.image("https://raw.githubusercontent.com/SalonChrisBest/easyProvisionsrechner/main/SalonChrisBest_Logo_schwarz.jpg", width=200)
st.markdown("### Willkommen im Provisionsrechner 💡")

name = st.text_input("Name")
daten = {}
if st.button("✅ Namen bestätigen & Daten laden") and name:
    daten = lade_daten(name)
    st.success("Daten wurden geladen!")

monate = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]
monat_index = datetime.now().month - 1
aktueller_monat = monate[monat_index]
monat = st.selectbox("Monat", monate, index=monat_index)
