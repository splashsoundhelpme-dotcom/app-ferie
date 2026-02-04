import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time
import smtplib
from email.mime.text import MIMEText

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024" 
PASSWORD_STANDARD = "12345" 
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'

# --- CONFIGURAZIONE EMAIL (SIMULATA - DA COMPILARE SE VUOI ATTIVARLE) ---
EMAIL_MITTENTE = "latuamail@gmail.com"
PASSWORD_APP_EMAIL = "xxxx xxxx xxxx xxxx" 
EMAIL_DESTINATARIO = "lorenzo.rossini@battistolli.it"

def carica_dati():
    if not os.path.exists(FILE_DIPENDENTI):
        df_dip = pd.DataFrame(columns=['Nome', 'Saldo_Arretrato', 'Password', 'Primo_Accesso'])
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
    if not os.path.exists(FILE_FERIE):
        df_ferie = pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Giorni'])
        df_ferie.to_csv(FILE_FERIE, index=False)
    else:
        df_ferie = pd.read_csv(FILE_FERIE)
        df_ferie['Inizio'] = pd.to_datetime(df_ferie['Inizio']).dt.date
        df_ferie['Fine'] = pd.to_datetime(df_ferie['Fine']).dt.date
    return df_dip, df_ferie

def calcola_giorni_lavorativi(start, end):
    return np.busday_count(start, end + timedelta(days=1))

def calcola_ferie_maturate_2026(saldo_arretrato):
    oggi = date.today()
    if oggi.year < 2026: return float(saldo_arretrato)
    mesi_maturati = oggi.month
    if oggi.year > 2026: mesi_maturati += (oggi.year - 2026) * 12
    return round(float(saldo_arretrato) + (mesi_maturati * 2.33), 2)

def invia_email_avviso(dipendente, inizio, fine, tipo):
    oggetto = f"Nuova Richiesta Ferie: {dipendente}"
    testo = f"Il dipendente {dipendente} ha registrato una richiesta di {tipo}\nDal: {inizio}\nAl: {fine}"
    
    # Per attivare l'invio reale, togli i commenti (#) qui sotto:
    # try:
    #     msg = MIMEText(testo)
    #     msg['Subject'] = oggetto
    #     msg['From'] = EMAIL_MITTENTE
    #     msg['To'] = EMAIL_DESTINATARIO
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()
    #     server.login(EMAIL_MITTENTE, PASSWORD_APP_EMAIL)
    #     server.sendmail(EMAIL_MITTENTE, EMAIL_DESTINATARIO, msg.as_string())
    #     server.quit()
    # except Exception as e:
    #     print(f"Errore email: {e}")
    
    # Simulazione visibile nei log del terminale
    print(f"--- EMAIL INVIATA A {EMAIL_DESTINATARIO} ---\n{testo}\n---------------------------------------------")

def verifica_disponibilita(inizio, fine, df_esistente, tipo_richiesta):
    # LISTA DEI "SALTA FILA" (AGGIUNTA DONAZIONE SANGUE)
    eccezioni = ["104", "Congedo Parentale", "Donazione Sangue"]
    
    # 1. Se è un'eccezione, passa SEMPRE
    if tipo_richiesta in eccezioni:
        return True, None
    
    # 2. Se è Ferie o Altro, controlliamo il limite
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        # Conta quanti sono già assenti in quel giorno (tutti i motivi contano per il numero)
        assenti = df_esistente[(df_esistente['Inizio'] <= giorno) & (df_esistente['Fine'] >= giorno)]
        numero_assenti = len(assenti)
        
        if numero_assenti >= 3:
            return False, giorno
            
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🔐 Portale Aziendale")
    # I campi supportano il TAB per passare dall'uno all'altro
    nome_input = st.text_input("Nome Utente")
    pwd_input = st.text_input("Password", type="password")
    
    if st.button("Entra"):
        if nome_input == "admin" and pwd_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            if not df_dipendenti.empty:
                df_dipendenti['Nome_Lower'] = df_dipendenti['Nome'].str.lower().str.strip()
                nome_cercato = nome_input.lower().strip()
                utente = df_dipendenti[(df_dipendenti['Nome_Lower'] == nome_cercato) & (df_dipendenti['Password'].astype(str) == pwd_input)]
                if not utente.empty:
                    st.session_state["user"] = utente.iloc[0]['Nome']
                    st.rerun()
                else:
                    st.error("Credenziali errate.")
            else:
                st.error("Nessun utente nel database.")
    st.stop()

