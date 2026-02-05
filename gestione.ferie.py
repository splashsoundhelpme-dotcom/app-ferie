import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE RIGIDA ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67

FESTIVITA = [
    '2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', 
    '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26',
    '2026-01-01', '2026-01-06', '2026-04-06', '2026-04-25', '2026-05-01',
    '2026-06-02', '2026-08-15', '2026-11-01', '2026-12-08', '2026-12-25', '2026-12-26'
]

GUARDIE_GIURATE = ["ROSSINI LORENZO", "LAMADDALENA ANTONIO", "MILILLO GENNARO", "BUFANO GIULIO", "LOBASCIO MICHELE", "RENNA GIUSEPPE", "FIORE ANTONIO", "FAVIA ANTONIO"]

st.set_page_config(page_title="Battistolli HR v18.0", layout="wide")

# --- FUNZIONE DI AUTO-RIPARAZIONE (Risolve i KeyError delle tue immagini) ---
def inizializza_e_pulisci():
    dati_base = [
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

    # Controllo e riparazione DB Dipendenti
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_base, columns=['Nome', 'Ferie', 'ROL'])
        df['Password'] = PASSWORD_STANDARD_DEFAULT
        df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
        df.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df = pd.read_csv(FILE_DIPENDENTI)
        if 'Contratto' not in df.columns: # FIX per Immagine 4
            df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
            df.to_csv(FILE_DIPENDENTI, index=False)

    # Controllo e riparazione DB Ferie
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note']).to_csv(FILE_FERIE, index=False)
    else:
        df_f = pd.read_csv(FILE_FERIE)
        if 'Risorsa' not in df_f.columns: # FIX per Immagine 1
            df_f['Risorsa'] = 'Ferie'
            df_f.to_csv(FILE_FERIE, index=False)

    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = inizializza_e_pulisci()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale Battistolli HR")
    u = st.text_input("NOME COGNOME").upper().strip()
    p = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u == "ADMIN" and p == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u in df_dip['Nome'].values:
            idx = df_dip.index[df_dip['Nome'] == u][0]
            if str(df_dip.at[idx, 'Password']) == p:
                st.session_state["user"] = u; st.rerun()
            else: st.error("Password errata")
        else: st.error("Utente non trovato")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Loggato come: **{st.session_state['user']}**")
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

# --- ADMIN ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Console Amministrazione")
    t1, t2 = st.tabs(["Situazione Saldi", "Registro Richieste"])
    
    with t1:
        # Calcolo residui protetto da errori
        df_f_all = pd.read_csv(FILE_FERIE)
        res_list = []
        for _, r in df_dip.iterrows():
            f_u = df_f_all[(df_f_all['Nome'] == r['Nome']) & (df_f_all['Risorsa'] == 'Ferie')]['Ore'].sum()
            r_u = df_f_all[(df_f_all['Nome'] == r['Nome']) & (df_f_all['Risorsa'] == 'ROL')]['Ore'].sum()
            res_list.append([r['Nome'], r['Contratto'], round(r['Ferie']-f_u, 2), round(r['ROL']-r_u, 2)])
        
        st.dataframe(pd.DataFrame(res_list, columns=['Nome','Contratto','Ferie Res','ROL Res']), use_container_width=True)
        
        if st.button("➕ Applica Maturazione"):
            df_dip['Ferie'] = df_dip.apply(lambda x: x['Ferie']+14.67 if x['Contratto']=='Guardia' else x['Ferie']+12.23, axis=1)
            df_dip['ROL'] = df_dip.apply(lambda x: x['ROL']+6.67 if x['Contratto']=='Guardia' else x['ROL']+4.67, axis=1)
            df_dip.to_csv(FILE_DIPENDENTI, index=False); st.rerun()

    with t2:
        df_f_reg = pd.read_csv(FILE_FERIE)
        st.dataframe(df_f_reg, use_container_width=True)
        if st.button("Svuota Archivio"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note']).to_csv(FILE_FERIE, index=False); st.rerun()

# --- DIPENDENTE ---
else:
    nome = st.session_state["user"]
    dati = df_dip[df_dip['Nome'] == nome].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    f_u = df_f[(df_f['Nome'] == nome) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    r_u = df_f[(df_f['Nome'] == nome) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    st.header(f"Area Personale: {nome}")
    st.metric("Saldo Ferie (Ore)", round(dati['Ferie']-f_u, 2))
    st.metric("Saldo ROL (Ore)", round(dati['ROL']-r_u, 2))

    with st.form("invio"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        scelta = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        
        if st.form_submit_button("INVIA"):
            lavorativi = 0
            df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
            df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
            
            for g in pd.date_range(da, al).date:
                if g.weekday() < 6 and g.strftime('%Y-%m-%d') not in FESTIVITA:
                    lavorativi += 1
            
            ore = round(lavorativi * ORE_GIORNATA, 2)
            # FIX SyntaxError Immagine 3: parentesi e quadre chiuse correttamente
            nuova = pd.DataFrame([[nome, da, al, tipo, scelta, ore, ""]], columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note'])
            nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
            st.success("Inviata!"); time.sleep(1); st.rerun()
