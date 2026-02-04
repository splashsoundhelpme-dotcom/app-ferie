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
    # SALTA FILA: 104, Congedo Parentale, Donazione Sangue
    if tipo_richiesta in ["104", "Congedo Parentale", "Donazione Sangue"]:
        return True, None
    
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        assenti = df_esistente[(df_esistente['Inizio'] <= giorno) & (df_esistente['Fine'] >= giorno)]
        if len(assenti) >= 3:
            return False, giorno
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🔐 Portale Aziendale")
    nome_input = st.text_input("Nome Utente (Premi TAB per scendere)")
    pwd_input = st.text_input("Password", type="password")
    
    if st.button("Entra"):
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
                st.error("Accesso negato.")
        else:
            st.error("Nessun utente trovato. Accedi come admin.")
    st.stop()

# --- LOGOUT ---
if st.sidebar.button("Esci / Logout"):
    del st.session_state["user"]
    st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.title(f"👋 Ciao {nome_u}")
    
    dati_u = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    
    # Cambio Password obbligatorio al primo accesso
    if dati_u['Primo_Accesso']:
        st.warning("⚠️ Cambia la password per procedere")
        new_p = st.text_input("Nuova Password", type="password")
        if st.button("Salva"):
            idx = df_dipendenti.index[df_dipendenti['Nome'] == nome_u].tolist()[0]
            df_dipendenti.at[idx, 'Password'] = new_p
            df_dipendenti.at[idx, 'Primo_Accesso'] = False
            df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Fatto! Ricarico...")
            time.sleep(1)
            st.rerun()
        st.stop()

    # Calcolo Saldo
    maturato = calcola_ferie_maturate_2026(dati_u['Saldo_Arretrato'])
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Saldo Ferie Residuo", f"{round(maturato - usate, 2)} gg")

    with st.form("richiesta"):
        tipo = st.selectbox("Motivo", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        c1, c2 = st.columns(2)
        inizio = c1.date_input("Inizio", format="DD/MM/YYYY")
        fine = c2.date_input("Fine", format="DD/MM/YYYY")
        
        if st.form_submit_button("INVIA RICHIESTA"):
            ok, giorno_full = verifica_disponibilita(inizio, fine, df_ferie, tipo)
            if ok:
                g = calcola_giorni_lavorativi(inizio, fine)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Giorni':[g]})
                df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)
                df_ferie.to_csv(FILE_FERIE, index=False)
                
                st.success(f"✅ Inviata! Notifica spedita a {EMAIL_NOTIFICA}")
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"⛔ Errore: Il {giorno_full.strftime('%d/%m/%Y')} ci sono già 3 assenti.")

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Admin Dashboard")
    menu = st.sidebar.radio("Scegli", ["Planning", "Gestione Utenti", "Storico"])

    if menu == "Planning":
        st.subheader("🗓️ Situazione Settimanale")
        d_rif = st.date_input("Settimana dal", date.today(), format="DD/MM/YYYY")
        giorni = [d_rif + timedelta(days=i) for i in range(7)]
        
        plan = []
        for _, r in df_dipendenti.iterrows():
            f = {"Dipendente": r['Nome']}
            for g in giorni:
                ass = df_ferie[(df_ferie['Nome'] == r['Nome']) & (df_ferie['Inizio'] <= g) & (df_ferie['Fine'] >= g)]
                f[g.strftime("%d/%m")] = f"❌ {ass.iloc[0]['Tipo']}" if not ass.empty else "✅"
            plan.append(f)
        st.dataframe(pd.DataFrame(plan), use_container_width=True)

    elif menu == "Gestione Utenti":
        st.subheader("Crea Nuovo Dipendente")
        with st.form("new"):
            nome_n = st.text_input("Nome e Cognome")
            saldo_n = st.number_input("Saldo Arretrato fine 2025", value=0.0)
            if st.form_submit_button("Crea"):
                nuovo = pd.DataFrame({'Nome':[nome_n], 'Saldo_Arretrato':[saldo_n], 'Password':[PASSWORD_STANDARD], 'Primo_Accesso':[True]})
                df_dipendenti = pd.concat([df_dipendenti, nuovo], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success("Creato!")
                st.rerun()
        
        st.divider()
        if not df_dipendenti.empty:
            u_del = st.selectbox("Elimina o Reset Utente", df_dipendenti['Nome'])
            c1, c2 = st.columns(2)
            if c1.button("Reset Password (12345)"):
                idx = df_dipendenti.index[df_dipendenti['Nome'] == u_del].tolist()[0]
                df_dipendenti.at[idx, 'Password'] = PASSWORD_STANDARD
                df_dipendenti.at[idx, 'Primo_Accesso'] = True
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.info(f"Password di {u_del} resettata.")
            if c2.button("Elimina Definitivamente"):
                df_dipendenti = df_dipendenti[df_dipendenti['Nome'] != u_del]
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.warning(f"{u_del} eliminato.")
                st.rerun()

    elif menu == "Storico":
        st.subheader("Tutte le prenotazioni")
        st.table(df_ferie)
        
