import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- 1. CONFIGURAZIONE INTEGRALE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67

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

st.set_page_config(page_title="Battistolli HR Portal v19.0", layout="wide")

# --- 2. INIZIALIZZAZIONE DATABASE (Tabula Rasa Selettiva) ---
def inizializza_sistema():
    nomi_e_saldi = [
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

    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(nomi_e_saldi, columns=['Nome', 'Ferie', 'ROL'])
        df['Password'] = PASSWORD_DEFAULT
        df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note']).to_csv(FILE_FERIE, index=False)

inizializza_sistema()
df_dip = pd.read_csv(FILE_DIPENDENTI)
df_ferie = pd.read_csv(FILE_FERIE)

# --- 3. LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale HR Battistolli")
    u_in = st.text_input("NOME COGNOME").upper().strip()
    p_in = st.text_input("Password", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            idx = df_dip.index[df_dip['Nome'] == u_in][0]
            if str(df_dip.at[idx, 'Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Password errata.")
        else: st.error("Utente non censito.")
    st.stop()

# --- 4. AREA AMMINISTRATORE ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Pannello Admin")
    t1, t2, t3 = st.tabs(["Saldi & CCNL", "Richieste Ricevute", "Manutenzione"])
    
    with t1:
        # Calcolo dinamico saldi sottraendo le richieste dal database ferie
        df_calcolo = df_dip.copy()
        def get_saldo(nome, colonna):
            usato = df_ferie[(df_ferie['Nome'] == nome) & (df_ferie['Risorsa'] == colonna)]['Ore'].sum()
            return round(df_calcolo.loc[df_calcolo['Nome'] == nome, colonna].values[0] - usato, 2)
        
        df_calcolo['Saldo_Ferie'] = df_calcolo['Nome'].apply(lambda x: get_saldo(x, 'Ferie'))
        df_calcolo['Saldo_ROL'] = df_calcolo['Nome'].apply(lambda x: get_saldo(x, 'ROL'))
        st.dataframe(df_calcolo[['Nome', 'Contratto', 'Saldo_Ferie', 'Saldo_ROL']], use_container_width=True)
        
        if st.button("➕ APPLICA MATURAZIONE MENSILE"):
            # Regola CCNL: Guardie +14.67/6.67, Fiduciari +12.23/4.67
            df_dip['Ferie'] = df_dip.apply(lambda x: x['Ferie'] + (14.67 if x['Contratto']=='Guardia' else 12.23), axis=1)
            df_dip['ROL'] = df_dip.apply(lambda x: x['ROL'] + (6.67 if x['Contratto']=='Guardia' else 4.67), axis=1)
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Maturazione applicata correttamente!"); time.sleep(1); st.rerun()

    with t2:
        st.dataframe(df_ferie, use_container_width=True)
        if not df_ferie.empty:
            del_idx = st.number_input("Riga da eliminare", 0, len(df_ferie)-1, 0)
            if st.button("ELIMINA RIGA"):
                df_ferie.drop(df_ferie.index[del_idx]).to_csv(FILE_FERIE, index=False)
                st.rerun()

    with t3:
        if st.button("RESET TOTALE FERIE"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note']).to_csv(FILE_FERIE, index=False)
            st.rerun()

# --- 5. AREA DIPENDENTE (Con blocco 3 persone) ---
else:
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    
    # Calcolo residui correnti
    f_usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Risorsa'] == 'Ferie')]['Ore'].sum()
    r_usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Risorsa'] == 'ROL')]['Ore'].sum()
    s_f = round(dati_u['Ferie'] - f_usate, 2)
    s_r = round(dati_u['ROL'] - r_usate, 2)

    st.header(f"Ciao {nome_u}")
    st.info(f"Contratto: CCNL {dati_u['Contratto']}")
    c1, c2 = st.columns(2)
    c1.metric("Ferie Residue", f"{s_f} h")
    c2.metric("ROL Residui", f"{s_r} h")

    with st.form("richiesta_ferie"):
        st.subheader("Invia Nuova Richiesta")
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Dalla data")
        al = st.date_input("Alla data")
        note = st.text_input("Note opzionali")
        
        if st.form_submit_button("INVIA"):
            conflitto = False
            giorni_lavorativi = 0
            # Analisi giorno per giorno
            for giorno in pd.date_range(da, al).date:
                data_str = giorno.strftime('%Y-%m-%d')
                
                # Regola: Sabato SI, Domenica NO, Festività NO
                if giorno.weekday() < 6 and data_str not in FESTIVITA:
                    giorni_lavorativi += 1
                    
                    # --- FUNZIONE BLOCCO 3 PERSONE ---
                    # Conta quante persone hanno già prenotato quel giorno
                    # (Si controllano tutte le richieste che coprono quel giorno)
                    df_ferie['Inizio'] = pd.to_datetime(df_ferie['Inizio']).dt.date
                    df_ferie['Fine'] = pd.to_datetime(df_ferie['Fine']).dt.date
                    
                    occupati = len(df_ferie[
                        (df_ferie['Inizio'] <= giorno) & 
                        (df_ferie['Fine'] >= giorno) & 
                        (~df_ferie['Tipo'].isin(["104", "Donazione Sangue"])) # Queste non bloccano
                    ])
                    
                    if occupati >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        conflitto = True
                        st.error(f"Spiacente, per il giorno {giorno} ci sono già 3 persone assenti.")
                        break
            
            if not conflitto and giorni_lavorativi > 0:
                ore_totali = round(giorni_lavorativi * ORE_GIORNATA, 2)
                nuova_r = pd.DataFrame([[nome_u, da, al, tipo, risorsa, ore_totali, note]], 
                                     columns=['Nome','Inizio','Fine','Tipo','Risorsa','Ore','Note'])
                nuova_r.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success(f"Richiesta salvata! Scalate {ore_totali} ore per {giorni_lavorativi} giorni lavorativi.")
                time.sleep(1.5); st.rerun()

# --- SIDEBAR (Cambio Password) ---
with st.sidebar:
    st.divider()
    if st.session_state["user"] != "admin":
        new_pw = st.text_input("Cambia Password", type="password")
        if st.button("SALVA PASSWORD"):
            df_dip.loc[df_dip['Nome'] == st.session_state['user'], 'Password'] = new_pw
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Password aggiornata!")
    if st.button("LOGOUT"):
        del st.session_state["user"]; st.rerun()
