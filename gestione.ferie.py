import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67  # 6 ore e 40 minuti

st.set_page_config(page_title="Battistolli HR", layout="wide")

# --- DATABASE DEFINITIVO (DA LISTA TESTUALE) ---
def genera_database_corretto():
    # Dati inseriti manualmente dalla tua lista
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
    return df

# Controllo e Auto-Riparazione
if os.path.exists(FILE_DIPENDENTI):
    df_check = pd.read_csv(FILE_DIPENDENTI)
    if "ABBATICCHIO ANTONIO" not in df_check['Nome'].values:
        df_dip = genera_database_corretto()
    else:
        df_dip = df_check
else:
    df_dip = genera_database_corretto()

if not os.path.exists(FILE_FERIE):
    pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Gestione Personale Battistolli")
    u_input = st.text_input("NOME COGNOME (Esempio: ROSSINI LORENZO)").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        else:
            user_row = df_dip[df_dip['Nome'] == u_input]
            if not user_row.empty and str(user_row.iloc[0]['Password']) == p_input:
                st.session_state["user"] = u_input; st.rerun()
            else:
                st.error("Dati non corretti. Usa NOME COGNOME tutto maiuscolo.")
    st.stop()

# --- DASHBOARD ---
with st.sidebar:
    st.write(f"Connesso: **{st.session_state['user']}**")
    if st.button("Logout"):
        del st.session_state["user"]; st.rerun()

if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    # Calcolo residui in tempo reale
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    st.header(f"Ciao {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("Residuo Ferie", f"{round(dati_u['Ferie'] - usato_f, 2)} h")
    c2.metric("Residuo ROL", f"{round(dati_u['ROL'] - usato_r, 2)} h")

    st.divider()

    with st.form("invio"):
        st.subheader("Nuova Richiesta")
        tipo = st.selectbox("Motivo", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        inizio = st.date_input("Dal")
        fine = st.date_input("Al")
        if st.form_submit_button("Invia"):
            if inizio > fine:
                st.error("Date non valide.")
            else:
                gg = int(np.busday_count(inizio, fine + timedelta(days=1)))
                ore = round(gg * ORE_GIORNATA, 2)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Risorsa':[risorsa],'Ore':[ore],'Note':[""]})
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success("Richiesta registrata!")
                time.sleep(1); st.rerun()
else:
    st.title("💻 Amministrazione")
    tab1, tab2 = st.tabs(["Richieste", "Personale"])
    with tab1:
        st.dataframe(pd.read_csv(FILE_FERIE), use_container_width=True)
    with tab2:
        st.dataframe(df_dip[['Nome', 'Ferie', 'ROL']], use_container_width=True)
