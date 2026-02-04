import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024" 
PASSWORD_STANDARD = "12345" 
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'

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

def verifica_disponibilita(inizio, fine, df_esistente):
    giorni_richiesti = pd.date_range(start=inizio, end=fine).date
    for giorno in giorni_richiesti:
        contatore = 0
        for _, row in df_esistente.iterrows():
            if row['Inizio'] <= giorno <= row['Fine']:
                if row['Tipo'] not in ["104", "Congedo Parentale", "Donazione Sangue"]:
                    contatore += 1
        if contatore >= 3:
            return False, giorno
    return True, None

df_dipendenti, df_ferie = carica_dati()

# --- ACCESSO ---
if "user" not in st.session_state:
    st.title("🔐 Portale Aziendale")
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
                # CORREZIONE: Variabile nome_cercato scritta correttamente
                utente = df_dipendenti[(df_dipendenti['Nome_Lower'] == nome_cercato) & (df_dipendenti['Password'].astype(str) == pwd_input)]
                
                if not utente.empty:
                    st.session_state["user"] = utente.iloc[0]['Nome']
                    st.rerun()
                else:
                    st.error("Accesso negato. Verifica Nome e Password.")
            else:
                st.error("Nessun dipendente registrato. Contatta l'amministratore.")
    st.stop()

# --- CAMBIO PASSWORD ---
if st.session_state["user"] != "admin":
    idx_l = df_dipendenti.index[df_dipendenti['Nome'] == st.session_state["user"]].tolist()
    if idx_l and df_dipendenti.at[idx_l[0], 'Primo_Accesso']:
        st.warning("🔒 Primo Accesso: Imposta una password personale.")
        n_p = st.text_input("Nuova password", type="password")
        if st.button("Salva Password"):
            if len(n_p) >= 4:
                df_dipendenti.at[idx_l[0], 'Password'] = n_p
                df_dipendenti.at[idx_l[0], 'Primo_Accesso'] = False
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success("Password salvata!")
                st.rerun()
            else:
                st.error("Minimo 4 caratteri.")
        st.stop()

if st.sidebar.button("Esci / Logout"):
    del st.session_state["user"]
    st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    st.title(f"👋 Pannello di {nome_u}")
    dati_u = df_dipendenti[df_dipendenti['Nome'] == nome_u].iloc[0]
    tot_maturato = calcola_ferie_maturate_2026(dati_u['Saldo_Arretrato'])
    usate = df_ferie[(df_ferie['Nome'] == nome_u) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    st.metric("Saldo Attuale", f"{round(tot_maturato - usate, 2)} gg")

    with st.form("form_invio"):
        motivazione = st.selectbox("Motivazione", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        inizio = st.date_input("Dalla data", format="DD/MM/YYYY")
        fine = st.date_input("Alla data", format="DD/MM/YYYY")
        if st.form_submit_button("Invia"):
            eccezioni = ["104", "Congedo Parentale", "Donazione Sangue"]
            disponibile, giorno_critico = verifica_disponibilita(inizio, fine, df_ferie)
            if motivazione in eccezioni or disponibile:
                g = calcola_giorni_lavorativi(inizio, fine)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[motivazione],'Giorni':[g]})
                df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)
                df_ferie.to_csv(FILE_FERIE, index=False)
                st.success(f"Registrato!")
                st.rerun()
            else:
                st.error(f"Saturazione il {giorno_critico.strftime('%d/%m/%Y')}")

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Portale Admin")
    menu = st.sidebar.radio("Navigazione", ["Planning Settimanale", "Storico", "Gestione Personale"])

    if menu == "Planning Settimanale":
        data_rif = st.date_input("Inizio settimana", date.today(), format="DD/MM/YYYY")
        giorni_sett = [data_rif + timedelta(days=i) for i in range(7)]
        planning_data = []
        for _, dip in df_dipendenti.iterrows():
            fila = {"Dipendente": dip['Nome']}
            for g in giorni_sett:
                ass = df_ferie[(df_ferie['Nome'] == dip['Nome']) & (df_ferie['Inizio'] <= g) & (df_ferie['Fine'] >= g)]
                fila[g.strftime("%d/%m/%Y")] = f"❌ {ass.iloc[0]['Tipo']}" if not ass.empty else "✅ Presente"
            planning_data.append(fila)
        st.dataframe(pd.DataFrame(planning_data), use_container_width=True)

    elif menu == "Storico":
        df_vis = df_ferie.copy()
        if not df_vis.empty:
            df_vis['Inizio'] = pd.to_datetime(df_vis['Inizio']).dt.strftime('%d/%m/%Y')
            df_vis['Fine'] = pd.to_datetime(df_vis['Fine']).dt.strftime('%d/%m/%Y')
            st.table(df_vis)
        else:
            st.write("Ancora nessuna richiesta registrata.")
    
    else:
        st.subheader("🆕 Aggiungi Dipendente")
        with st.form("nuovo"):
            n = st.text_input("Nome e Cognome")
            s = st.number_input("Saldo Arretrato fine 2025", value=0.0)
            if st.form_submit_button("Crea"):
                nuovo = pd.DataFrame({'Nome':[n], 'Saldo_Arretrato':[s], 'Password':[PASSWORD_STANDARD], 'Primo_Accesso':[True]})
                df_dipendenti = pd.concat([df_dipendenti, nuovo], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success("Account creato!")
                st.rerun()

        st.divider()
        if not df_dipendenti.empty:
            st.subheader("🆘 Reset Password")
            user_reset = st.selectbox("Seleziona utente per reset PW", df_dipendenti['Nome'])
            if st.button("Riporta Password a 12345"):
                idx_r = df_dipendenti.index[df_dipendenti['Nome'] == user_reset].tolist()[0]
                df_dipendenti.at[idx_r, 'Password'] = PASSWORD_STANDARD
                df_dipendenti.at[idx_r, 'Primo_Accesso'] = True
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.warning(f"Password di {user_reset} resettata.")

            st.divider()
            st.subheader("🗑️ Elimina Risorsa")
            da_elim = st.selectbox("Seleziona chi eliminare", df_dipendenti['Nome'], key="del_box")
            if st.button("Elimina Definitivamente"):
                df_dipendenti = df_dipendenti[df_dipendenti['Nome'] != da_elim]
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                df_ferie = df_ferie[df_ferie['Nome'] != da_elim]
                df_ferie.to_csv(FILE_FERIE, index=False)
                st.success(f"Eliminato {da_elim}")
                st.rerun()
