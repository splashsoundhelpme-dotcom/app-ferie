import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import time

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67

# Festività Nazionali 2025-2026 (Non scalano ore dal saldo)
FESTIVITA = [
    '2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', 
    '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26',
    '2026-01-01', '2026-01-06', '2026-04-06', '2026-04-25', '2026-05-01',
    '2026-06-02', '2026-08-15', '2026-11-01', '2026-12-08', '2026-12-25', '2026-12-26'
]

# Elenco specifico Guardie Giurate
GG_LIST = ["ROSSINI LORENZO", "LAMADDALENA ANTONIO", "MILILLO GENNARO", "BUFANO GIULIO", "LOBASCIO MICHELE", "RENNA GIUSEPPE", "FIORE ANTONIO", "FAVIA ANTONIO"]

st.set_page_config(page_title="Battistolli HR Portal v17.5", layout="wide")

# --- DATABASE ENGINE ---
def load_data():
    if not os.path.exists(FILE_DIPENDENTI):
        nomi = [
            ["ABBATICCHIO ANTONIO", 53.13, 11.24], ["ACQUAVIVA ANNALISA", 126.40, 72.63],
            ["ANTONACCI MARIO", 146.92, 43.98], ["BERGAMASCO COSIMO DAMIANO", 186.60, 47.81],
            ["BOTTALICO LEONARDO", 133.42, 9.33], ["BOZZI RAFFAELLA", 258.08, 106.60],
            ["BUFANO GIULIO", 11.12, 0.0], ["BUQUICCHIO ANGELA", 259.03, 48.65],
            ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95], ["CAMPANILE DENNIS", 92.73, 47.85],
            ["CARBONE ROBERTA", 66.64, 47.20], ["CISTERNINO BENITO", 93.14, -19.35],
            ["DE NAPOLI SERENA", 26.49, 115.55], ["DI BARI GIORGIA", 112.76, 54.03],
            ["DILISO CLARA ANNARITA", 152.13, 44.23], ["FIORE ANTONIO", 39.56, 0.0],
            ["GIANNINI CAMILLA", 135.33, 85.08], ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18],
            ["LAMADDALENA ANTONIO", 47.32, 0.0], ["MANGIONE FRANCESCO", 200.25, 43.98],
            ["MASTRONARDI ANNA GUENDALINA", 100.92, 27.15], ["MILILLO GENNARO", 32.60, 0.0],
            ["MOSCA SIMONA", 166.51, 47.68], ["PALERMO DOMENICO", 167.08, 48.01],
            ["PALTERA CRISTINA", 227.03, 48.65], ["PORCARO NICOLA", 3.10, 0.64],
            ["PRIAMI LUCA", 33.00, 60.64], ["RAFASCHIERI ANNA ILENIA", 117.30, 32.73],
            ["RENNA GIUSEPPE", 14.81, 0.0], ["SANO' MORENA", 39.81, 24.00],
            ["SISTO FEDERICA", 193.91, 50.65], ["TANGARI FRANCESCO", -39.85, 6.91],
            ["TRENTADUE ANNARITA", 65.95, 47.20], ["VISTA NICOLA", 207.03, 45.60],
            ["ZIFARELLI ROBERTA", 72.96, 44.11], ["CINQUEPALMI NICOLANTONIO", 53.69, 30.83],
            ["DI RELLA COSIMO DAMIANO", 15.34, 29.01], ["FUCCI LUCIA", 59.39, 26.15],
            ["MARTINO ALESSANDRO", 79.83, 21.12], ["MENGA LEONARDO", 174.00, 16.00],
            ["RANA DONATO", 146.41, 30.98], ["GENTILE SAVERIO", 202.77, 25.62],
            ["LOBASCIO MICHELE", 34.04, 0.0], ["ROSSINI LORENZO", 6.40, 0.0],
            ["FAVIA ANTONIO", 0.0, 0.0]
        ]
        df = pd.DataFrame(nomi, columns=['Nome', 'Ferie', 'ROL'])
        df['Password'] = PASSWORD_STANDARD_DEFAULT
        df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GG_LIST else 'Fiduciario')
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore']).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = load_data()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale HR")
    u = st.text_input("NOME COGNOME").upper().strip()
    p = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if u == "ADMIN" and p == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u in df_dip['Nome'].values:
            if str(df_dip[df_dip['Nome']==u]['Password'].values[0]) == p:
                st.session_state["user"] = u; st.rerun()
        else: st.error("Dati errati")
    st.stop()

