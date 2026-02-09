import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# --- 1. COMANDO DI PULIZIA FORZATA ---
# Questo cancella i file "invisibili" che bloccano l'accesso a Lorenzo Rossini
if os.path.exists('db_dipendenti.csv'):
    os.remove('db_dipendenti.csv')
if os.path.exists('db_ferie.csv'):
    os.remove('db_ferie.csv')

# --- 2. NUOVI DATI (CON LORENZO ROSSINI) ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'

DIPENDENTI_BASE = [
    ["ROSSINI LORENZO", 0.96, 0.0, "Guardia"],
    ["ABBATICCHIO ANTONIO", 53.13, 11.24, "Fiduciario"],
    ["ACQUAVIVA ANNALISA", 126.40, 72.63, "Fiduciario"],
    ["ANTONACCI MARIO", 146.92, 43.98, "Fiduciario"],
    ["DI RELLA COSIMO DAMIANO", 15.34, 29.01, "Fiduciario"],
    ["FAVIA ANTONIO", 0.0, 0.0, "Guardia"]
]

st.set_page_config(page_title="Battistolli HR FIX", layout="wide")

# --- 3. CREAZIONE DATABASE PULITO ---
df_dip = pd.DataFrame(DIPENDENTI_BASE, columns=['Nome', 'Ferie', 'ROL', 'Contratto'])
df_dip['Password'] = PASSWORD_DEFAULT
df_dip.to_csv(FILE_DIPENDENTI, index=False)

if not os.path.exists(FILE_FERIE):
    pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
df_ferie = pd.read_csv(FILE_FERIE)

# --- 4. LOGIN ---
st.title("🏢 Accesso Portale Battistolli")
u_in = st.text_input("NOME COGNOME").strip().upper()
p_in = st.text_input("Password", type="password").strip()

if st.button("ACCEDI"):
    if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
        st.session_state["user"] = "admin"; st.rerun()
    elif u_in in df_dip['Nome'].values:
        user_row = df_dip[df_dip['Nome'] == u_in].iloc[0]
        if str(user_row['Password']) == p_in:
            st.session_state["user"] = u_in; st.rerun()
        else: st.error("Password errata.")
    else:
        st.error(f"L'utente '{u_in}' non è in lista. Nomi disponibili: {df_dip['Nome'].tolist()}")

# --- 5. AREA UTENTE ---
if "user" in st.session_state:
    nome = st.session_state["user"]
    if nome != "admin":
        dati = df_dip[df_dip['Nome'] == nome].iloc[0]
        unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
        st.header(f"Ciao {nome}")
        st.metric(f"Saldo Ferie ({unita})", dati['Ferie'])
        if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()
    else:
        st.write("Area Admin")
        st.dataframe(df_dip)
