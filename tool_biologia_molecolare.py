import streamlit as st

st.set_page_config(page_title="dr. Buonsanti - Tool Biologia Molecolare")
st.title("dr. Buonsanti - tool interpretativo test biologia molecolare")

# Selezione del kit diagnostico
kit = st.radio("Seleziona il kit diagnostico:", [
    "HPV-geneprof",
    "MSTriplex-ABAnalitica",
    "HBV-geneprof",
    "HCV-geneprof",
    "MTHFR-C677T-Geneprof"
], index=None)

# Transcodifica universale canale → colore
universal_channel_color = {
    "FAM": "GREEN",
    "SYBR Green I": "GREEN",
    "Fluorescein": "GREEN",
    "EvaGreen": "GREEN",
    "Alexa Fluor 488": "GREEN",
    "JOE": "YELLOW",
    "VIC": "YELLOW",
    "HEX": "YELLOW",
    "TET": "YELLOW",
    "CAL Fluor Gold 540": "YELLOW",
    "Yakima Yellow": "YELLOW",
    "ROX": "ORANGE",
    "CAL Fluor Red 610": "ORANGE",
    "Cy3.5": "ORANGE",
    "Texas Red": "ORANGE",
    "Alexa Fluor 568": "ORANGE",
    "Cy5": "RED",
    "Quasar 670": "RED",
    "LightCycler Red640": "RED",
    "Alexa Fluor 633": "RED",
    "Quasar 705": "CRIMSON",
    "LightCycler Red705": "CRIMSON",
    "Alexa Fluor 680": "CRIMSON"
}

# Mapping kit → sonde → canali → colori
kit_sonde = {
    "HPV-geneprof": ["FAM", "HEX", "ROX", "Cy5", "Quasar 705"],
    "MSTriplex-ABAnalitica": ["FAM", "HEX", "Cy5", "ROX"],
    "HBV-geneprof": ["FAM", "HEX"],
    "HCV-geneprof": ["FAM", "HEX"],
    "MTHFR-C677T-Geneprof": ["FAM", "HEX"]
}

kit_color_map = {}
for nome_kit, sonde in kit_sonde.items():
    mapping = {}
    for sonda in sonde:
        colore = universal_channel_color.get(sonda)
        if colore:
            mapping[colore] = sonda
    kit_color_map[nome_kit] = {"mapping": mapping, "colori": list(mapping.keys())}

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

    if st.button("Interpreta risultato"):
        risultato = ""
        st.session_state.show_quant = False

        if kit == "HPV-geneprof":
            canali = [mapping[c] for c in selezionati]
            fam, hex_ = "FAM" in canali, "HEX" in canali
            cy5, texred, quasar = "Cy5" in canali, "ROX" in canali, "Quasar 705" in canali

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
            bg = "ROX" in canali
            if not bg:
                risultato = "❌ Test invalido (controllo interno assente)"
            else:
                risultato = "\n".join([
                    f"✅ {label}: positivo" if probe in canali else f"❌ {label}: non rilevato"
                    for probe, label in zip(["FAM", "HEX", "Cy5"], ["Chlamydia trachomatis (CT)", "Neisseria gonorrhoeae (NG)", "Mycoplasma genitalium (MG)"])
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

        elif kit == "MTHFR-C677T-Geneprof":
            canali = [mapping[c] for c in selezionati if c in mapping]
            fam, hex_ = "FAM" in canali, "HEX" in canali
            if fam and not hex_:
                risultato = "✅ Mutazione C677T assente (omozigote wild type - C/C)"
            elif not fam and hex_:
                risultato = "✅ Mutazione C677T presente in omozigosi (T/T)"
            elif fam and hex_:
                risultato = "✅ Mutazione C677T presente in eterozigosi (C/T)"
            else:
                risultato = "❌ Test invalido (nessun segnale rilevato)"

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
