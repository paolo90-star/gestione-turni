import streamlit as st 
import pandas as pd 
import random 
from report lab.platibus import SimpleDocTemplate, Table, TableStyle 
from reportlab.lib import Colors

st.set_page_config(layout="wide")

===================== CONFIG DINAMICA =====================

st.sidebar.header("⚙️ Configurazione")

Persone modificabili

people_input = st.sidebar.text_area( "Persone (una per riga)", value="Paolo\nMarco\nGianfranco\nClaudio\nCarmelo" ) people = [p.strip() for p in people_input.split("\n") if p.strip()]

Senior modificabili

senior_input = st.sidebar.text_input( "Senior (separati da virgola)", value="Paolo,Gianfranco,Carmelo" ) senior = {s.strip() for s in senior_input.split(",") if s.strip()}

Orari modificabili

m_time = st.sidebar.text_input("Orario Mattina", "08:00-15:10") p_time = st.sidebar.text_input("Orario Pomeriggio", "11:00-18:10")

Giorni

custom_days = st.sidebar.text_input( "Giorni (separati da virgola)", value="Lun,Mar,Mer,Gio,Ven,Sab,Dom" ) days = [d.strip() for d in custom_days.split(",") if d.strip()]

COLOR_MAP = {"M": "🟢", "P": "🔵", "R": "🔴", "": "➖"}

st.title("📅 Gestione Turni (Dinamica)") st.caption(f"Mattina: {m_time} | Pomeriggio: {p_time}")

===================== STATO =====================

key_df = f"df_{len(people)}_{len(days)}" if key_df not in st.session_state: st.session_state[key_df] = pd.DataFrame("", index=people, columns=days)

df = st.session_state[key_df]

Se cambiano persone/giorni, riallinea

if list(df.index) != people or list(df.columns) != days: df = pd.DataFrame("", index=people, columns=days) st.session_state[key_df] = df

===================== INPUT =====================

shift = st.radio("Seleziona turno:", ["M", "P", "R"], horizontal=True)

st.markdown("---")

===================== AUTO GENERAZIONE =====================

if st.button("🤖 Genera Turni Automatici"): new_df = pd.DataFrame("R", index=people, columns=days)

for day in days:
    # assicurati che ci siano senior validi
    valid_senior = [p for p in people if p in senior]
    if not valid_senior:
        st.error("Nessun senior valido definito")
        break

    s_m = random.choice(valid_senior)
    s_p = random.choice(valid_senior)

    new_df.loc[s_m, day] = "M"
    new_df.loc[s_p, day] = "P"

    others = [p for p in people if p not in [s_m, s_p]]
    random.shuffle(others)

    if others:
        new_df.loc[others[0], day] = "M"
    if len(others) > 1:
        new_df.loc[others[1], day] = "P"

st.session_state[key_df] = new_df
df = new_df
st.success("Turni generati automaticamente!")

===================== GRIGLIA =====================

for person in people: st.write(f"{person}") cols = st.columns(len(days)) for i, day in enumerate(days): val = df.loc[person, day] display = COLOR_MAP[val] if cols[i].button(display, key=f"{person}-{day}"): df.loc[person, day] = shift

st.markdown("---")

===================== TABELLA =====================

st.dataframe(df)

===================== VINCOLI =====================

if st.button("✅ Verifica Vincoli Senior"): problemi = [] for day in days: mattina_ok = False pomeriggio_ok = False for person in people: val = df.loc[person, day] if person in senior: if val == "M": mattina_ok = True if val == "P": pomeriggio_ok = True if not mattina_ok: problemi.append(f"{day}: manca senior mattina") if not pomeriggio_ok: problemi.append(f"{day}: manca senior pomeriggio")

if problemi:
    st.error("\n".join(problemi))
else:
    st.success("Tutti i vincoli rispettati!")

===================== EXPORT =====================

csv = df.to_csv().encode('utf-8') st.download_button("💾 Scarica CSV", csv, "turni.csv", "text/csv")

if st.button("📄 Esporta PDF"): file_path = "/tmp/turni.pdf" doc = SimpleDocTemplate(file_path)

table_data = [["Nome"] + days]
for person in people:
    row = [person] + list(df.loc[person])
    table_data.append(row)

table = Table(table_data)
table.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('TEXTCOLOR',(0,0),(-1,0),colors.white)
]))

doc.build([table])

with open(file_path, "rb") as f:
    st.download_button("⬇️ Scarica PDF", f, "turni.pdf")

st.markdown("---") st.info("Suggerimento: modifica tutto dalla sidebar (persone, senior, giorni, orari).")
