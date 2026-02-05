import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67
SETTIMANA_LAVORATIVA = '1111110' 

FESTIVITA = [
    '2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', 
    '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26',
    '2026-01-01', '2026-01-06', '2026-04-06', '2026-04-25', '2026-05-01',
    '2026-06-02', '2026-08-15', '2026-11-01', '2026-12-08', '2026-12-25', '2026-12-26'
]

GUARDIE_GIURATE = [
    "ROSSINI LORENZO", "LAMADDALENA ANTONIO", "MILILLO GENNARO", 
    "BUFANO GIULIO", "LOBASCIO MICHELE", "RENNA GIUSEPPE", 
    "FIORE ANTONIO", "FAVIA ANTONIO"
]

st.set_page_config(page_title="Battistolli HR v16.2", layout="wide")

# --- FUNZIONE DI RIPARAZIONE DATABASE ---
def inizializza_e_ripara():
    # 1. Gestione Database Dipendenti
    if not os.path.exists(FILE_DIPENDENTI):
        dati_iniziali = [
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
        df_d = pd.DataFrame(dati_iniziali, columns=['Nome', 'Ferie', 'ROL'])
        df_d['Password'] = PASSWORD_STANDARD_DEFAULT
        df_d['Contratto'] = df_d['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
        df_d.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_d = pd.read_csv(FILE_DIPENDENTI)
        # Riparazione colonne mancanti (Fix KeyError)
        if 'Contratto' not in df_d.columns:
            df_d['Contratto'] = df_d['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
            df_d.to_csv(FILE_DIPENDENTI, index=False)
        if 'Password' not in df_d.columns:
            df_d['Password'] = PASSWORD_STANDARD_DEFAULT
            df_d.to_csv(FILE_DIPENDENTI, index=False)

    # 2. Gestione Database Ferie (Richieste)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note']).to_csv(FILE_FERIE, index=False)
    else:
        df_f = pd.read_csv(FILE_FERIE)
        # Riparazione colonna 'Risorsa' se mancante (Fix KeyError)
        if 'Risorsa' not in df_f.columns:
            df_f['Risorsa'] = 'Ferie' # Imposta default per i vecchi dati
            df_f.to_csv(FILE_FERIE, index=False)
            
    return pd.read_csv(FILE_DIPENDENTI)

df_dip = inizializza_e_ripara()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Battistolli HR")
    u_in = st.text_input("NOME COGNOME").upper().strip()
    p_in = st.text_input("Password", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        else:
            user_row = df_dip[df_dip['Nome'] == u_in]
            if not user_row.empty and str(user_row.iloc[0]['Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Dati non corretti.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header(f"👤 {st.session_state['user']}")
    if st.session_state["user"] != "admin":
        st.divider()
        npw = st.text_input("Nuova Password", type="password")
        if st.button("Aggiorna"):
            df_dip.loc[df_dip['Nome'] == st.session_state['user'], 'Password'] = npw
            df_dip.to_csv(FILE_DIPENDENTI, index=False); st.success("Salvata!")
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

# --- ADMIN ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Console Amministratore")
    t1, t2, t3 = st.tabs(["Registro Richieste", "Saldi Personale", "Sistema"])
    
    with t1:
        df_f = pd.read_csv(FILE_FERIE)
        st.dataframe(df_f, use_container_width=True)
        if not df_f.empty:
            rid = st.number_input("ID riga da eliminare", 0, len(df_f)-1, 0)
            if st.button("Elimina"):
                df_f.drop(df_f.index[rid]).to_csv(FILE_FERIE, index=False); st.rerun()

    with t2:
        df_f_all = pd.read_csv(FILE_FERIE)
        df_res = df_dip.copy()
        
        def calcola_residuo(row, tipo_r):
            # Filtro sicuro per evitare errori se il DB è vuoto
            usato = df_f_all[(df_f_all['Nome'] == row['Nome']) & (df_f_all['Risorsa'] == tipo_r)]['Ore'].sum()
            ore = round(row[tipo_r] - usato, 2)
            return f"{ore} h ({round(ore/6.67, 1)} gg)"
            
        df_res['Saldo_Ferie'] = df_res.apply(lambda r: calcola_residuo(r, 'Ferie'), axis=1)
        df_res['Saldo_ROL'] = df_res.apply(lambda r: calcola_residuo(r, 'ROL'), axis=1)
        
        st.dataframe(df_res[['Nome', 'Contratto', 'Saldo_Ferie', 'Saldo_ROL']], use_container_width=True)
        
        if st.button("➕ Applica Maturazione Mensile"):
            def m_proc(r):
                if r['Contratto'] == 'Guardia': r['Ferie'] += 14.67; r['ROL'] += 6.67
                else: r['Ferie'] += 12.23; r['ROL'] += 4.67
                return r
            df_dip = df_dip.apply(m_proc, axis=1)
            df_dip.to_csv(FILE_DIPENDENTI, index=False); st.rerun()

    with t3:
        if st.button("RESET ARCHIVIO FERIE"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note']).to_csv(FILE_FERIE, index=False); st.rerun()

# --- DIPENDENTE ---
else:
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    # Calcolo residui con protezione per file vuoti
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum() if not df_f.empty else 0
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum() if not df_f.empty else 0
    
    st.header(f"Bentornato {nome_u}")
    st.info(f"Contratto: {dati_u['Contratto']}")
    
    c1, c2 = st.columns(2)
    c1.metric("Ferie Rimaste", f"{round(dati_u['Ferie'] - usato_f, 2)} h")
    c2.metric("ROL Rimasti", f"{round(dati_u['ROL'] - usato_r, 2)} h")

    with st.form("invio"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Inizio"); al = st.date_input("Fine")
        
        if st.form_submit_button("INVIA"):
            conflitto = False
            lavorativi = 0
            # Trasformazione date per confronto
            df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
            df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
            
            for g in pd.date_range(da, al).date:
                if g.weekday() < 6 and g.strftime('%Y-%m-%d') not in FESTIVITA:
                    lavorativi += 1
                    count = len(df_f[(df_f['Inizio'] <= g) & (df_f['Fine'] >= g)])
                    if count >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        conflitto = True; st.error(f"Limite 3 assenze raggiunto per il {g}"); break
            
            if not conflitto:
                ore = round(lavorativi * ORE_GIORNATA, 2)
                nuova = pd.DataFrame([[nome_u, da, al
