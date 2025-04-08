import streamlit as st
import math

st.set_page_config(page_title="dr. Buonsanti - Tool Biologia Molecolare")
st.title("dr. Buonsanti - tool interpretativo test biologia molecolare")

kit = st.radio("Seleziona il kit diagnostico:", [
    "HPV-geneprof",
    "MSTriplex-ABAnalitica",
    "HBV-geneprof",
    "HCV-geneprof",
    "MTHFR-C677T",
    "MTHFR-A1298C",
    "BV-NLM"
], index=None)

kit_color_map = {
    "HPV-geneprof": {"mapping": {"GREEN": "FAM", "YELLOW": "HEX", "ORANGE": "ROX", "RED": "Cy5", "CRIMSON": "Quasar 705"}},
    "MSTriplex-ABAnalitica": {"mapping": {"GREEN": "FAM", "YELLOW": "HEX", "RED": "Cy5", "ORANGE": "ROX"}},
    "HBV-geneprof": {"mapping": {"GREEN": "FAM", "YELLOW": "HEX"}},
    "HCV-geneprof": {"mapping": {"GREEN": "FAM", "YELLOW": "HEX"}},
    "MTHFR-C677T": {"mapping": {"GREEN": "FAM", "YELLOW": "HEX"}},
    "MTHFR-A1298C": {"mapping": {"GREEN": "FAM", "YELLOW": "HEX"}}
}

for k in kit_color_map:
    kit_color_map[k]["colori"] = list(kit_color_map[k]["mapping"].keys())

if kit == "BV-NLM":
    st.markdown("### Inserisci le copie/ml")
    batteri_totali = st.number_input("Batteri totali (canale RED)", min_value=0.0)
    lattobacilli = st.number_input("Lattobacilli (canale ORANGE)", min_value=0.0)
    atopobium = st.number_input("Atopobium vaginae (canale YELLOW)", min_value=0.0)
    gardnerella = st.number_input("Gardnerella vaginalis (canale GREEN)", min_value=0.0)

    st.markdown("### Inserisci i valori di CT")
    ct_red = st.number_input("CT Batteri totali (RED)", min_value=0.0)
    ct_orange = st.number_input("CT Lattobacilli (ORANGE)", min_value=0.0)
    ct_yellow = st.number_input("CT Atopobium (YELLOW)", min_value=0.0)
    ct_green = st.number_input("CT Gardnerella (GREEN)", min_value=0.0)

    if st.button("Interpreta risultato"):
        presenza_gardnerella = ct_green < 35 and ct_green != 0.00
        presenza_atopobium = ct_yellow < 35 and ct_yellow != 0.00

        presenza_text = []
        if presenza_gardnerella:
            presenza_text.append("✅ Presenza di Gardnerella")
        if presenza_atopobium:
            presenza_text.append("✅ Presenza di Atopobium")

        atopobium = 1 if atopobium == 0 else atopobium
        gardnerella = 1 if gardnerella == 0 else gardnerella

        kc1 = kc2 = kc3 = None
        vaginosi = ""
        flora_perc = ""

        if batteri_totali < 1e5:
            vaginosi = "❌ Carica batterica insufficiente per l'analisi"
        else:
            try:
                gvav = gardnerella + atopobium
                kc1 = math.log10(lattobacilli) - math.log10(gvav)
                kc2 = math.log10(batteri_totali) - math.log10(lattobacilli)
                kc3 = math.log10(batteri_totali) - math.log10(gvav)

                if kc2 > 1 and kc3 > 2:
                    vaginosi = "⚠️ Alterazioni della flora di eziologia ignota"
                elif kc1 < 0.5:
                    vaginosi = "🟥 Presenza di vaginosi batterica"
                elif kc1 > 1:
                    vaginosi = "🟩 Assenza di vaginosi batterica"
                else:
                    vaginosi = "🟧 Flora vaginale intermedia"
            except:
                vaginosi = "⚠️ Errore nel calcolo dei logaritmi"

        if lattobacilli > batteri_totali:
            flora_perc = "% lattobacillare non calcolabile"
        elif batteri_totali > 0:
            perc = round((lattobacilli / batteri_totali) * 100)
            flora_perc = f"% lattobacillare: {perc}%"

        st.markdown("### Risultato")
        if presenza_text:
            st.markdown("\n".join(presenza_text))
        st.markdown(vaginosi)
        st.markdown(flora_perc)

elif kit in kit_color_map:
    colori_validi = kit_color_map[kit]["colori"]
    mapping = kit_color_map[kit]["mapping"]
    selezionati = st.multiselect("Seleziona i colori rilevati (puoi selezionarne più di uno):", colori_validi)

    if st.button("Interpreta risultato"):
        risultato = ""
        canali = [mapping[c] for c in selezionati if c in mapping]

        if kit == "HPV-geneprof":
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
            bg = "ROX" in canali
            if not bg:
                risultato = "❌ Test invalido (controllo interno assente)"
            else:
                risultato = "\n" + "\n".join([
                    f"❌ {label}: rilevato" if probe in canali else f"✅ {label}: non rilevato"
                    for probe, label in zip(
                        ["FAM", "HEX", "Cy5"],
                        ["Chlamydia trachomatis (CT)", "Neisseria gonorrhoeae (NG)", "Mycoplasma genitalium (MG)"]
                    )
                ])

        elif kit in ["HBV-geneprof", "HCV-geneprof"]:
            fam = "FAM" in canali
            hex_ = "HEX" in canali

            if not fam and not hex_:
                st.session_state.show_quant = False
                risultato = "❌ Test invalido (controllo interno assente)"

            elif fam:
                st.session_state.show_quant = True
                risultato = f"✅ Test valido - {kit[:3]} positivo"

            else:
                st.session_state.show_quant = False
                risultato = f"✅ Test valido - {kit[:3]} non rilevato"f"✅ Test valido - {kit[:3]} positivo"
            else:
                st.session_state.show_quant = False
                risultato = f"✅ Test valido - {kit[:3]} non rilevato""❌ Test invalido (controllo interno assente)"
                st.session_state.show_quant = False
            elif fam:
                risultato = f"✅ Test valido - {kit[:3]} positivo"
                st.session_state.show_quant = True
            else:
                risultato = f"✅ Test valido - {kit[:3]} non rilevato"
                st.session_state.show_quant = False"❌ Test invalido (controllo interno assente)"
            elif fam:
                risultato = f"✅ Test valido - {kit[:3]} positivo"
                st.session_state.show_quant = True
            else:
                risultato = f"✅ Test valido - {kit[:3]} non rilevato"

        elif kit in ["MTHFR-C677T", "MTHFR-A1298C"]:
            fam = "FAM" in canali
            hex_ = "HEX" in canali
            if fam and not hex_:
                risultato = "🟩 Omozigote wild-type (C/C)"
            elif fam and hex_:
                risultato = "🟧 Eterozigote (C/T)"
            elif not fam and hex_:
                risultato = "🟥 Omozigote mutato (T/T)"
            else:
                risultato = "❌ Test invalido (nessun segnale rilevato)"

        st.markdown("### Risultato")
        st.markdown(risultato.replace('\n', '<br>'), unsafe_allow_html=True)
