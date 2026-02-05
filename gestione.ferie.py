import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- COSTANTI E CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67
COLONNE_FERIE = ['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']

st.set_page_config(page_title="Battistolli HR Portal v6.0", layout="wide")

# --- DATABASE INTEGRALE (44 DIPENDENTI DAL TUO TESTO) ---
def inizializza_sistema():
    dati = [
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
        ["DI RELLA COSIMO DAMIANO", 153.41, 29.01], ["FUCCI LUCIA", 59.39, 26.15],
        ["MARTINO ALESSANDRO", 79.83, 21.12], ["MENGA LEONARDO", 174.00, 16.00],
        ["RANA DONATO", 146.41, 30.98], ["GENTILE SAVERIO", 202.77, 25.62],
        ["LOBASCIO MICHELE", 34.04, 0.0], ["ROSSINI LORENZO", 6.40, 0.0]
    ]
    df = pd.DataFrame(dati, columns=['Nome', 'Ferie', 'ROL'])
    df['Password'] = PASSWORD_STANDARD
    df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=COLONNE_FERIE).to_csv(FILE_FERIE, index=False)
    return df

# --- CARICAMENTO SICURO ---
def carica_ferie():
    try:
        df = pd.read_csv(FILE_FERIE)
        if df.empty or 'Ore' not in df.columns:
            return pd.DataFrame(columns=COLONNE_FERIE)
        return df
    except:
        return pd.DataFrame(columns=COLONNE_FERIE)

df_dip = inizializza_sistema()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale HR")
    u_input = st.text_input("NOME COGNOME").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        else:
            match = df_dip[df_dip['Nome'] == u_input]
            if not match.empty and p_input == PASSWORD_STANDARD:
                st.session_state["user"] = u_input; st.rerun()
            else:
                st.error("Credenziali errate.")
    st.stop()

# --- INTERFACCIA ---
with st.sidebar:
    st.info(f"Utente: {st.session_state['user']}")
    if st.button("Logout"):
        del st.session_state["user"]; st.rerun()

# --- LOGICA ADMIN ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Pannello di Controllo Amministratore")
    tab1, tab2, tab3 = st.tabs(["Registro Richieste", "Saldi Personale", "Gestione Database"])
    
    with tab1:
        df_f = carica_ferie()
        st.dataframe(df_f, use_container_width=True)
        if not df_f.empty:
            st.divider()
            idx = st.number_input("Seleziona ID riga da eliminare", 0, len(df_f)-1, 0)
            if st.button("Cancella Richiesta Selezionata"):
                df_f.drop(df_f.index[idx]).to_csv(FILE_FERIE, index=False)
                st.success("Richiesta eliminata."); time.sleep(1); st.rerun()

    with tab2:
        df_f_all = carica_ferie()
        df_res = df_dip.copy()
        def calcola_res(row, t):
            u = df_f_all[(df_f_all['Nome'] == row['Nome']) & (df_f_all['Risorsa'] == t)]['Ore'].sum()
            return round(row[t] - u, 2)
        df_res['Ferie_R'] = df_res.apply(lambda r: calcola_res(r, 'Ferie'), axis=1)
        df_res['ROL_R'] = df_res.apply(lambda r: calcola_res(r, 'ROL'), axis=1)
        st.dataframe(df_res[['Nome', 'Ferie_R', 'ROL_R']], use_container_width=True)
        st.download_button("Scarica CSV per Ufficio", df_res.to_csv(index=False).encode('utf-8'), "report_ore.csv")

    with tab3:
        if st.button("⚠️ RESET TOTALE RICHIESTE"):
            pd.DataFrame(columns=COLONNE_FERIE).to_csv(FILE_FERIE, index=False); st.rerun()

# --- LOGICA DIPENDENTE ---
else:
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = carica_ferie()
    
    # Calcolo residui istantaneo
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    st.header(f"Benvenuto {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("Saldo Ferie", f"{round(dati_u['Ferie'] - usato_f, 2)} h")
    c2.metric("Saldo ROL", f"{round(dati_u['ROL'] - usato_r, 2)} h")

    with st.form("nuova_richiesta"):
        st.subheader("Richiedi Assenza")
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        
        if st.form_submit_button("INVIA"):
            # Controllo limite 3 persone
            conflitto = False
            if not df_f.empty:
                df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
                df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
                for g in pd.date_range(da, al).date:
                    count = len(df_f[(df_f['Inizio'] <= g) & (df_f['Fine'] >= g)])
                    if count >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        conflitto = True
                        st.error(f"Posti esauriti per il giorno {g}"); break
            
            if not conflitto:
                gg = int(np.busday_count(da, al + timedelta(days=1)))
                ore_tot = round(gg * ORE_GIORNATA, 2)
                nuova = pd.DataFrame([[nome_u, da, al, tipo, risorsa, ore_tot, ""]], columns=COLONNE_FERIE)
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success(f"Richiesta salvata! ({ore_tot} ore)"); time.sleep(1); st.rerun()
