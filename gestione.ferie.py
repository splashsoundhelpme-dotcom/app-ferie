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
    # REGOLA SALTA FILA: 104, Congedi e Donazione Sangue passano sempre
    if tipo_richiesta in ["104", "Congedo Parentale", "Donazione Sangue"]:
        return True, None
    
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        # Contiamo tutti gli assenti in quel giorno
        assenti = df_esistente[(df_esistente['Inizio'] <= giorno) & (df_esistente['Fine'] >= giorno)]
        if len(assenti) >= 3:
            return False, giorno
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🔐 Portale Ferie Battistolli")
    nome_input = st.text_input("Nome Utente (Premi TAB per scendere)")
    pwd_input = st.text_input("Password", type="password")
    
    if st.button("ACCEDI"):
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
            else: st.error("Credenziali errate.")
        else: st.error("Database vuoto. Accedi come admin.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.button("🚪 Logout"):
        del st.session_state["user"]
        st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.header(f"👋 Ciao {nome_u}")
    
    dati_u = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    
    # Primo Accesso
    if dati_u['Primo_Accesso']:
        st.warning("⚠️ Cambia password al primo accesso")
        n_p = st.text_input("Nuova Password", type="password")
        if st.button("Salva"):
            idx = df_dipendenti.index[df_dipendenti['Nome'] == nome_u].tolist()[0]
            df_dipendenti.at[idx, 'Password'] = n_p
            df_dipendenti.at[idx, 'Primo_Accesso'] = False
            df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
            st.rerun()
        st.stop()

    # Saldo
    maturato = calcola_ferie_maturate_2026(dati_u['Saldo_Arretrato'])
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Saldo Ferie Residuo", f"{round(maturato - usate, 2)} gg")

    with st.form("richiesta"):
        tipo = st.selectbox("Motivo", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        c1, c2 = st.columns(2)
        inizio = c1.date_input("Dal", format="DD/MM/YYYY")
        fine = c2.date_input("Al", format="DD/MM/YYYY")
        if st.form_submit_button("INVIA RICHIESTA"):
            ok, g_pieno = verifica_disponibilita(inizio, fine, df_ferie, tipo)
            if ok:
                g = calcola_giorni_lavorativi(inizio, fine)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Giorni':[g]})
                df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)
                df_ferie.to_csv(FILE_FERIE, index=False)
                st.success(f"✅ Inviata! Notifica a {EMAIL_NOTIFICA}")
                time.sleep(2)
                st.rerun()
            else: st.error(f"⛔ Limite raggiunto il {g_pieno.strftime('%d/%m/%Y')}")

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Amministrazione")
    tab1, tab2, tab3 = st.tabs(["🗓️ Planning", "🛠️ Gestione Prenotazioni", "👥 Gestione Utenti"])

    with tab1:
        d_rif = st.date_input("Settimana dal", format="DD/MM/YYYY")
        giorni = [d_rif + timedelta(days=i) for i in range(7)]
        plan = []
        for _, r in df_dipendenti.iterrows():
            f = {"Dipendente": r['Nome']}
            for g in giorni:
                ass = df_ferie[(df_ferie['Nome'] == r['Nome']) & (df_ferie['Inizio'] <= g) & (df_ferie['Fine'] >= g)]
                f[g.strftime("%d/%m")] = f"❌ {ass.iloc[0]['Tipo']}" if not ass.empty else "✅"
            plan.append(f)
        st.dataframe(pd.DataFrame(plan), use_container_width=True)

    with tab2:
        st.subheader("Elimina Richieste")
        if not df_ferie.empty:
            for i, row in df_ferie.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['Nome']}**: {row['Tipo']} ({row['Inizio'].strftime('%d/%m/%Y')} - {row['Fine'].strftime('%d/%m/%Y')})")
                if c2.button("Elimina", key=f"del_{i}"):
                    df_ferie = df_ferie.drop(i)
                    df_ferie.to_csv(FILE_FERIE, index=False)
                    st.rerun()
        else: st.info("Nessuna prenotazione.")

    with tab3:
        st.subheader("Aggiungi/Elimina Personale")
        with st.form("new_u"):
            n = st.text_input("Nome Cognome")
            s = st.number_input("Saldo Arretrato fine 2025", value=0.0)
            if st.form_submit_button("Aggiungi"):
                nuovo = pd.DataFrame({'Nome':[n], 'Saldo_Arretrato':[s], 'Password':[PASSWORD_STANDARD], 'Primo_Accesso':[True]})
                df_dipendenti = pd.concat([df_dipendenti, nuovo], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.rerun()
        
        st.divider()
        if not df_dipendenti.empty:
            u_da_canc = st.selectbox("Seleziona utente da eliminare", df_dipendenti['Nome'])
            if st.button("ELIMINA UTENTE DEFINITIVAMENTE"):
                df_dipendenti = df_dipendenti[df_dipendenti['Nome'] != u_da_canc]
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.warning(f"Utente {u_da_canc} eliminato.")
                st.rerun()
