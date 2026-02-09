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
    if isinstance(data_obj, str):
        try:
            data_obj = datetime.strptime(data_obj, '%Y-%m-%d')
        except:
            return data_obj
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
        ["ABBATICCHIO ANTONIO", 10.0, 5.0, "Fiduciario", "12345"],
        ["ACQUAVIVA ANNALISA", 10.0, 5.0, "Fiduciario", "12345"],
        ["ANTONACCI MARIO", 10.0, 5.0, "Guardia", "12345"],
        ["DI RELLA COSIMO DAMIANO", 10.0, 5.0, "Guardia", "12345"],
        ["FAVIA ANTONIO", 10.0, 5.0, "Guardia", "12345"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(dati_test, columns=['Nome','Ferie','ROL','Contratto','Password']).to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()

st.set_page_config(page_title="Battistolli HR v26.4", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale Battistolli")
    u_in = st.text_input("NOME COGNOME (es: ROSSINI LORENZO)").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
            
        # Controllo flessibile del nome
        utente_trovato = False
        for nome_db in df_dip['Nome'].values:
            nome_invertito = " ".join(nome_db.split()[::-1])
            if u_in == nome_db or u_in == nome_invertito:
                pwd_corretta = str(df_dip[df_dip['Nome'] == nome_db].iloc[0]['Password'])
                if p_in == pwd_corretta:
                    st.session_state["user"] = nome_db
                    utente_trovato = True
                    break
        
        if utente_trovato:
            st.rerun()
        else:
            st.error("Credenziali non valide o utente non in lista.")
    st.stop()

user = st.session_state["user"]

# --- AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Console Amministratore")
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🚪 LOGOUT"): del st.session_state["user"]; st.rerun()
        if st.button("🗑️ RESET RICHIESTE"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
            st.rerun()
    with col_a:
        st.subheader("📋 Registro O.D.S.")
        if not df_ferie.empty:
            df_vis = df_ferie.copy()
            df_vis['Inizio'] = df_vis['Inizio'].apply(formatta_data_it)
            df_vis['Fine'] = df_vis['Fine'].apply(formatta_data_it)
            st.dataframe(df_vis, use_container_width=True)
        else: st.info("Nessuna richiesta presente.")

# --- AREA UTENTE ---
else:
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    st.header(f"Benvenuto {user}")
    
    # Calcolo Saldi
    usato_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Ferie ({unita})", round(float(dati['Ferie']) - usato_f, 2))
    c2.metric(f"ROL ({unita})", round(float(dati['ROL']) - usato_r, 2))
    if c3.button("Logout"): del st.session_state["user"]; st.rerun()

    st.divider()
    
    # Calendario Disponibilità
    st.subheader("📅 Disponibilità Reparto (Max 3)")
    giorni_monitor = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols = st.columns(len(giorni_monitor))
    for i, g in enumerate(giorni_monitor):
        occ = 0
        if not df_ferie.empty:
            occ = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g)])
        col_color = "🟢" if occ < LIMITE_CONTEMPORANEITA else "🔴"
        cols[i].markdown(f"**{g.strftime('%d/%m')}**\n\n{col_color}\n\n{occ}/{LIMITE_CONTEMPORANEITA}")

    st.divider()

    with st.form("form_richiesta"):
        tipo = st.selectbox("Cosa vuoi richiedere?", ["Ferie", "ROL"])
        domani = date.today() + timedelta(days=1)
        da = st.date_input("Dalla data", value=domani, min_value=domani)
        al = st.date_input("Alla data", value=domani, min_value=domani)
        
        if st.form_submit_button("INVIA RICHIESTA"):
            intervallo = pd.date_range(da, al).date
            conflitto = False
            for g in intervallo:
                if not df_ferie.empty:
                    if len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g)]) >= LIMITE_CONTEMPORANEITA:
                        conflitto = True; break
            
            if conflitto:
                st.error("Spiacenti, limite di 3 persone raggiunto in una delle date scelte.")
            else:
                val = len(intervallo) if dati['Contratto'] == "Guardia" else round(len(intervallo)*ORE_GIORNATA_FIDUCIARI, 2)
                nuova = pd.DataFrame([[user, str(da), str(al), tipo, tipo, val, unita]], columns=df_ferie.columns)
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                
                # Email
                da_it, al_it = formatta_data_it(da), formatta_data_it(al)
                invia_email(f"Richiesta {tipo} - {user}", f"Dipendente: {user}\nTipo: {tipo}\nDal: {da_it}\nAl: {al_it}\nValore: {val} {unita}")
                
                st.success(f"Richiesta registrata con successo dal {da_it} al {al_it}")
                time.sleep(2); st.rerun()
