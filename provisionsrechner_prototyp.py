
import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd
import os

DATA_FILE = "umsatzverlauf.csv"

def speichere_eintrag(name, monat, tag, dl, vk):
    eintrag = pd.DataFrame([{"Name": name, "Monat": monat, "Tag": tag, "DL": dl, "VK": vk}])
    if os.path.exists(DATA_FILE):
        alt = pd.read_csv(DATA_FILE)
        df = pd.concat([alt, eintrag], ignore_index=True)
    else:
        df = eintrag
    df.to_csv(DATA_FILE, index=False)

def lade_umsatzliste(name, monat):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        gefiltert = df[(df["Name"] == name) & (df["Monat"] == monat)]
        gesamt = gefiltert["DL"].sum() + gefiltert["VK"].sum()
        return gesamt, gefiltert["DL"].sum(), gefiltert["VK"].sum()
    return 0, 0, 0

feiertage_rlp_2025 = {
    date(2025, 1, 1), date(2025, 3, 21), date(2025, 4, 21), date(2025, 5, 1),
    date(2025, 5, 29), date(2025, 6, 9), date(2025, 6, 19), date(2025, 10, 3),
    date(2025, 11, 1), date(2025, 12, 25), date(2025, 12, 26)
}

st.set_page_config(page_title="Provisionsrechner", layout="centered")
st.image("https://raw.githubusercontent.com/SalonChrisBest/easyProvisionsrechner/main/SalonChrisBest_Logo_schwarz.jpg", width=200)
st.markdown("### Willkommen im Provisionsrechner 💡")

name = st.text_input("Name")
monate = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]
aktueller_monat = datetime.now().strftime("%B")
monat = st.selectbox("Monat", monate, index=monate.index(aktueller_monat))
modell = st.radio("Arbeitszeitmodell", ["Modell A (Di–Fr)", "Modell B (Mo–Fr)"])
urlaubstage = st.number_input("Geplante Urlaubstage", min_value=0, max_value=31, value=0)
arbeitstage_bisher = st.number_input("Bereits gearbeitete Tage", min_value=0, max_value=31, value=2)
fixgehalt = st.number_input("Fixgehalt (Brutto €)", value=2500)
wunschgehalt = st.number_input("Wunschgehalt (Brutto €)", value=3500)

umsatz_dl = st.number_input("Umsatz heute (Dienstleistung)", value=0)
umsatz_vk = st.number_input("Umsatz heute (Verkauf)", value=0)
umsatz_gesamt_heute = umsatz_dl + umsatz_vk
heutiges_datum = date.today()

if st.button("💾 Umsatz speichern"):
    if name and umsatz_gesamt_heute > 0:
        speichere_eintrag(name, monat, heutiges_datum.day, umsatz_dl, umsatz_vk)
        st.success("Umsatz wurde gespeichert! 🎉")

aktueller_umsatz, gesamt_dl, gesamt_vk = lade_umsatzliste(name, monat)

monat_nummer = monate.index(monat) + 1
jahr = 2025
_, anzahl_tage = calendar.monthrange(jahr, monat_nummer)

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
restumsatz = ziel_umsatz - aktueller_umsatz
rest_tagesziel = restumsatz / offene_tage
aktueller_lf = aktueller_umsatz / fixgehalt
fortschritt = aktueller_umsatz / ziel_umsatz * 100
provision = 0
if aktueller_umsatz > lf4:
    if aktueller_umsatz < lf5:
        provision = 0.2 * (aktueller_umsatz - lf4)
    else:
        provision = 0.3 * (aktueller_umsatz - lf4)

verkaufsanteil = (gesamt_vk / aktueller_umsatz * 100) if aktueller_umsatz > 0 else 0

st.markdown("---")
st.subheader(f"📊 Dein Zwischenstand für {monat}")
st.markdown(f"**Arbeitstage (abzgl. Urlaub):** {arbeitstage_gesamt}")
st.markdown(f"**Umsatz gesamt:** {aktueller_umsatz:.2f} €")
st.markdown(f"**Davon DL:** {gesamt_dl:.2f} € | **VK (Heimpflege):** {gesamt_vk:.2f} €")
st.markdown(f"**Heimpflegeanteil:** {verkaufsanteil:.1f} %")
st.markdown(f"**Aktueller LF:** {aktueller_lf:.2f}")
st.markdown(f"**Aktuelle Provision:** {provision:.2f} €")
st.markdown(f"**Noch benötigter Umsatz:** {restumsatz:.2f} €")
st.markdown(f"**Tagesziel für verbleibende {offene_tage} Tage:** {rest_tagesziel:.2f} €")

st.subheader("📈 Fortschritt zum Ziel")
st.progress(min(1.0, fortschritt / 100))

if fortschritt >= 100:
    st.balloons()
    st.success("🎉 BOOM! Du hast dein Ziel geknackt! Gönn dir den Moment – das ist DEIN Erfolg! 🥂")

st.markdown("---")
st.subheader("💬 Motivation")
if fortschritt < 50:
    st.info("🔁 Du bist in Bewegung – dranbleiben lohnt sich!")
elif fortschritt < 100:
    st.info("🚀 Starke Basis! Jetzt weiter durchziehen – du kannst sogar drüber hinaus!")
elif 100 <= fortschritt <= 110:
    st.success("🏁 Ziel erreicht – und du hast noch Power! Bleib dran – jeder Euro zählt!")
elif fortschritt > 110:
    st.success("🌟 Du setzt neue Maßstäbe! Das ist nicht nur stark – das inspiriert dein Team! 💙")
