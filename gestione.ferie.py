import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"

# 1. FUNZIONE DI REFRESH FORZATO (Risolve il problema dell'accesso)
def refresh_database():
    dati_test_e_reali = [
        ["ROSSINI LORENZO", 6.40, 0.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 0.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 0.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 20.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 20.0, "Fiduciario", "test4"],
        ["FAVIA ANTONIO", 0.0, 0.0, "Guardia", "12345"]
    ]
    
    # Se il file esiste ma non ha l'utente test, lo cancelliamo per aggiornarlo
    if os.path.exists(FILE_DIPENDENTI):
        df_check = pd.read_csv(FILE_DIPENDENTI)
        if "TEST GUARDIA 1" not in df_check['Nome'].values:
            os.remove(FILE_DIPENDENTI)
    
    # Creazione file pulito con tutti i nomi
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_test_e_reali, columns=['Nome', 'Ferie', 'ROL', 'Contratto', 'Password'])
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)

    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()

st.set_page_config(page_title="Battistolli HR v23.2", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Area Test")
    st.info("Prova con: TEST GUARDIA 1 / test1")
    
    u_in = st.text_input("NOME UTENTE").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            row = df_dip[df_dip['Nome'] == u_in].iloc[0]
            if str(row['Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Password errata.")
        else:
            st.error(f"Utente '{u_in}' non trovato. Riprova o contatta l'assistenza.")
    st.stop()

# --- INTERFACCIA ---
user = st.session_state["user"]

if user == "admin":
    st.header("👨‍💼 Console Amministratore")
    st.dataframe(df_dip)
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()
else:
    # Area per i tuoi test
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto {user}")
    st.write(f"Tipo Contratto: **{dati['Contratto']}**")
    
    usato = df_ferie[df_ferie['Nome'] == user]['Valore'].sum()
    st.metric(f"Saldo Residuo ({unita})", round(dati['Ferie'] - usato, 2))
    
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()
