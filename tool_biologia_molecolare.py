import streamlit as st

st.title("Interpretazione risultati PCR - HPV / MST")

# Selezione del kit diagnostico
kit = st.radio("Seleziona il kit diagnostico:", ["HPV-geneprof", "MSTriplex-ABAnalitica"], index=None)

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

# Associazione kit → dizionario colori e lista colori validi
kit_color_map = {
    "HPV-geneprof": {
        "mapping": color_to_channel_hpv,
        "colori": list(color_to_channel_hpv.keys())
    },
    "MSTriplex-ABAnalitica": {
        "mapping": color_to_channel_mst,
        "colori": list(color_to_channel_mst.keys())
    }
}

if kit:
    colori_validi = kit_color_map[kit]["colori"]
    mapping = kit_color_map[kit]["mapping"]

    selezionati = st.multiselect("Seleziona i colori rilevati (puoi selezionarne più di uno):", colori_validi)

    if st.button("Interpreta risultato"):
        risultato = ""

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
