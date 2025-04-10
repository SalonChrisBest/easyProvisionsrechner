import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import calendar

# ------------------- GOOGLE SHEETS SETUP -------------------
SHEET_NAME = "Provisionsdaten 2025"  # <- Name deines Google Sheets
JSON_KEYFILE = "provisionsapp-456412-9e8e0d5e3174.json"  # JSON-Datei lokal im Projektordner

# Verbindung herstellen
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, scope)
client = gspread.authorize(creds)
sheet_einstellungen = client.open(SHEET_NAME).worksheet("Einstellungen")
sheet_umsatz = client.open(SHEET_NAME).worksheet("Umsätze")

# ------------------- STREAMLIT UI -------------------
st.set_page_config(page_title="Provisionsrechner", layout="centered")
st.image("https://raw.githubusercontent.com/SalonChrisBest/easyProvisionsrechner/main/SalonChrisBest_Logo_schwarz.jpg", width=200)
st.markdown("### Willkommen im Provisionsrechner 💡")

name = st.text_input("Name")
daten = {}

# Daten auslesen
if st.button("✅ Namen bestätigen & Daten laden") and name:
    daten_rows = sheet_einstellungen.get_all_records()
    for row in daten_rows:
        if row["Name"] == name:
            daten = row
            break
    st.success("Daten erfolgreich geladen!")

monate = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]
aktueller_monat = datetime.now().strftime("%B")
monat = st.selectbox("Monat", monate, index=monate.index(aktueller_monat))

modell = st.radio("Arbeitszeitmodell", ["Modell A (Di–Fr)", "Modell B (Mo–Fr)"], 
                  index=0 if daten.get("Modell") == "Modell A (Di–Fr)" else 1)

urlaubstage = st.number_input("Geplante Urlaubstage", min_value=0, max_value=31,
                              value=int(daten.get("Urlaubstage", 0)) if daten else 0)

arbeitstage_bisher = st.number_input("Bereits gearbeitete Tage", min_value=0, max_value=31,
                                     value=int(daten.get("GearbeiteteTage", 2)) if daten else 2)

fixgehalt = st.number_input("Fixgehalt (Brutto €)", value=float(daten.get("Fixgehalt", 2500)) if daten else 2500)
wunschgehalt = st.number_input("Wunschgehalt (Brutto €)", value=float(daten.get("Wunschgehalt", 3500)) if daten else 3500)

umsatz_dl = st.number_input("Umsatz heute (Dienstleistung)", value=0)
umsatz_vk = st.number_input("Umsatz heute (Verkauf)", value=0)
umsatz_gesamt = umsatz_dl + umsatz_vk
heute = date.today()

if st.button("💾 Umsatz speichern"):
    sheet_einstellungen.append_row([name, modell, urlaubstage, arbeitstage_bisher, fixgehalt, wunschgehalt])
    sheet_umsatz.append_row([name, monat, heute.isoformat(), umsatz_dl, umsatz_vk])
    st.success("✅ Daten erfolgreich gespeichert!")

# Daten summieren
alle_eintraege = sheet_umsatz.get_all_records()
umsatz_summe = sum(row["DL"] + row["VK"] for row in alle_eintraege if row["Name"] == name and row["Monat"] == monat)
umsatz_dl_summe = sum(row["DL"] for row in alle_eintraege if row["Name"] == name and row["Monat"] == monat)
umsatz_vk_summe = sum(row["VK"] for row in alle_eintraege if row["Name"] == name and row["Monat"] == monat)

# Berechnung
monat_nummer = monate.index(monat) + 1
jahr = 2025
_, anzahl_tage = calendar.monthrange(jahr, monat_nummer)

feiertage_rlp_2025 = {
    date(2025, 1, 1), date(2025, 3, 21), date(2025, 4, 21), date(2025, 5, 1),
    date(2025, 5, 29), date(2025, 6, 9), date(2025, 6, 19), date(2025, 10, 3),
    date(2025, 11, 1), date(2025, 12, 25), date(2025, 12, 26)
}

arbeitstage_gesamt = 0
for tag in range(1, anzahl_tage + 1):
    d = date(jahr, monat_nummer, tag)
    wt = d.weekday()
    if modell == "Modell A (Di–Fr)" and wt in [1, 2, 3, 4] and d not in feiertage_rlp_2025:
        arbeitstage_gesamt += 1
    elif modell == "Modell B (Mo–Fr)" and wt in [0, 1, 2, 3, 4] and d not in feiertage_rlp_2025:
        arbeitstage_gesamt += 1
arbeitstage_gesamt -= urlaubstage

lf4 = fixgehalt * 4
lf5 = fixgehalt * 5
provisionsziel = wunschgehalt - fixgehalt
ziel_umsatz = (provisionsziel / 0.3) + lf4
offene_tage = max(1, arbeitstage_gesamt - arbeitstage_bisher)
restumsatz = ziel_umsatz - umsatz_summe
rest_tagesziel = restumsatz / offene_tage
aktueller_lf = umsatz_summe / fixgehalt
fortschritt = umsatz_summe / ziel_umsatz * 100

provision = 0
if umsatz_summe > lf4:
    if umsatz_summe < lf5:
        provision = 0.2 * (umsatz_summe - lf4)
    else:
        provision = 0.3 * (umsatz_summe - lf4)

verkaufsanteil = (umsatz_vk_summe / umsatz_summe * 100) if umsatz_summe > 0 else 0

# Ausgabe
st.markdown("---")
st.subheader(f"📊 Zwischenstand für {monat}")
st.markdown(f"**Umsatz gesamt:** {umsatz_summe:.2f} €")
st.markdown(f"**DL:** {umsatz_dl_summe:.2f} € | **VK:** {umsatz_vk_summe:.2f} €")
st.markdown(f"**Heimpflegeanteil:** {verkaufsanteil:.1f} %")
st.markdown(f"**Aktueller LF:** {aktueller_lf:.2f}")
st.markdown(f"**Provision:** {provision:.2f} €")
st.markdown(f"**Noch offener Umsatz:** {restumsatz:.2f} €")
st.markdown(f"**Tagesziel für {offene_tage} verbleibende Tage:** {rest_tagesziel:.2f} €")

st.subheader("📈 Fortschritt zum Ziel")
st.progress(min(1.0, fortschritt / 100))
if fortschritt >= 100:
    st.balloons()
    st.success("🎉 BOOM! Ziel erreicht – du rockst das!")
