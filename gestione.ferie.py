import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'

# Database iniziale con i nomi corretti
DIPENDENTI_BASE = [
    ["ROSSINI LORENZO", 0.96, 0.0, "Guardia"],
    ["ABBATICCHIO ANTONIO", 53.13, 11.24, "Fiduciario"],
    ["ACQUAVIVA ANNALISA", 126.40, 72.63, "Fiduciario"],
    ["ANTONACCI MARIO", 146.92, 43.98, "Fiduciario"],
    ["DI RELLA COSIMO DAMIANO", 15.34, 29.01, "Fiduciario"],
    ["FAVIA ANTONIO", 0.0, 0.0, "Guardia"]
]

st.set_page_config(page_title="Battistolli HR - Smart Login", layout="wide")

# --- ENGINE DI INIZIALIZZAZIONE ---
@st.cache_data
def load_initial_data():
    df = pd.DataFrame(DIPENDENTI_BASE, columns=['Nome', 'Ferie', 'ROL', 'Contratto'])
    df['Password'] = "12345"
    return df

df_dip = load_initial_data()

# --- LOGIN INTELLIGENTE ---
st.title("🏢 Accesso Portale Battistolli")
u_in = st.text_input("INSERISCI NOME E COGNOME").strip().upper()
p_in = st.text_input("Password", type="password").strip()

if st.button("ACCEDI"):
    # Controllo Admin
    if u_in == "ADMIN" and p_in == "admin2024":
        st.session_state["user"] = "admin"; st.rerun()
    
    # Controllo Utente Flessibile (ROSSINI LORENZO o LORENZO ROSSINI)
    successo = False
    for nome_db in df_dip['Nome'].values:
        # Creiamo la versione invertita del nome nel DB (es: da ROSSINI LORENZO a LORENZO ROSSINI)
        parti = nome_db.split()
        nome_invertito = " ".join(parti[::-1])
        
        if u_in == nome_db or u_in == nome_invertito:
            user_row = df_dip[df_dip['Nome'] == nome_db].iloc[0]
            if str(user_row['Password']) == p_in:
                st.session_state["user"] = nome_db
                successo = True
                break
    
    if successo:
        st.success("Accesso eseguito!"); time.sleep(1); st.rerun()
    else:
        st.error(f"Credenziali non valide. Assicurati di aver scritto bene il nome.")

# --- AREA PERSONALE ---
if "user" in st.session_state:
    nome = st.session_state["user"]
    if nome != "admin":
        dati = df_dip[df_dip['Nome'] == nome].iloc[0]
        st.header(f"Benvenuto, {nome}")
        st.info(f"Contratto: {dati['Contratto']}")
        st.metric("Saldo Ferie (Giorni)", dati['Ferie'])
        if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()
