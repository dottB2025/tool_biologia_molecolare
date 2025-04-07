import streamlit as st

st.set_page_config(page_title="dr. Buonsanti - Tool Biologia Molecolare")
st.title("dr. Buonsanti - tool interpretativo test biologia molecolare")

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

    if st.button("Interpreta risultato"):
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
