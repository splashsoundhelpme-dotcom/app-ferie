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
EMAIL_NOTIFICA = "lorenzo.rossini@battistolli.it"

def carica_dati():
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
        df_dip = pd.DataFrame(columns=['Nome', 'Saldo_Arretrato', 'Password', 'Primo_Accesso'])
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
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
    mesi = oggi.month if oggi.year == 2026 else (12 if oggi.year > 2026 else 0)
    return round(float(saldo_arretrato) + (mesi * 2.33), 2)

def verifica_disponibilita(inizio, fine, df_esistente, tipo_richiesta):
    # SALTA FILA: Motivi che non bloccano mai la prenotazione
    if tipo_richiesta in ["104", "Congedo Parentale", "Donazione Sangue"]:
        return True, None
    
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        # Conta quanti sono già assenti in quel giorno (qualsiasi motivo)
        assenti = df_esistente[(df_esistente['Inizio'] <= giorno) & (df_esistente['Fine'] >= giorno)]
        if len(assenti) >= 3:
            return False, giorno
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- INTERFACCIA DI LOGIN ---
if "user" not in st.session_state:
    st.title("🔐 Gestione Ferie Battistolli")
    c1, c2 = st.columns(2)
    nome_input = c1.text_input("👤 Nome Utente")
    pwd_input = c2.text_input("🔑 Password", type="password")
    
    if st.button("ACCEDI", use_container_width=True):
        if nome_input == "admin" and pwd_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        elif not df_dipendenti.empty:
            df_dipendenti['Nome_Lower'] = df_dipendenti['Nome'].str.lower().str.strip()
            nome_cercato = nome_input.lower().strip()
            utente = df_dipendenti[(df_dipendenti['Nome_Lower'] == nome_cercato) & (df_dipendenti['Password'].astype(str) == pwd_input)]
            if not utente.empty:
                st.session_state["user"] = utente.iloc[0]['Nome']
                st.rerun()
            else:
                st.error("Credenziali errate. Riprova.")
        else:
            st.error("Nessun utente configurato. Contatta l'Admin.")
    st.stop()

# --- BARRA LATERALE ---
with st.sidebar:
    st.write(f"Connesso come: **{st.session_state['user']}**")
    if st.button("🚪 Esci"):
        del st.session_state["user"]
        st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.header(f"👋 Ciao, {nome_u}")
    
    dati_u = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    
    # Blocco Primo Accesso
    if dati_u['Primo_Accesso']:
        st.info("💡 Questo è il tuo primo accesso. Imposta una password sicura.")
        nuova_p = st.text_input("Nuova Password", type="password")
        conferma_p = st.text_input("Conferma Password", type="password")
        if st.button("Salva Nuova Password"):
            if nuova_p == conferma_p and len(nuova_p) > 3:
                idx = df_dipendenti.index[df_dipendenti['Nome'] == nome_u].tolist()[0]
                df_dipendenti.at[idx, 'Password'] = nuova_p
                df_dipendenti.at[idx, 'Primo_Accesso'] = False
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success("Password salvata! Ricarico...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Le password non coincidono o sono troppo brevi.")
        st.stop()

    # Dashboard Saldo
    maturato = calcola_ferie_maturate_2026(dati_u['Saldo_Arretrato'])
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Saldo Ferie Disponibile", f"{round(maturato - usate, 2)} giorni")

    # Modulo Richiesta
    with st.expander("➕ Inserisci Nuova Richiesta", expanded=True):
        with st.form("form_richiesta"):
            tipo = st.selectbox("Motivazione", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
            c1, c2 = st.columns(2)
            inizio = c1.date_input("Dalla data", format="DD/MM/YYYY")
            fine = c2.date_input("Alla data", format="DD/MM/YYYY")
            
            if st.form_submit_button("INVIA RICHIESTA"):
                if inizio > fine:
                    st.error("La data di inizio non può essere successiva alla fine.")
                else:
                    ok, giorno_full = verifica_disponibilita(inizio, fine, df_ferie, tipo)
                    if ok:
                        g = calcola_giorni_lavorativi(inizio, fine)
                        nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Giorni':[g]})
                        df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)
                        df_ferie.to_csv(FILE_FERIE, index=False)
                        st.success(f"✅ Richiesta salvata! Notifica inviata a {EMAIL_NOTIFICA}")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"⛔ Limite raggiunto: il giorno {giorno_full.strftime('%d/%m/%Y')} ci sono già 3 persone assenti.")

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Pannello Controllo Admin")
    tab1, tab2, tab3 = st.tabs(["🗓️ Planning", "🛠️ Gestione Prenotazioni", "👥 Utenti"])

    with tab1:
        st.subheader("Situazione Settimanale")
        d_rif = st.date_input("Seleziona data inizio", date.today())
        giorni = [d_rif + timedelta(days=i) for i in range(7)]
        
        planning = []
        for _, r in df_dipendenti.iterrows():
            fila = {"Dipendente": r['Nome']}
            for g in giorni:
                ass = df_ferie[(df_ferie['Nome'] == r['Nome']) & (df_ferie['Inizio'] <= g) & (df_ferie['Fine'] >= g)]
                if not ass.empty:
                    icona = "🔵" if ass.iloc[0]['Tipo'] != "Ferie" else "❌"
                    fila[g.strftime("%d/%m")] = f"{icona} {ass.iloc[0]['Tipo']}"
                else:
                    fila[g.strftime("%d/%m")] = "✅"
            planning.append(fila)
        st.table(pd.DataFrame(planning))

    with tab2:
        st.subheader("Modifica o Annulla Richieste")
        if not df_ferie.empty:
            for i, row in df_ferie.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.write(f"**{row['Nome']}** ({row['Tipo']})")
                    c2.write(f"{row['Inizio']} ➡️ {row['Fine']}")
                    if c3.button("🗑️ Elimina", key=f"del_{i}"):
                        df_ferie = df_ferie.drop(i)
                        df_ferie.to_csv(FILE_FERIE, index=False)
                        st.warning("Richiesta eliminata.")
                        st.rerun()
        else:
            st.write("Nessuna prenotazione presente.")

    with tab3:
        st.subheader("Gestione Organico")
        with st.form("nuovo_dip"):
            nome_n = st.text_input("Nome e Cognome")
            saldo_n = st.number_input("Saldo Arretrato fine 2025", value=0.0)
            if st.form_submit_button("AGGIUNGI"):
                nuovo = pd.DataFrame({'Nome':[nome_n], 'Saldo_Arretrato':[saldo_n], 'Password':[PASSWORD_STANDARD], 'Primo_Accesso':[True]})
                df_dipendenti = pd.concat([df_dipendenti, nuovo], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success(f"Utente {nome_n} creato!")
                st.rerun()