# --- LOGOUT ---
if st.sidebar.button("Esci / Logout"):
    del st.session_state["user"]
    st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.title(f"👋 Ciao {nome_u}")
    
    # Primo Accesso
    dati_u = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    if dati_u['Primo_Accesso']:
        st.warning("⚠️ Primo Accesso: Imposta la tua password personale.")
        new_pass = st.text_input("Nuova Password", type="password")
        if st.button("Salva Password"):
            idx = df_dipendenti.index[df_dipendenti['Nome'] == nome_u].tolist()[0]
            df_dipendenti.at[idx, 'Password'] = new_pass
            df_dipendenti.at[idx, 'Primo_Accesso'] = False
            df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Password aggiornata! Ricarico...")
            time.sleep(1)
            st.rerun()
        st.stop()

    tot_maturato = calcola_ferie_maturate_2026(dati_u['Saldo_Arretrato'])
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Saldo Ferie Disponibile", f"{round(tot_maturato - usate, 2)} gg")

    with st.form("richiesta_form"):
        st.subheader("Nuova Richiesta")
        motivazione = st.selectbox("Motivazione", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        c1, c2 = st.columns(2)
        inizio = c1.date_input("Dal", format="DD/MM/YYYY")
        fine = c2.date_input("Al", format="DD/MM/YYYY")
        
        submitted = st.form_submit_button("Invia Richiesta")
        
        if submitted:
            # Controllo disponibilità
            disponibile, giorno_critico = verifica_disponibilita(inizio, fine, df_ferie, motivazione)
            
            if disponibile:
                giorni_calc = calcola_giorni_lavorativi(inizio, fine)
                nuova_r = pd.DataFrame({
                    'Nome': [nome_u],
                    'Inizio': [inizio],
                    'Fine': [fine],
                    'Tipo': [motivazione],
                    'Giorni': [giorni_calc]
                })
                df_ferie = pd.concat([df_ferie, nuova_r], ignore_index=True)
                df_ferie.to_csv(FILE_FERIE, index=False)
                
                # Invio notifica
                invia_email_avviso(nome_u, inizio, fine, motivazione)
                
                st.success("✅ Richiesta inviata con successo! Email di notifica inoltrata.")
                time.sleep(2) # Pausa per leggere il messaggio
                st.rerun()    # Torna alla home pulita
            else:
                st.error(f"⛔ IMPOSSIBILE PRENOTARE: Il giorno {giorno_critico.strftime('%d/%m/%Y')} è stato raggiunto il limite massimo di 3 assenze. Contatta l'amministrazione.")

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Admin Dashboard")
    menu = st.sidebar.radio("Menu", ["Planning", "Storico", "Gestione Utenti"])

    if menu == "Planning":
        st.subheader("🗓️ Planning Settimanale")
        d_rif = st.date_input("Inizio settimana", date.today(), format="DD/MM/YYYY")
        giorni = [d_rif + timedelta(days=i) for i in range(7)]
        
        data_plan = []
        for _, r in df_dipendenti.iterrows():
            row = {"Dipendente": r['Nome']}
            for g in giorni:
                res = df_ferie[(df_ferie['Nome'] == r['Nome']) & (df_ferie['Inizio'] <= g) & (df_ferie['Fine'] >= g)]
                if not res.empty:
                    tipo = res.iloc[0]['Tipo']
                    # Colore diverso per i "Salta Fila"
                    if tipo in ["104", "Congedo Parentale", "Donazione Sangue"]:
                        icon = "🔵" 
                    else:
                        icon = "❌"
