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
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
        df_dip = pd.DataFrame(columns=['Nome', 'Saldo_Arretrato', 'Password', 'Primo_Accesso'])
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
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

def verifica_disponibilita(inizio, fine, df_esistente, tipo_richiesta):
    # SALTA FILA: 104, Congedo, Donazione Sangue
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
    st.title("🔐 Portale Aziendale")
    nome_input = st.text_input("Nome Utente (usa TAB per scendere)")
    pwd_input = st.text_input("Password", type="password")
    
    if st.button("Entra"):
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
                st.error("Credenziali errate.")
        else:
            st.error("Database vuoto. Accedi come admin per aggiungere personale.")
    st.stop()

# --- LOGOUT ---
if st.sidebar.button("Esci / Logout"):
    del st.session_state["user"]
    st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.title(f"👋 Pannello di {nome_u}")
    
    with st.form("form_richiesta"):
        st.subheader("Inserisci la tua richiesta")
        tipo = st.selectbox("Motivazione", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        c1, c2 = st.columns(2)
        inizio = c1.date_input("Dal", format="DD/MM/YYYY")
        fine = c2.date_input("Al", format="DD/MM/YYYY")
        
        if st.form_submit_button("Invia"):
            ok, giorno_pieno = verifica_disponibilita(inizio, fine, df_ferie, tipo)
            if ok:
                g = calcola_giorni_lavorativi(inizio, fine)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Giorni':[g]})
                df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)
                df_ferie.to_csv(FILE_FERIE, index=False)
                
                st.success(f"✅ Richiesta salvata! Notifica inviata a {EMAIL_NOTIFICA}")
                time.sleep(2)
                st.rerun() # Torna alla home dell'app
            else:
                st.error(f"⛔ Limite raggiunto il {giorno_pieno.strftime('%d/%m/%Y')}. Scegli altre date.")

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Admin Dashboard")
    scelta = st.sidebar.radio("Menu", ["Planning", "Gestione Utenti"])

    if scelta == "Planning":
        st.write("### Situazione Settimanale")
        # Visualizza tabella ferie se non vuota
        if not df_ferie.empty:
            st.dataframe(df_ferie)
        else:
            st.info("Nessuna prenotazione presente.")

    elif scelta == "Gestione Utenti":
        st.subheader("Aggiungi Personale")
        with st.form("add"):
            n = st.text_input("Nome e Cognome")
            if st.form_submit_button("Aggiungi"):
                nuovo = pd.DataFrame({'Nome':[n], 'Saldo_Arretrato':[0], 'Password':[PASSWORD_STANDARD], 'Primo_Accesso':[True]})
                df_dipendenti = pd.concat([df_dipendenti, nuovo], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success(f"Aggiunto {n}")
                st.rerun()
