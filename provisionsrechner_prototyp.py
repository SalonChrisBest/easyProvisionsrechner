
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import calendar

# === Google Sheets Setup ===
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("Provisionsdaten 2025").worksheet("Umsätze")

# === Seitenlayout ===
st.set_page_config(page_title="Provisionsrechner", layout="centered")
st.image("https://raw.githubusercontent.com/SalonChrisBest/easyProvisionsrechner/main/SalonChrisBest_Logo_schwarz.jpg", width=200)

st.markdown("### Willkommen im Provisionsrechner 💡")
st.markdown("""
Schön, dass du da bist! 🙌  
Diese App hilft dir dabei, **dein Wunschgehalt zu erreichen** – transparent, motivierend und realistisch.

🔍 Gib einfach deinen aktuellen Stand ein,  
🚀 und du bekommst direkt deinen persönlichen Fahrplan für den Monat.  
💡 Egal wo du gerade stehst – du kannst dein Ziel erreichen.

_Let’s grow together._  
**Dein Chris 💙**
""")

st.divider()

# === Formular zur Eingabe ===
with st.form("provisions_form"):
    st.subheader("🔧 Deine Eingaben")

    name = st.text_input("Name")
    monat = st.selectbox("Monat", [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ])
    modell = st.radio("Arbeitszeitmodell", ["Modell A (Di–Fr)", "Modell B (Mo–Fr)"])
    urlaubstage = st.number_input("Geplante Urlaubstage in diesem Monat", min_value=0, max_value=31, value=0)
    arbeitstage_bisher = st.number_input("Bereits gearbeitete Tage", min_value=0, max_value=31, value=0)
    fixgehalt = st.number_input("Fixgehalt (Brutto €)", value=2500)
    wunschgehalt = st.number_input("Wunschgehalt (Brutto €)", value=3500)
    umsatz_dl = st.number_input("Umsatz Dienstleistung (€)", min_value=0.0)
    umsatz_vk = st.number_input("Umsatz Verkauf (€)", min_value=0.0)

    submitted = st.form_submit_button("🚀 Berechnen & Speichern")

# === Feiertagsbasierte Arbeitstage berechnen ===
def berechne_arbeitstage(monat, jahr, modell, urlaubstage):
    feiertage = {
        "Januar": [1, 6],
        "April": [1],
        "Mai": [1, 9, 20, 29],
        "Juni": [30],
        "August": [15],
        "Oktober": [3, 31],
        "November": [1],
        "Dezember": [25, 26],
    }
    wochentage = [1, 2, 3, 4] if modell == "Modell A (Di–Fr)" else [0, 1, 2, 3, 4]
    tage_im_monat = calendar.monthrange(jahr, monat)[1]
    arbeitstage = sum(
        1 for tag in range(1, tage_im_monat + 1)
        if datetime.date(jahr, monat, tag).weekday() in wochentage and tag not in feiertage.get(calendar.month_name[monat], [])
    )
    return arbeitstage - urlaubstage

# === Ergebnisse und Berechnung ===
if submitted:
    monat_index = list(calendar.month_name).index(monat)
    jahr = datetime.date.today().year
    arbeitstage_gesamt = berechne_arbeitstage(monat_index, jahr, modell, urlaubstage)
    aktueller_umsatz = umsatz_dl + umsatz_vk
    lf4 = fixgehalt * 4
    provisionsziel = wunschgehalt - fixgehalt
    ziel_umsatz = (provisionsziel / 0.3) + lf4
    offene_tage = arbeitstage_gesamt - arbeitstage_bisher
    restumsatz = ziel_umsatz - aktueller_umsatz
    rest_tagesziel = restumsatz / offene_tage if offene_tage > 0 else 0
    aktueller_lf = aktueller_umsatz / fixgehalt
    provision = 0
    if aktueller_umsatz > lf4:
        provision = 0.3 * (aktueller_umsatz - lf4)

    fortschritt = min(aktueller_umsatz / ziel_umsatz, 1.0)
    st.progress(fortschritt)
    if fortschritt >= 1.0:
        st.balloons()
        st.success("🎉 Du hast dein Ziel erreicht! Mega stark!")

    st.success(f"📊 {name}, hier ist dein Zwischenstand für {monat}:")
    st.markdown(f"- **Gesamtumsatz:** {aktueller_umsatz:.2f} €")
    st.markdown(f"- **Heimpflegeanteil (VK):** {umsatz_vk / aktueller_umsatz:.2%}")
    st.markdown(f"- **Aktueller LF:** {aktueller_lf:.2f}")
    st.markdown(f"- **Provision bisher:** {provision:.2f} €")
    st.markdown(f"- **Noch benötigter Umsatz:** {restumsatz:.2f} €")
    st.markdown(f"- **Tagesziel für verbleibende {offene_tage} Tage:** {rest_tagesziel:.2f} €")

    if rest_tagesziel < 650:
        st.info("✅ Du liegst gut im Plan – bleib dran!")
    elif rest_tagesziel < 800:
        st.warning("💪 Mit nur einem zusätzlichen Produktverkauf pro Kunde bist du wieder im Rennen. Glaub an dich!")
    else:
        st.error("🔥 Da ist noch Luft nach oben – baue deine Expertise gezielt in die Beratung ein.")

    try:
        sheet.append_row([name, monat, f"{umsatz_dl:.2f}", f"{umsatz_vk:.2f}", f"{aktueller_umsatz:.2f}", f"{provision:.2f}"])
        st.success("📥 Daten erfolgreich gespeichert!")
    except Exception as e:
        st.error("Fehler beim Speichern in Google Sheets. Bitte später erneut versuchen.")
