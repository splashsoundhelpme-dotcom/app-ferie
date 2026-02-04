import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024" 
PASSWORD_STANDARD = "12345" 
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'

def carica_dati():
    if not os.path.exists(FILE_DIPENDENTI):
        df_dip = pd.DataFrame(columns=['Nome', 'Saldo_Arretrato', 'Password', 'Primo_Accesso'])
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
    if not os.path.exists(FILE_FERIE):
        df_ferie = pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Giorni'])
        df_ferie.to_csv(FILE_FERIE, index=False)
    else:
        df_ferie = pd.read_csv(FILE_FERIE)
        # Assicuriamoci che siano oggetti data
        df_ferie['Inizio'] = pd.to_datetime(df_ferie['Inizio']).dt.date
        df_ferie['Fine'] = pd.to_datetime(df_ferie['Fine']).dt.date
    return df_dip, df_ferie

def calcola_giorni_lavorativi(start, end):
    return np.busday_count(start, end + timedelta(days=1))

def calcola_ferie_maturate_2026(saldo_arretrato):
    oggi = date.today()
    if oggi.year < 2026: return float(saldo_arretrato)
    mesi_maturati = oggi.month
    if oggi.year > 2026: mesi_maturati += (oggi.year - 2026) * 12
    return round(float(saldo_arretrato) + (mesi_maturati * 2.33), 2)

def verifica_disponibilita(inizio, fine, df_esistente):
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        contatore = 0
        for _, row in df_esistente.iterrows():
            if row['Inizio'] <= giorno <= row['Fine']:
                if row['Tipo'] not in ["104", "Congedo Parentale", "Donazione Sangue"]:
                    contatore += 1
        if contatore >= 3:
            return False, giorno
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- ACCESSO ---
if "user" not in st.session_state:
    st.title("🔐 Portale Aziendale")
    nome_input = st.text_input("Nome Utente (Esatto come registrato)")
    pwd_input = st.text_input("Password", type="password")
    if st.button("Entra"):
        if nome_input == "admin" and pwd_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            # Controllo minuscole/maiuscole e spazi per facilitare l'accesso
            df_dipendenti['Nome_Lower'] = df_dipendenti['Nome'].str.lower().str.strip()
            utente = df_dipendenti[(df_dipendenti['Nome_Lower'] == nome_input.lower().strip()) & (df_dipendenti['Password'].astype
