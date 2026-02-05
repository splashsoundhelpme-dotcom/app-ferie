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
ORE_GIORNATA = 6.67  # 6h 40m

st.set_page_config(page_title="Battistolli HR", layout="wide")

# --- DATABASE REALE ESTRATTO DAL TUO FILE (45 DIPENDENTI) ---
def popola_database_iniziale():
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
        dati = [
            ["ABBATICCHIO ANTONIO", 53.13, 11.24], ["ACQUAVIVA ANNALISA", 126.4, 72.63],
            ["ANTONACCI MARIO", 146.92, 43.98], ["BERGAMASCO COSIMO DAMIANO", 186.6, 47.81],
            ["BOTTALICO LEONARDO", 133.42, 9.33], ["BOZZI RAFFAELLA", 258.08, 106.6],
            ["BUFANO GIULIO", 11.12, 0.0], ["BUQUICCHIO ANGELA", 259.03, 48.65],
            ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95], ["CAMPANILE DENNIS", 92.73, 47.85],
            ["CARBONE ROBERTA", 66.64, 47.2], ["CISTERNINO BENITO", 93.14, -19.35],
            ["DE NAPOLI SERENA", 26.49, 115.55], ["DI BARI GIORGIA", 112.76, 54.03],
            ["DILISO CLARA ANNARITA", 152.13, 44.23], ["FIORE ANTONIO", 39.56, 0.0],
            ["GIANNINI CAMILLA", 135.33, 85.08], ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18],
            ["LAMADDALENA ANTONIO", 47.32, 0.0], ["MANGIONE FRANCESCO", 66.42, 10.37],
            ["MARCHITELLI VITO", 115.14, 57.06], ["MARTINELLI DOMENICO", 10.0, 52.6],
            ["MICELE MARCO", 76.53, 53.1], ["MILILLO MARCO", 12.35, 11.0],
            ["MINECCIA GIUSEPPE", 66.6, 32.7], ["MOLINARO NATALIZIA", 143.23, 114.3],
            ["MONGELLI SAVINO", 113.12, 57.0], ["MONTEMURRO MICHELE", 14.65, 0.0],
            ["NACCARATO MICHELE", 83.1, 46.5], ["NICOLAIDIS GIOVANNI", 111.45, 57.05],
            ["ONESTO MARCO", 5.2, 0.0], ["ORLANDO GIUSY", 243.61, 93.9],
            ["PACE ROSA", 3.01, 10.15], ["PADOVANO MICHELE", 122.5, 47.2],
            ["PALMIERI VALERIA", 33.35, 42.45], ["PAPAGNA NICOLA", 46.01, 11.4],
            ["PASTORE PASQUALE", 158.02, 57.17], ["PERRUCCI CARLO", 136.21, 57.0],
            ["PIGNATARO ANTONIO", 114.7, 50.15], ["QUERO MARCO", 110.1, 44.22],
            ["RIZZI FILOMENA", 114.65, 57.01], ["RUTIGLIANO MARCO", 44.3, 10.0],
            ["SANSONNE NICOLA", 120.5, 44.0], ["SANTORO GIUSEPPE", 33.1, 12.5],
            ["ROSSINI LORENZO", 80.0, 20.0]
        ]
        df = pd.DataFrame(dati, columns=['Nome', 'Saldo_Ferie_2025', 'Saldo_ROL_2025'])
        df['Password'] = PASSWORD_STANDARD
        df.to_csv(FILE_DIPENDENTI, index=False)

def inizializza_files():
    popola_database_iniziale()
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo_A', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)

inizializza_files()
df_dip = pd.read_csv(FILE_DIPENDENTI)

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Battistolli HR")
    u_input = st.text_input("NOME COGNOME (Esempio: ABBATICCHIO ANTONIO)").upper().strip()
    p_input = st.text_input("Password", type="password")
    
    if st.button("ACCEDI"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            user = df_dip[(df_dip['Nome'] == u_input) & (df_dip['Password'].astype(str) == p_input)]
            if not user.empty:
                st.session_state["user"] = u_input
                st.rerun()
            else:
                st.error("Credenziali errate. Assicurati di scrivere il nome correttamente come nel file.")
    st.stop()

# --- INTERFACCIA ---
with st.sidebar:
    st.info(f"Utente: {st.session_state['user']}")
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()

if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    dati = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    st.header(f"Ciao {nome_u}")
    
    c1, c2 = st.columns(2)
    c1.metric("Saldo Ferie", f"{dati['Saldo_Ferie_2025']} h")
    c2.metric("Saldo ROL", f"{dati['Saldo_ROL_2025']} h")
    
    with st.form("richiesta"):
        st.subheader("Invia Richiesta")
        tipo = st.selectbox("Tipo", ["Ferie", "104", "Donazione Sangue"])
        da = st.date_input("Inizio")
        a = st.date_input("Fine")
        risorsa = st.radio("Scala da:", ["Saldo_Ferie_2025", "Saldo_ROL_2025"])
        
        if st.form_submit_button("Invia"):
            gg = int(np.busday_count(da, a + timedelta(days=1)))
            ore = round(gg * ORE_GIORNATA, 2)
            # Salvataggio e aggiornamento (logica semplificata per test)
            st.success(f"Richiesta inviata per {ore} ore.")

else:
    st.title("Pannello Amministratore")
    st.write("### Anagrafica e Saldi Attuali")
    st.dataframe(df_dip, use_container_width=True)
