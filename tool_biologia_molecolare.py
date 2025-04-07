import streamlit as st

st.title("Interpretazione risultati PCR - HPV / MST / HBV")

# Selezione del kit diagnostico
kit = st.radio("Seleziona il kit diagnostico:", ["HPV-geneprof", "MSTriplex-ABAnalitica", "HBV-geneprof"], index=None)

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

color_to_channel_hbv = {
    "GREEN": "FAM",
    "YELLOW": "HEX"
}

# Associazione kit → dizionario colori e lista colori validi
kit_color_map = {
    "HPV-geneprof": {
        "mapping": color_to_channel_hpv,
        "colori": list(color_to_channel_hpv.keys())
    },
    "MSTriplex-ABAnalitica": {
        "mapping": color_to_channel_mst,
        "colori": list(color_to_channel_mst.keys())
    },
    "HBV-geneprof": {
        "mapping": color_to_channel_hbv,
        "colori": list(color_to_channel_hbv.keys())
    }
}

# Stati per la sessione
if "show_hbv_quant" not in st.session_state:
    st.session_state.show_hbv_quant = False
if "hbv_result" not in st.session_state:
    st.session_state.hbv_result = ""

if kit:
    colori_validi = kit_color_map[kit]["colori"]
    mapping = kit_color_map[kit]["mapping"]

    selezionati = st.multiselect("Seleziona i colori rilevati (puoi selezionarne più di uno):", colori_validi)

    if st.button("Interpreta risultato"):
        risultato = ""
        st.session_state.show_hbv_quant = False

        if kit == "HPV-geneprof":
            canali = [mapping[c] for c in selezionati]
            fam = "FAM" in canali
            hex_ = "HEX" in canali
            cy5 = "Cy5" in canali
            texred = "TexRed/ROX" in canali
            quasar = "Cy5.5/Quasar 705" in canali

            if not fam and not hex_ and not cy5 and not texred and not quasar:
                risultato = "❌ Risultato: Non interpretabile (nessun canale rilevato)"
            elif not hex_:
                risultato = "❌ Test invalido (controllo interno assente)"
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
            elif not fam and hex_:
                risultato = "✅ Test valido - HPV non rilevato"
            else:
                risultato = "⚠️ Caso non previsto - controlla i canali inseriti"
            st.markdown("### Risultato")
            st.info(risultato)

        elif kit == "MSTriplex-ABAnalitica":
            canali = [mapping[c] for c in selezionati if c in mapping]
            bg = "BG" in canali

            if not bg:
                risultato = "❌ Test invalido (controllo interno assente)"
            else:
                esiti = []
                if "CT" in canali:
                    esiti.append("✅ Chlamydia trachomatis (CT): positivo")
                else:
                    esiti.append("❌ Chlamydia trachomatis (CT): non rilevato")

                if "NG" in canali:
                    esiti.append("✅ Neisseria gonorrhoeae (NG): positivo")
                else:
                    esiti.append("❌ Neisseria gonorrhoeae (NG): non rilevato")

                if "MG" in canali:
                    esiti.append("✅ Mycoplasma genitalium (MG): positivo")
                else:
                    esiti.append("❌ Mycoplasma genitalium (MG): non rilevato")

                risultato = "\n".join(esiti)
            st.markdown("### Risultato")
            st.info(risultato)

        elif kit == "HBV-geneprof":
            canali = [mapping[c] for c in selezionati if c in mapping]
            fam = "FAM" in canali
            hex_ = "HEX" in canali

            if not fam and not hex_:
                st.session_state.hbv_result = "❌ Test invalido (controllo interno assente)"
            elif fam and hex_:
                st.session_state.hbv_result = "✅ Test valido - HBV positivo"
                st.session_state.show_hbv_quant = True
            elif not fam and hex_:
                st.session_state.hbv_result = "✅ Test valido - HBV non rilevato"
            else:
                st.session_state.hbv_result = "⚠️ Caso non previsto - controlla i canali inseriti"
            st.markdown("### Risultato")
            st.info(st.session_state.hbv_result)

if st.session_state.show_hbv_quant:
    st.markdown("### Inserisci i dati per la quantificazione (IU/ml)")
    with st.form("quantificazione"):
        sc = st.number_input("SC (concentrazione del campione in UI/µl)", min_value=0.0, format="%.2f")
        ev = st.number_input("EV (volume di eluizione in µl)", min_value=0.0, format="%.2f")
        iv = st.number_input("IV (volume di isolamento in ml)", min_value=0.0, format="%.2f")
        calcola = st.form_submit_button("Calcola concentrazione")

        if calcola:
            if sc > 0 and ev > 0 and iv > 0:
                concentrazione = (sc * ev) / iv
                st.success(f"Concentrazione campione: {concentrazione:.2f} UI/ml")
            else:
                st.warning("Inserire tutti i valori per calcolare la concentrazione.")
