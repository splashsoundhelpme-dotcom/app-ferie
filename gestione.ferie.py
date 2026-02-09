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

# --- FUNZIONE INVIO EMAIL ---
def invia_email(oggetto, corpo):
    try:
        # Recupera le credenziali dai Secrets di Streamlit
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
    except:
        return False

def refresh_database():
    dati_test = [
        ["ROSSINI LORENZO", 6.40, 12.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 8.0, "Guardia", "test1"],
        ["TEST FIDUCIARIO 1", 100.0, 40.0, "Fiduciario", "test3"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_test, columns=['Nome','Ferie','ROL','Contratto','Password'])
        df.to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()
st.set_page_config(page_title="Battistolli HR v25.0", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale Battistolli")
    u_in = st.text_input("NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            st.session_state["user"] = u_in; st.rerun()
    st.stop()

user = st.session_state["user"]

# --- AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Console Amministratore")
    st.subheader("Registro Dettagliato")
    st.dataframe(df_ferie)
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

# --- AREA UTENTE ---
else:
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto {user}")
    
    # Visualizzazione Saldi (Ferie e ROL)
    usato_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Saldo Ferie ({unita})", round(dati['Ferie'] - usato_f, 2))
    c2.metric(f"Saldo ROL ({unita})", round(dati['ROL'] - usato_r, 2))
    if c3.button("Logout"): del st.session_state["user"]; st.rerun()

    st.divider()
    
    with st.form("richiesta_v25"):
        st.subheader("📝 Nuova Richiesta")
        tipo_scelta = st.selectbox("Cosa vuoi richiedere?", ["Ferie", "ROL"])
        # BLOCCO DATA ODIERNA: Il minimo selezionabile è domani
        domani = date.today() + timedelta(days=1)
        da = st.date_input("Inizio", value=domani, min_value=domani)
        al = st.date_input("Fine", value=domani, min_value=domani)
        
        if st.form_submit_button("Invia Richiesta"):
            # Verifica blocco 3 persone (logica v23.5)
            intervallo = pd.date_range(da, al).date
            conflitto = False
            for g in intervallo:
                cont = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g)])
                if cont >= LIMITE_CONTEMPORANEITA:
                    conflitto = True; break
            
            if conflitto:
                st.error("❌ Limite massimo raggiunto per quelle date.")
            else:
                valore = len(intervallo) if dati['Contratto'] == "Guardia" else round(len(intervallo) * 6.67, 2)
                nuova = pd.DataFrame([[user, str(da), str(al), tipo_scelta, tipo_scelta, valore, unita]], 
                                    columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                
                # INVIO EMAIL
                testo_mail = f"Nuova richiesta da {user}: {tipo_scelta} dal {da.strftime('%d/%m/%Y')} al {al.strftime('%d/%m/%Y')}"
                inviata = invia_email(f"Richiesta {tipo_scelta} - {user}", testo_mail)
                
                st.success(f"✅ Richiesta salvata! Email inviata: {'Sì' if inviata else 'No (Configura Secrets)'}")
                time.sleep(2); st.rerun()
