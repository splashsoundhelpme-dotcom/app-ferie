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
        df_dip = pd.DataFrame(columns=['Nome', 'Ferie_Totali_Anno', 'Password', 'Primo_Accesso'])
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
    if not os.path.exists(FILE_FERIE):
        df_ferie = pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Giorni'])
        df_ferie.to_csv(FILE_FERIE, index=False)
    else:
        df_ferie = pd.read_csv(FILE_FERIE)
    return df_dip, df_ferie

def calcola_giorni_lavorativi(start, end):
    return np.busday_count(start, end + timedelta(days=1))

df_dipendenti, df_ferie = carica_dati()

# --- GESTIONE ACCESSO ---
if "user" not in st.session_state:
    st.title("🔐 Accesso Portale Ferie")
    nome_input = st.text_input("Nome Utente")
    pwd_input = st.text_input("Password", type="password")
    
    if st.button("Entra"):
        if nome_input == "admin" and pwd_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            utente = df_dipendenti[(df_dipendenti['Nome'] == nome_input) & (df_dipendenti['Password'].astype(str) == pwd_input)]
            if not utente.empty:
                st.session_state["user"] = nome_input
                st.rerun()
            else:
                st.error("Dati errati. Se hai dimenticato la password, contatta l'amministratore.")
    st.stop()

# --- CAMBIO PASSWORD OBBLIGATORIO ---
if st.session_state["user"] != "admin":
    idx_list = df_dipendenti.index[df_dipendenti['Nome'] == st.session_state["user"]].tolist()
    if idx_list:
        idx = idx_list[0]
        if df_dipendenti.at[idx, 'Primo_Accesso'] == True:
            st.warning("🔒 Devi impostare una password personale.")
            nuova_pwd = st.text_input("Nuova password", type="password")
            conferma = st.text_input("Conferma password", type="password")
            if st.button("Salva"):
                if nuova_pwd == conferma and len(nuova_pwd) > 3:
                    df_dipendenti.at[idx, 'Password'] = nuova_pwd
                    df_dipendenti.at[idx, 'Primo_Accesso'] = False
                    df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                    st.success("Password salvata!")
                    st.rerun()
                else:
                    st.error("Errore nelle password.")
            st.stop()

# --- LOGOUT ---
if st.sidebar.button("Esci"):
    del st.session_state["user"]
    st.rerun()

# --- INTERFACCIA ---
if st.session_state["user"] != "admin":
    # --- AREA DIPENDENTE ---
    nome_u = st.session_state["user"]
    st.title(f"👋 Ciao {nome_u}")
    dati = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Ferie Rimanenti", f"{dati['Ferie_Totali_Anno'] - usate} gg")
    
    with st.form("invio"):
        tipo = st.selectbox("Tipo", ["Ferie", "Permesso", "Malattia"])
        inizio = st.date_input("Inizio")
        fine = st.date_input("Fine")
        if st.form_submit_button("Invia"):
            g = calcola_giorni_lavorativi(inizio, fine)
            nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Giorni':[g]})
            df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)
            df_ferie.to_csv(FILE_FERIE, index=False)
            st.success("Inviata!")
else:
    # --- AREA ADMIN ---
    st.title("👨‍💼 Pannello Admin")
    menu = st.sidebar.radio("Menu", ["Riepilogo", "Gestione Personale"])
    
    if menu == "Riepilogo":
        st.write("### Storico Ferie", df_ferie)
    else:
        st.subheader("Aggiungi Dipendente")
        with st.form("add"):
            n = st.text_input("Nome")
            g = st.number_input("Giorni", 26)
            if st.form_submit_button("Crea"):
                nuovo = pd.DataFrame({'Nome':[n], 'Ferie_Totali_Anno':[g], 'Password':[PASSWORD_STANDARD], 'Primo_Accesso':[True]})
                df_dipendenti = pd.concat([df_dipendenti, nuovo], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.rerun()
        
        st.divider()
        st.subheader("🆘 Recupero Password")
        if not df_dipendenti.empty:
            target = st.selectbox("Scegli dipendente da resettare", df_dipendenti['Nome'])
            if st.button("Resetta Password a Standard"):
                idx_res = df_dipendenti.index[df_dipendenti['Nome'] == target].tolist()[0]
                df_dipendenti.at[idx_res, 'Password'] = PASSWORD_STANDARD
                df_dipendenti.at[idx_res, 'Primo_Accesso'] = True
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.warning(f"Password di {target} resettata a {PASSWORD_STANDARD}. Al prossimo accesso dovrà cambiarla.")
