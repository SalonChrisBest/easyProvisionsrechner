
import streamlit as st

st.set_page_config(page_title="Provisionsrechner", layout="centered")

# --- Logo und Begrüßung ---
st.image("https://raw.githubusercontent.com/SalonChrisBest/easyProvisionsrechner/main/SalonChrisBest_Logo_schwarz.jpg", width=200)




with st.container():
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

# --- Formularbereich ---
with st.form("provisions_form"):
    st.subheader("🔧 Deine Eingaben")

    name = st.text_input("Name")
from datetime import datetime

# Automatisch aktuellen Monat bestimmen
aktueller_monat = datetime.now().strftime("%B")

# Liste aller Monate (Deutsch)
monate = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

# Auswahlfeld mit aktueller Vorauswahl
monat = st.selectbox("Monat", monate, index=monate.index(aktueller_monat))

    modell = st.radio("Arbeitszeitmodell", ["Modell A (Di–Fr)", "Modell B (Mo–Fr)"])
    arbeitstage_gesamt = st.number_input("Arbeitstage im Monat (inkl. Urlaub/Feiertage)", min_value=1, max_value=31, value=22)
    arbeitstage_bisher = st.number_input("Bereits gearbeitete Tage", min_value=0, max_value=arbeitstage_gesamt, value=2)
    fixgehalt = st.number_input("Fixgehalt (Brutto €)", value=2500)
    wunschgehalt = st.number_input("Wunschgehalt (Brutto €)", value=3500)
    umsaetze_str = st.text_input("Tagesumsätze (durch Kommas getrennt)", "614, 544")
    submitted = st.form_submit_button("🚀 Berechnen")

# --- Ergebnisanzeige ---
if submitted:
    try:
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
        provision = 0
        if aktueller_umsatz > lf4:
            if aktueller_umsatz < lf5:
                provision = 0.2 * (aktueller_umsatz - lf4)
            else:
                provision = 0.3 * (aktueller_umsatz - lf4)

        st.success(f"📊 {name}, hier ist dein Zwischenstand für {monat}:")
        st.markdown(f"**Aktueller Umsatz:** {aktueller_umsatz:.2f} €")
        st.markdown(f"**Aktueller LF:** {aktueller_lf:.2f}")
        st.markdown(f"**Aktuelle Provision:** {provision:.2f} €")
        st.markdown(f"**Noch benötigter Umsatz:** {restumsatz:.2f} €")
        st.markdown(f"**Tagesziel für verbleibende {offene_tage} Tage:** {rest_tagesziel:.2f} €")

        if rest_tagesziel < 650:
            st.info("💡 Du liegst gut im Plan – mit Fokus & Upgrades ist dein Ziel gut erreichbar!")
        elif rest_tagesziel < 800:
            st.warning("🚀 Du musst etwas Gas geben – nutze starke Tage & Pflegeverkäufe!")
        else:
            st.error("🔥 Du bist hinten dran – lass uns gemeinsam überlegen, wie du aufholen kannst!")
    except Exception as e:
        st.error("Fehler bei der Berechnung. Bitte überprüfe deine Eingaben.")
        
