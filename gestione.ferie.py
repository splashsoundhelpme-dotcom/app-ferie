import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
LIMITE_CONTEMPORANEITA = 3 
ORE_GIORNATA_FIDUCIARI = 6.67

# --- FUNZIONI DI UTILITÀ ---
def formatta_data_it(data_obj):
    """Trasforma un oggetto date/datetime o stringa ISO in GG/MM/AAAA"""
    if isinstance(data_obj, str):
        data_obj = datetime.strptime(data_obj, '%Y-%m-%d')
    return data_obj.strftime('%d/%m/%Y')

def invia_email(oggetto, corpo):
    try:
        if "email" not in st.secrets: return False
        mittente = st.secrets["email"]["user"]
        password = st.secrets["email"]["password"]
        destinatario = st.secrets["email"]["admin_email"]
        msg = MIMEText(corpo)
        msg['Subject'] = oggetto
        msg['From'] = mittente
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(mittente, password)
            server.sendmail(mittente, destinatario, msg.as_string())
        return True
    except: return False

# --- GESTIONE DATABASE ---
def refresh_database():
    dati_test = [
        ["ROSSINI LORENZO", 6.40, 12.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 8.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 8.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 40.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 40.0, "Fiduciario", "test4"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(dati_test, columns=['Nome','Ferie','ROL','Contratto','Password']).to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()

st.set_page_config(page_title="Battistolli HR v26.3", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale Battistolli")
    u_in = st.text_input("NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        successo = False
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        for nome_db in df_dip['Nome'].values:
            nome_inv = " ".join(nome_db.split()[::-1])
            if u_in == nome_db or u_in == nome_inv:
                if str(df_dip[df_dip['Nome'] == nome_db].iloc[0]['Password']) == p_in:
                    st.session_state["user"] = nome_db; successo = True; break
        if successo: st.rerun()
        else: st.error("Credenziali
