
import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd
import os

DATA_FILE = "mitarbeiterdaten.csv"

# --- Funktion zum Laden der gespeicherten Daten ---
def lade_daten(name):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        eintrag = df[df["Name"] == name]
        if not eintrag.empty:
            return eintrag.iloc[-1].to_dict()
    return {}

# --- Funktion zum Speichern der Daten ---
def speichere_daten(daten):
    df_neu = pd.DataFrame([daten])
    if os.path.exists(DATA_FILE):
        df_alt = pd.read_csv(DATA_FILE)
        df = pd.concat([df_alt, df_neu], ignore_index=True)
    else:
        df = df_neu
    df.to_csv(DATA_FILE, index=False)

# --- Feiertage Rheinland-Pfalz ---
feiertage_rlp_2025 = {
    date(2025, 1, 1), date(2025, 3, 21), date(2025, 4, 21), date(2025, 5, 1),
    date(2025, 5, 29), date(2025, 6, 9), date(2025, 6, 19), date(2025, 10, 3),
    date(2025, 11, 1), date(2025, 12, 25), date(2025, 12, 26)
}

st.set_page_config(page_title="Provisionsrechner", layout="centered")
st.image("https://raw.githubusercontent.com/SalonChrisBest/easyProvisionsrechner/main/SalonChrisBest_Logo_schwarz.jpg", width=200)
st.markdown("### Willkommen im Provisionsrechner 💡")

name = st.text_input("Gib deinen Namen ein (für automatische Speicherung):")
daten_alt = lade_daten(name) if name else {}

# --- Formularbereich ---
with st.form("provisions_form"):
    aktueller_monat = datetime.now().strftime("%B")
    monate = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    monat = st.selectbox("Monat", monate, index=monate.index(aktueller_monat))
    modell = st.radio("Arbeitszeitmodell", ["Modell A (Di–Fr)", "Modell B (Mo–Fr)"],
                      index=0 if daten_alt.get("Modell") == "Modell A (Di–Fr)" else 1)
    urlaubstage = st.number_input("Geplante Urlaubstage", min_value=0, max_value=31,
                                  value=int(daten_alt.get("Urlaubstage", 0)))
    arbeitstage_bisher = st.number_input("Bereits gearbeitete Tage", min_value=0, max_value=31,
                                         value=int(daten_alt.get("GearbeiteteTage", 2)))
    fixgehalt = st.number_input("Fixgehalt (Brutto €)", value=float(daten_alt.get("Fixgehalt", 2500)))
    wunschgehalt = st.number_input("Wunschgehalt (Brutto €)", value=float(daten_alt.get("Wunschgehalt", 3500)))
    umsaetze_str = st.text_input("Tagesumsätze (durch Kommas getrennt)",
                                 daten_alt.get("Umsaetze", "614, 544"))
    submitted = st.form_submit_button("🚀 Berechnen")

# --- Berechnung & Anzeige ---
if submitted and name:
    monat_nummer = monate.index(monat) + 1
    jahr = datetime.now().year
    _, anzahl_tage = calendar.monthrange(jahr, monat_nummer)

    arbeitstage_gesamt = 0
    for tag in range(1, anzahl_tage + 1):
        aktuelles_datum = date(jahr, monat_nummer, tag)
        wochentag = aktuelles_datum.weekday()
        if modell == "Modell A (Di–Fr)" and wochentag in [1, 2, 3, 4]:
            if aktuelles_datum not in feiertage_rlp_2025:
                arbeitstage_gesamt += 1
        elif modell == "Modell B (Mo–Fr)" and wochentag in [0, 1, 2, 3, 4]:
            if aktuelles_datum not in feiertage_rlp_2025:
                arbeitstage_gesamt += 1

    arbeitstage_gesamt -= urlaubstage

    umsatzliste = [float(x.strip()) for x in umsaetze_str.split(",") if x.strip()]
    aktueller_umsatz = sum(umsatzliste)
    lf4 = fixgehalt * 4
    lf5 = fixgehalt * 5
    provisionsziel = wunschgehalt - fixgehalt
    ziel_umsatz = (provisionsziel / 0.3) + lf4
    offene_tage = arbeitstage_gesamt - arbeitstage_bisher
    restumsatz = ziel_umsatz - aktueller_umsatz
    rest_tagesziel = restumsatz / offene_tage if offene_tage > 0 else 0
    aktueller_lf = aktueller_umsatz / fixgehalt
    fortschritt_prozent = aktueller_umsatz / ziel_umsatz * 100
    provision = 0
    if aktueller_umsatz > lf4:
        if aktueller_umsatz < lf5:
            provision = 0.2 * (aktueller_umsatz - lf4)
        else:
            provision = 0.3 * (aktueller_umsatz - lf4)

    st.success(f"📊 {name}, hier ist dein Zwischenstand für {monat}:")
    st.markdown(f"**Arbeitstage (abzgl. Urlaub):** {arbeitstage_gesamt}")
    st.markdown(f"**Aktueller Umsatz:** {aktueller_umsatz:.2f} €")
    st.markdown(f"**Aktueller LF:** {aktueller_lf:.2f}")
    st.markdown(f"**Aktuelle Provision:** {provision:.2f} €")
    st.markdown(f"**Noch benötigter Umsatz:** {restumsatz:.2f} €")
    st.markdown(f"**Tagesziel für verbleibende {offene_tage} Tage:** {rest_tagesziel:.2f} €")

    # Motivation nach Fortschritt
    st.markdown("---")
    st.subheader("💬 Motivation")
    if fortschritt_prozent < 25:
        st.info("Du hast noch fast den ganzen Monat vor dir – alles ist möglich! 💥")
    elif fortschritt_prozent < 50:
        st.info("Du bist in Bewegung – bleib dran, du wächst mit jedem Tag! 🌱")
    elif fortschritt_prozent < 75:
        st.info("Halbzeit! Du weißt, wie’s läuft – jetzt kommt der Feinschliff! 🔥")
    elif fortschritt_prozent < 90:
        st.success("Du bist sooo nah dran! Noch ein paar starke Tage und du bist durch 🚀")
    else:
        st.success("Finish strong! Gönn dir den Erfolg – du hast es verdient! 🏁")

    # Tipps bei Rückstand
    if rest_tagesziel > 750:
        st.warning("🔧 Du bist etwas hinten dran. Tipp: Nutze ruhige Zeiten für Pflegeverkäufe oder Zusatzleistungen!")
    if rest_tagesziel > 900:
        st.warning("🔥 Dein Tagesziel ist gerade hoch. Tipp: Konzentrier dich auf Upgrades & hohe Durchschnittsbons,du bist es wert!")

    daten_neu = {
        "Name": name, "Monat": monat, "Modell": modell, "Urlaubstage": urlaubstage,
        "GearbeiteteTage": arbeitstage_bisher, "Fixgehalt": fixgehalt,
        "Wunschgehalt": wunschgehalt, "Umsaetze": umsaetze_str
    }
    speichere_daten(daten_neu)
