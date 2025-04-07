import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="dr. Buonsanti - Tool Biologia Molecolare")
st.title("dr. Buonsanti - tool interpretativo test biologia molecolare")

# Database path
DB_PATH = "storico_risultati.csv"

# Carica database se esiste
if os.path.exists(DB_PATH):
    db = pd.read_csv(DB_PATH)
else:
    db = pd.DataFrame(columns=["codice_paziente", "kit", "colori", "risultato", "concentrazione"])

# Campo per il codice paziente
codice_paziente = st.text_input("Inserisci il codice del paziente:")

# Se il codice è già presente, mostra i dati
if codice_paziente:
    if codice_paziente in db["codice_paziente"].values:
        st.subheader("🗂️ Elaborazione precedente trovata")
        match = db[db["codice_paziente"] == codice_paziente].iloc[-1]
        st.write(f"**Kit:** {match['kit']}")
        st.write(f"**Colori rilevati:** {match['colori']}")
        st.write(f"**Risultato:** {match['risultato']}")
        if pd.notna(match['concentrazione']):
            st.write(f"**Concentrazione:** {int(match['concentrazione']):,} UI/ml".replace(",", "."))

# Selezione del kit diagnostico
kit = st.radio("Seleziona il kit diagnostico:", ["HPV-geneprof", "MSTriplex-ABAnalitica", "HBV-geneprof", "HCV-geneprof"], index=None)

# Dizionari di transcodifica dei canali per ciascun kit
color_to_channel_hpv = {
    "GREEN": "FAM",
    "YELLOW": "HEX",
    "ORANGE": "TexRed/ROX",
    "RED": "Cy5",
    "CRIMSON": "Cy5.5/Quasar 705"
}
color_to_channel_mst = {
    "GREEN": "CT",
    "YELLOW": "NG",
    "RED": "MG",
    "ORANGE": "BG"
}
color_to_channel_hbv = {"GREEN": "FAM", "YELLOW": "HEX"}
color_to_channel_hcv = {"GREEN": "FAM", "YELLOW": "HEX"}

# Associazione kit → dizionario colori e lista colori validi
kit_color_map = {
    "HPV-geneprof": {"mapping": color_to_channel_hpv, "colori": list(color_to_channel_hpv.keys())},
    "MSTriplex-ABAnalitica": {"mapping": color_to_channel_mst, "colori": list(color_to_channel_mst.keys())},
    "HBV-geneprof": {"mapping": color_to_channel_hbv, "colori": list(color_to_channel_hbv.keys())},
    "HCV-geneprof": {"mapping": color_to_channel_hcv, "colori": list(color_to_channel_hcv.keys())}
}

# Stati per la sessione
if "show_quant" not in st.session_state:
    st.session_state.show_quant = False
if "result_text" not in st.session_state:
    st.session_state.result_text = ""

concentrazione = None

if kit:
    colori_validi = kit_color_map[kit]["colori"]
    mapping = kit_color_map[kit]["mapping"]
    selezionati = st.multiselect("Seleziona i colori rilevati (puoi selezionarne più di uno):", colori_validi)

    if st.button("Interpreta risultato") and codice_paziente:
        risultato = ""
        st.session_state.show_quant = False

        if kit == "HPV-geneprof":
            canali = [mapping[c] for c in selezionati]
            fam, hex_ = "FAM" in canali, "HEX" in canali
            cy5, texred, quasar = "Cy5" in canali, "TexRed/ROX" in canali, "Cy5.5/Quasar 705" in canali

            if not hex_:
                risultato = "❌ Test invalido (controllo interno assente)"
            elif not fam:
                risultato = "✅ Test valido - HPV non rilevato"
            elif fam and not cy5 and not texred and not quasar:
                risultato = "✅ Positivo per HPV ad alto rischio (genotipo non determinabile)"
            elif fam and cy5 and not texred and not quasar:
                risultato = "✅ Positivo per HPV 16"
            elif fam and not cy5 and texred and not quasar:
                risultato = "✅ Positivo per HPV 18"
            elif fam and not cy5 and not texred and quasar:
                risultato = "✅ Positivo per HPV 45"
            elif fam and cy5 and texred and not quasar:
                risultato = "✅ Positivo per HPV 16 e 18"
            elif fam and cy5 and not texred and quasar:
                risultato = "✅ Positivo per HPV 16 e 45"
            elif fam and not cy5 and texred and quasar:
                risultato = "✅ Positivo per HPV 18 e 45"
            elif fam and cy5 and texred and quasar:
                risultato = "✅ Positivo per HPV 16, 18 e 45"
            else:
                risultato = "⚠️ Caso non previsto"

        elif kit == "MSTriplex-ABAnalitica":
            canali = [mapping[c] for c in selezionati if c in mapping]
            bg = "BG" in canali
            if not bg:
                risultato = "❌ Test invalido (controllo interno assente)"
            else:
                risultato = "\n".join([
                    f"✅ {target}: positivo" if target in canali else f"❌ {target}: non rilevato"
                    for target in ["CT", "NG", "MG"]
                ])

        elif kit in ["HBV-geneprof", "HCV-geneprof"]:
            canali = [mapping[c] for c in selezionati if c in mapping]
            fam, hex_ = "FAM" in canali, "HEX" in canali

            if not fam and not hex_:
                risultato = "❌ Test invalido (controllo interno assente)"
            elif fam:
                risultato = f"✅ Test valido - {kit[:3]} positivo"
                st.session_state.show_quant = True
            else:
                risultato = f"✅ Test valido - {kit[:3]} non rilevato"

        st.session_state.result_text = risultato
        st.markdown("### Risultato")
        st.info(risultato)

    if st.session_state.show_quant:
        st.markdown("### Inserisci i dati per la quantificazione (IU/ml)")
        with st.form("quantificazione"):
            sc = st.number_input("SC (concentrazione del campione in UI/µl)", min_value=0.0, format="%.2f")
            ev = st.number_input("EV (volume di eluizione in µl)", min_value=0.0, format="%.2f")
            iv = st.number_input("IV (volume di isolamento in ml)", min_value=0.0, format="%.2f")
            calcola = st.form_submit_button("Calcola concentrazione")
            if calcola and sc > 0 and ev > 0 and iv > 0:
                concentrazione = round((sc * ev) / iv)
                st.success(f"Concentrazione campione: {concentrazione:,.0f} UI/ml".replace(",", "."))

    if st.session_state.result_text and codice_paziente:
        if st.button("Salva risultato nel database"):
            nuova_riga = {
                "codice_paziente": codice_paziente,
                "kit": kit,
                "colori": ", ".join(selezionati),
                "risultato": st.session_state.result_text,
                "concentrazione": concentrazione if concentrazione else None
            }
            db = pd.concat([db, pd.DataFrame([nuova_riga])], ignore_index=True)
            db.to_csv(DB_PATH, index=False)
            st.success("Risultato salvato correttamente nel database!")
