import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
LIMITE_CONTEMPORANEITA = 3  # Massimo 3 persone insieme

def refresh_database():
    dati_test = [
        ["ROSSINI LORENZO", 6.40, 0.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 0.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 0.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 20.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 20.0, "Fiduciario", "test4"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(dati_test, columns=['Nome','Ferie','ROL','Contratto','Password']).to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()
st.set_page_config(page_title="Battistolli HR v23.5 - BLOCK TEST", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Test Blocco Contemporaneità")
    u_in = st.text_input("NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            st.session_state["user"] = u_in; st.rerun()
    st.stop()

user = st.session_state["user"]

if user == "admin":
    st.header("👨‍💼 Admin - Registro Conflitti")
    st.dataframe(df_ferie)
    if st.button("🗑️ RESET REGISTRO (per ripartire da zero)"):
        os.remove(FILE_FERIE)
        st.rerun()
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

else:
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    st.header(f"Utente: {user}")
    
    with st.form("form_blocco"):
        da = st.date_input("Inizio", value=date.today())
        al = st.date_input("Fine", value=date.today())
        submit = st.form_submit_button("VERIFICA E INVIA")
        
        if submit:
            intervallo = pd.date_range(da, al).date
            conflitto = False
            giorno_pieno = ""

            for g in intervallo:
                # Controlliamo quante persone hanno ferie che coprono il giorno 'g'
                contatore = 0
                for _, riga in df_ferie.iterrows():
                    inizio_f = datetime.strptime(riga['Inizio'], '%Y-%m-%d').date()
                    fine_f = datetime.strptime(riga['Fine'], '%Y-%m-%d').date()
                    if inizio_f <= g <= fine_f:
                        contatore += 1
                
                if contatore >= LIMITE_CONTEMPORANEITA:
                    conflitto = True
                    giorno_pieno = g.strftime('%d/%m/%Y')
                    break
            
            if conflitto:
                st.error(f"❌ RICHIESTA NEGATA: Il giorno {giorno_pieno} ci sono già {LIMITE_CONTEMPORANEITA} persone assenti.")
            else:
                nuova = pd.DataFrame([[user, str(da), str(al), "Ferie", "Ferie", 1, "G/O"]], 
                                    columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success("✅ Richiesta approvata e registrata!")
                time.sleep(1); st.rerun()