# --- INTERFACCIA ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

# --- LOGICA ADMIN ---
if st.session_state["user"] == "admin":
    st.header("👨‍💼 Console Amministrazione")
    tab1, tab2 = st.tabs(["Saldi Attuali", "Registro Richieste"])
    
    with tab1:
        res = []
        for _, r in df_dip.iterrows():
            f_u = df_ferie[(df_ferie['Nome']==r['Nome']) & (df_ferie['Risorsa']=='Ferie')]['Ore'].sum()
            r_u = df_ferie[(df_ferie['Nome']==r['Nome']) & (df_ferie['Risorsa']=='ROL')]['Ore'].sum()
            res.append([r['Nome'], r['Contratto'], round(r['Ferie']-f_u, 2), round(r['ROL']-r_u, 2)])
        st.dataframe(pd.DataFrame(res, columns=['Nome','Contratto','Ferie (h)','ROL (h)']), use_container_width=True)
        
        if st.button("➕ Applica Maturazione Mensile"):
            df_dip['Ferie'] = df_dip.apply(lambda x: x['Ferie']+14.67 if x['Contratto']=='Guardia' else x['Ferie']+12.23, axis=1)
            df_dip['ROL'] = df_dip.apply(lambda x: x['ROL']+6.67 if x['Contratto']=='Guardia' else x['ROL']+4.67, axis=1)
            df_dip.to_csv(FILE_DIPENDENTI, index=False); st.success("Fatto!"); time.sleep(1); st.rerun()

    with tab2:
        st.dataframe(df_ferie, use_container_width=True)
        if st.button("Svuota Registro"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore']).to_csv(FILE_FERIE, index=False); st.rerun()

# --- LOGICA DIPENDENTE ---
else:
    nome = st.session_state["user"]
    row = df_dip[df_dip['Nome']==nome].iloc[0]
    f_u = df_ferie[(df_ferie['Nome']==nome) & (df_ferie['Risorsa']=='Ferie')]['Ore'].sum()
    r_u = df_ferie[(df_ferie['Nome']==nome) & (df_ferie['Risorsa']=='ROL')]['Ore'].sum()
    
    st.header(f"Ciao {nome}")
    st.caption(f"CCNL: {row['Contratto']}")
    c1, c2 = st.columns(2)
    c1.metric("Ferie Residue (h)", round(row['Ferie']-f_u, 2))
    c2.metric("ROL Residui (h)", round(row['ROL']-r_u, 2))

    with st.form("richiesta"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        scalo = st.radio("Da scalare su:", ["Ferie", "ROL"])
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        
        if st.form_submit_button("INVIA"):
            lavorativi = 0
            bloccato = False
            for d in pd.date_range(da, al).date:
                # Sabato incluso (weekday < 6), Domenica esclusa, Festività escluse
                if d.weekday() < 6 and d.strftime('%Y-%m-%d') not in FESTIVITA:
                    lavorativi += 1
                    count = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= d) & (pd.to_datetime(df_ferie['Fine']).dt.date >= d)])
                    if count >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        bloccato = True; st.error(f"Posti esauriti per il giorno {d}"); break
            
            if not bloccato and lavorativi > 0:
                ore = round(lavorativi * ORE_GIORNATA, 2)
                nuova = pd.DataFrame([[nome, da, al, tipo, scalo, ore]], columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore'])
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success("Richiesta registrata!"); time.sleep(1); st.rerun()
