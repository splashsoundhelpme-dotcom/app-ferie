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
EMAIL_NOTIFICA = "lorenzo.rossini@battistolli.it"

def carica_dati():
    # Creazione file dipendenti se vuoto o inesistente
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
        # Quando mi manderai l'elenco, aggiornerò questi nomi e saldi
        dati_iniziali = {
            'Nome': ['Lorenzo Rossini'], 
            'Saldo_Arretrato': [0.0],
            'Password': [PASSWORD_STANDARD],
            'Primo_Accesso': [True]
        }
        df_dip = pd.DataFrame(dati_iniziali)
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
    # Creazione file ferie se vuoto o inesistente
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
        df_ferie = pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Giorni'])
        df_ferie.to_csv(FILE_FERIE, index=False)
    else:
        df_ferie = pd.read_csv(FILE_FERIE)
        df_ferie['Inizio'] = pd.to_datetime(df_ferie['Inizio']).dt.date
        df_ferie['Fine'] = pd.to_datetime(df_ferie['Fine']).dt.date
    return df_dip, df_ferie

def calcola_giorni_lavorativi(start, end):
    return np.busday_count(start, end + timedelta(days=1))

def calcola_ferie_maturate_2026(saldo_arretrato):
    oggi = date.today()
    mesi = oggi.month if oggi.year == 2026 else (12 if oggi.year > 2026 else 0)
    return round(float(saldo_arretrato) + (mesi * 2.33), 2)

def verifica_disponibilita(inizio, fine, df_esistente, tipo_richiesta):
    # Logica Salta Fila
    if tipo_richiesta in ["104", "Congedo Parentale", "Donazione Sangue"]:
        return True, None
    
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        assenti = df_esistente[(df_esistente['Inizio'] <= giorno) & (df_esistente['Fine'] >= giorno)]
        if len(assenti) >= 3:
            return False, giorno
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🔐 Portale Ferie & Assenze")
    nome_input = st.text_input("Nome Utente")
    pwd_input = st.text_input("Password", type="password")
    
    if st.button("ACCEDI"):
        if nome_input == "admin" and pwd_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        elif not df_dipendenti.empty:
            df_dipendenti['Nome_Lower'] = df_dipendenti['Nome'].str.lower().str.strip()
            nome_cercato = nome_input.lower().strip()
            utente = df_dipendenti[(df_dipendenti['Nome_Lower'] == nome_cercato) & (df_dipendenti['Password'].astype(str) == pwd_input)]
            if not utente.empty:
                st.session_state["user"] = utente.iloc[0]['Nome']
                st.rerun()
            else:
                st.error("Credenziali non valide.")
        else:
            st.error("Database vuoto. Accedere come admin.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.button("🚪 Esci"):
        del st.session_state["user"]
        st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.header(f"👋 Pannello di {nome_u}")
    
    dati_u = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    
    # Saldo Ferie
    maturato = calcola_ferie_maturate_2026(dati_u['Saldo_Arretrato'])
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Saldo Ferie Stimato (ad oggi)", f"{round(maturato - usate, 2)} gg")

    # Inserimento Richiesta
    with st.form("nuova_richiesta"):
        tipo = st.selectbox("Motivo Assenza", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        c1, c2 = st.columns(2)
        inizio = c1.date_input("Dalla data", format="DD/MM/YYYY")
        fine = c2.date_input("Alla data", format="DD/MM/YYYY")
        
        if st.
