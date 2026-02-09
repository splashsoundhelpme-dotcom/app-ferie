import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- 1. CONFIGURAZIONE COSTANTI ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
LIMITE_CONTEMPORANEITA = 3 
ORE_GIORNATA_FIDUCIARI = 6.67

# --- 2. FUNZIONI DI SERVIZIO ---
def formatta_data_it(data_obj):
    """Converte date ISO (AAAA-MM-GG) in formato Italiano (GG/MM/AAAA)"""
    if isinstance(data_obj, str):
        try:
            data_obj = datetime.strptime(data_obj, '%Y-%m-%d')
        except:
            return data_obj
    return data_obj.strftime('%d/%m/%Y')

def invia_email(oggetto, corpo):
    """Gestisce l'invio delle notifiche tramite Gmail SMTP e Streamlit Secrets"""
    try:
        if "email" not in st.secrets:
            return False
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
    except Exception as e:
        print(f"Errore Email: {e}")
        return False

# --- 3. INIZIALIZZAZIONE DATABASE (I 45 NOMI) ---
def inizializza_database():
    # Esempio di struttura per i tuoi 45 dipendenti
    # Puoi espandere questa lista liberamente
    elenco_iniziale = [
        ["ROSSINI LORENZO", 6.40, 12.0, "Guardia", "12345"],
        ["ABBATICCHIO ANTONIO", 10.0, 8.0, "Fiduciario", "12345"],
        ["ACQUAVIVA ANNALISA", 10.0, 8.0, "Fiduciario", "12345"],
        ["ANTONACCI MARIO", 15.0, 10.0, "Guardia", "12345"],
        ["DI RELLA COSIMO DAMIANO", 12.0, 5.0, "Guardia", "12345"],
        ["FAVIA ANTONIO", 8.0, 4.0, "Guardia", "12345"],
        # ... aggiungi qui gli altri nomi seguendo lo schema ...
    ]
    
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(elenco_iniziale, columns=['Nome','Ferie','ROL','Contratto','Password'])
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        df_f = pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
        df_f.to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = inizializza_database()

# --- 4. INTERFACCIA UTENTE ---
st.set_page_config(page_title="Battistolli HR v28.0", layout="wide")

# Gestione Login
if "user" not in st.session_state:
    st.title("🏢 Portale Risorse Umane - Battistolli")
    st.subheader("Accesso Dipendenti")
    u_in = st.text_input("NOME E COGNOME (MAIUSCOLO)").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
            
        trovato = False
        for n in df_dip['Nome'].values:
            n_inv = " ".join(n.split()[::-1]) # Supporta Cognome Nome o Nome Cognome
            if u_in == n or u_in == n_inv:
                if str(df_dip[df_dip['Nome'] == n].iloc[0]['Password']) == p_in:
                    st.session_state["user"] = n
                    trovato = True; break
        
        if trovato: st.rerun()
        else: st.error("Dati di accesso non corretti.")
    st.stop()

# --- 5. LOGICA AREA ADMIN ---
current_user = st.session_state["user"]

if current_user == "admin":
    st.header("👨‍💼 Console Amministratore")
    c1, c2 = st.columns([3, 1])
    
    with c2:
        if st.button("🚪 LOGOUT"):
            del st.session_state["user"]; st.rerun()
        st.divider()
        st.error("ZONA RESET")
        if st.button("🗑️ SVUOTA REGISTRO FERIE"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
            st.success("Tutte le richieste sono state cancellate.")
            time.sleep(1); st.rerun()

    with c1:
        st.subheader("📋 Registro O.D.S. (Tutte le prenotazioni)")
        if not df_ferie.empty:
            df_admin = df_ferie.copy()
            df_admin['Inizio'] = df_admin['Inizio'].apply(formatta_data_it)
            df_admin['Fine'] = df_admin['Fine'].apply(formatta_data_it)
            st.table(df_admin)
        else:
            st.info("Al momento non ci sono richieste caricate.")

# --- 6. LOGICA AREA DIPENDENTE ---
else:
    info = df_dip[df_dip['Nome'] == current_user].iloc[0]
    unita = "Giorni" if info['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto, {current_user}")
    
    # Calcolo Saldi in tempo reale
    u_ferie = df_ferie[(df_ferie['Nome'] == current_user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    u_rol = df_ferie[(df_ferie['Nome'] == current_user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Saldo Ferie ({unita})", round(float(info['Ferie']) - u_ferie, 2))
    m2.metric(f"Saldo ROL ({unita})", round(float(info['ROL']) - u_rol, 2))
    if m3.button("Logout"):
        del st.session_state["user"]; st.rerun()

    st.divider()
    
    # Visualizzazione Disponibilità (Semaforo)
    st.subheader("📅 Disponibilità Posti Ferie")
    giorni_test = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols_calendar = st.columns(len(giorni_test))
    
    for idx, d_day in enumerate(giorni_test):
        count_occ = 0
        if not df_ferie.empty:
            count_occ = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= d_day) & (pd.to_datetime(df_ferie['Fine']).dt.date >= d_day)])
        
        status = "🟢" if count_occ < LIMITE_CONTEMPORANEITA else "🔴"
        cols_calendar[idx].markdown(f"**{d_day.strftime('%d/%m')}**\n\n{status}\n\n{count_occ}/{LIMITE_CONTEMPORANEITA}")

    st.divider()

    # Modulo Richiesta
    with st.form("invio_form_definitivo"):
        st.subheader("📝 Inserisci Nuova Richiesta")
        tipo_req = st.selectbox("Seleziona Causale", ["Ferie", "ROL"])
        day_start = st.date_input("Dalla data (Inclusa)", value=date.today()+timedelta(days=1), min_value=date.today()+timedelta(days=1))
        day_end = st.date_input("Alla data (Inclusa)", value=date.today()+timedelta(days=1), min_value=date.today()+timedelta(days=1))
        
        if st.form_submit_button("CONFERMA E INVIA"):
            intervallo_date = pd.date_range(day_start, day_end).date
            bloccato = False
            for d in intervallo_date:
                if not df_ferie.empty:
                    c = len(df_ferie[(pd.to_datetime(df_fer
