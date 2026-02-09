import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- CONFIGURAZIONE COSTANTI ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
LIMITE_CONTEMPORANEITA = 3 
ORE_GIORNATA_FIDUCIARI = 6.67

# --- 1. FUNZIONI DI SUPPORTO ---
def formatta_data_it(data_obj):
    """Converte qualsiasi formato data in GG/MM/AAAA per la visualizzazione"""
    if isinstance(data_obj, str):
        try:
            data_obj = datetime.strptime(data_obj, '%Y-%m-%d')
        except:
            return data_obj
    return data_obj.strftime('%d/%m/%Y')

def invia_email(oggetto, corpo):
    """Sistema di notifica e-mail tramite Secrets"""
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
    except:
        return False

# --- 2. GESTIONE DATABASE (INIZIALIZZAZIONE) ---
def carica_database():
    # Qui aggiungeremo i tuoi 45 dipendenti. Per ora ho messo i primi per test.
    elenco_base = [
        ["ROSSINI LORENZO", 6.40, 12.0, "Guardia", "12345"],
        ["ABBATICCHIO ANTONIO", 10.0, 8.0, "Fiduciario", "12345"],
        ["ACQUAVIVA ANNALISA", 10.0, 8.0, "Fiduciario", "12345"],
        ["ANTONACCI MARIO", 15.0, 10.0, "Guardia", "12345"],
        ["DI RELLA COSIMO DAMIANO", 12.0, 5.0, "Guardia", "12345"],
        ["FAVIA ANTONIO", 8.0, 4.0, "Guardia", "12345"]
    ]
    
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(elenco_base, columns=['Nome','Ferie','ROL','Contratto','Password']).to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = carica_database()

# --- 3. INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="Battistolli HR Management", layout="wide")

# LOGIN SYSTEM
if "user" not in st.session_state:
    st.title("🏢 Portale Battistolli - Gestione Assenze")
    nome_input = st.text_input("NOME E COGNOME (es. ROSSINI LORENZO)").strip().upper()
    pass_input = st.text_input("PASSWORD", type="password").strip()
    
    if st.button("ACCEDI"):
        if nome_input == "ADMIN" and pass_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
            
        trovato = False
        for n_db in df_dip['Nome'].values:
            n_rev = " ".join(n_db.split()[::-1])
            if nome_input == n_db or nome_input == n_rev:
                if str(df_dip[df_dip['Nome'] == n_db].iloc[0]['Password']) == pass_input:
                    st.session_state["user"] = n_db
                    trovato = True
                    break
        if trovato: 
            st.rerun()
        else: 
            st.error("Credenziali non valide. Verifica Nome o Password.")
    st.stop()

user_attuale = st.session_state["user"]

# --- 4. AREA AMMINISTRATORE (O.D.S.) ---
if user_attuale == "admin":
    st.header("👨‍💼 Console di Comando Admin")
    
    c_admin_1, c_admin_2 = st.columns([3, 1])
    
    with c_admin_2:
        if st.button("Logout"):
            del st.session_state["user"]; st.rerun()
        st.divider()
        if st.button("🗑️ RESET TUTTE LE FERIE"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
            st.warning("Archivio svuotato!")
            time.sleep(1); st.rerun()

    with c_admin_1:
        st.subheader("📋 Registro Prenotazioni per O.D.S.")
        if not df_ferie.empty:
            df_admin_view = df_ferie.copy()
            df_admin_view['Inizio'] = df_admin_view['Inizio'].apply(formatta_data_it)
            df_admin_view['Fine'] = df_admin_view['Fine'].apply(formatta_data_it)
            st.dataframe(df_admin_view, use_container_width=True)
        else:
            st.info("Nessuna prenotazione attiva.")

# --- 5. AREA DIPENDENTE ---
else:
    dati_u = df_dip[df_dip['Nome'] == user_attuale].iloc[0]
    u_misura = "Giorni" if dati_u['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto, {user_attuale}")
    
    # Calcolo Saldi Sottraendo le prenotazioni esistenti
    u_f = df_ferie[(df_ferie['Nome'] == user_attuale) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    u_r = df_ferie[(df_ferie['Nome'] == user_attuale) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Saldo Ferie ({u_misura})", round(float(dati_u['Ferie']) - u_f, 2))
    m2.metric(f"Saldo ROL ({u_misura})", round(float(dati_u['ROL']) - u_r, 2))
    if m3.button("Logout"):
        del st.session_state["user"]; st.rerun()

    st.divider()
    
    # Calendario Privacy per i dipendenti
    st.subheader("📅 Verifica Posti Disponibili")
    prossimi_giorni = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    col_cal = st.columns(len(prossimi_giorni))
    
    for i, giorno_c in enumerate(prossimi_giorni):
        occupati = 0
        if not df_ferie.empty:
            occupati = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= giorno_c) & (pd.to_datetime(df_ferie['Fine']).dt.date >= giorno_c)])
        
        colore = "🟢" if occupati < LIMITE_CONTEMPORANEITA else "🔴"
        col_cal[i].markdown(f"**{giorno_c.strftime('%d/%m')}**\n\n{colore}\n\n{occupati}/{LIMITE_CONTEMPORANEITA}")

    st.divider()

    # Form Richiesta
    with st.form("form_richiesta_v30"):
        st.subheader("📝 Nuova Richiesta")
        tipo_assenza = st.selectbox("Causale", ["Ferie", "ROL"])
        domani = date.today() + timedelta(days=1)
        data_inizio = st.date_input("Data Inizio", value=domani, min_value=domani)
        data_fine = st.date_input("Data Fine", value=domani, min_value=domani)
        
        if st.form_submit_button("INVIA RICHIESTA"):
            riferimento_date = pd.date_range(data_inizio, data_fine).date
            blocco_posto = False
            for d_singola in riferimento_date:
                if not df_ferie.empty:
                    n_occupati = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= d_singola) & (pd.to_datetime(df_ferie['Fine']).dt.date >= d_singola)])
                    if n_occupati >= LIMITE_CONTEMPORANEITA:
                        blocco_posto = True; break
            
            if blocco_posto:
                st.error("Spiacenti, per le date scelte non ci sono posti disponibili (Max 3).")
            else:
                quantita = len(riferimento_date) if dati_u['Contratto'] == "Guardia" else round(len(riferimento_date)*ORE_GIORNATA_FIDUCIARI, 2)
                nuova_prenotazione = pd.DataFrame([[user_attuale, str(data_inizio), str(data_fine), tipo_assenza, tipo_assenza, quantita, u_misura]], columns=df_ferie.columns)
                nuova_prenotazione.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                
                # Formato Italiano per la Mail
                inizio_it = formatta_data_it(data_inizio)
                fine_it = formatta_data_it(data_fine)
                corpo_mail = f"Nuova richiesta da: {user_attuale}\nTipo: {tipo_assenza}\nDal: {inizio_it}\nAl: {fine_it}\nValore: {quantita} {u_misura}"
                inviata = invia_email(f"Richiesta {tipo_assenza} - {user_attuale}", corpo_mail)
                
                st.success(f"Richiesta registrata per il periodo {inizio_it} - {fine_it}!")
                time.sleep(1.5); st.rerun()
