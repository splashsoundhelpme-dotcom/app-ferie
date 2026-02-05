import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- COSTANTI ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67

st.set_page_config(page_title="Battistolli HR Portal v4.0", layout="wide")

# --- DATABASE REALE (44 NOMI ESATTI) ---
def inizializza_database():
    dati = [
        ["ABBATICCHIO ANTONIO", 53.13, 11.24], ["ACQUAVIVA ANNALISA", 126.40, 72.63],
        ["ANTONACCI MARIO", 146.92, 43.98], ["BERGAMASCO COSIMO DAMIANO", 186.60, 47.81],
        ["BOTTALICO LEONARDO", 133.42, 9.33], ["BOZZI RAFFAELLA", 258.08, 106.60],
        ["BUFANO GIULIO", 11.12, 0.0], ["BUQUICCHIO ANGELA", 259.03, 48.65],
        ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95], ["CAMPANILE DENNIS", 92.73, 47.85],
        ["CARBONE ROBERTA", 66.64, 47.20], ["CISTERNINO BENITO", 93.14, -19.35],
        ["DE NAPOLI SERENA", 26.49, 115.55], ["DI BARI GIORGIA", 112.76, 54.03],
        ["DILISO CLARA ANNARITA", 152.13, 44.23], ["FIORE ANTONIO", 39.56, 0.0],
        ["GIANNINI CAMILLA", 135.33, 85.08], ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18],
        ["LAMADDALENA ANTONIO", 47.32, 0.0], ["MANGIONE FRANCESCO", 200.25, 43.98],
        ["MASTRONARDI ANNA GUENDALINA", 100.92, 27.15], ["MILILLO GENNARO", 32.60, 0.0],
        ["MOSCA SIMONA", 166.51, 47.68], ["PALERMO DOMENICO", 167.08, 48.01],
        ["PALTERA CRISTINA", 227.03, 48.65], ["PORCARO NICOLA", 3.10, 0.64],
        ["PRIAMI LUCA", 33.00, 60.64], ["RAFASCHIERI ANNA ILENIA", 117.30, 32.73],
        ["RENNA GIUSEPPE", 14.81, 0.0], ["SANO' MORENA", 39.81, 24.00],
        ["SISTO FEDERICA", 193.91, 50.65], ["TANGARI FRANCESCO", -39.85, 6.91],
        ["TRENTADUE ANNARITA", 65.95, 47.20], ["VISTA NICOLA", 207.03, 45.60],
        ["ZIFARELLI ROBERTA", 72.96, 44.11], ["CINQUEPALMI NICOLANTONIO", 53.69, 30.83],
        ["DI RELLA COSIMO DAMIANO", 153.41, 29.01], ["FUCCI LUCIA", 59.39, 26.15],
        ["MARTINO ALESSANDRO", 79.83, 21.12], ["MENGA LEONARDO", 174.00, 16.00],
        ["RANA DONATO", 146.41, 30.98], ["GENTILE SAVERIO", 202.77, 25.62],
        ["LOBASCIO MICHELE", 34.04, 0.0], ["ROSSINI LORENZO", 6.40, 0.0]
    ]
    df = pd.DataFrame(dati, columns=['Nome', 'Ferie', 'ROL'])
    df['Password'] = PASSWORD_STANDARD
    df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
    return df

df_dip = inizializza_database()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Battistolli HR")
    u_input = st.text_input("NOME COGNOME").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            match = df_dip[df_dip['Nome'] == u_input]
            if not match.empty and p_input == PASSWORD_STANDARD:
                st.session_state["user"] = u_input
                st.rerun()
            else:
                st.error("Accesso negato. Verifica Nome e Password.")
    st.stop()

# --- INTERFACCIA ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()

# --- SEZIONE ADMIN ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Pannello Amministratore")
    
    t1, t2, t3 = st.tabs(["Registro Richieste", "Saldi Personale", "Reset"])
    
    with t1:
        st.subheader("Storico Assenze")
        df_f = pd.read_csv(FILE_FERIE)
        if not df_f.empty:
            st.dataframe(df_f, use_container_width=True)
            
            # ELIMINAZIONE
            st.divider()
            st.write("### Gestione Richieste")
            idx = st.number_input("Inserisci ID riga da cancellare", min_value=0, max_value=len(df_f)-1, step=1)
            if st.button("Elimina Definitivamente"):
                df_f = df_f.drop(df_f.index[idx])
                df_f.to_csv(FILE_FERIE, index=False)
                st.success("Riga eliminata correttamente.")
                time.sleep(1)
                st.rerun()
        else:
            st.info("Nessuna richiesta presente nel database.")

    with t2:
        st.subheader("Situazione Saldi Aggiornata")
        try:
            df_richieste = pd.read_csv(FILE_FERIE)
            df_res = df_dip.copy()
            
            # Calcolo sicuro dei residui
            def calcola_residuo(row, tipo):
                if df_richieste.empty: return row[tipo]
                usato = df_richieste[(df_richieste['Nome'] == row['Nome']) & (df_richieste['Risorsa'] == tipo)]['Ore'].sum()
                return round(row[tipo] - usato, 2)

            df_res['Ferie_Residue'] = df_res.apply(lambda r: calcola_residuo(r, 'Ferie'), axis=1)
            df_res['ROL_Residui'] = df_res.apply(lambda r: calcola_residuo(r, 'ROL'), axis=1)
            
            st.dataframe(df_res[['Nome', 'Ferie_Residue', 'ROL_Residui']], use_container_width=True)
            
            # Export
            csv = df_res.to_csv(index=False).encode('utf-8')
            st.download_button("Scarica Report Saldi (Excel/CSV)", csv, "situazione_personale.csv", "text/csv")
        except Exception as e:
            st.error(f"Errore nel calcolo saldi: {e}")

    with t3:
        st.warning("⚠️ Attenzione: Questa azione è irreversibile.")
        if st.button("CANCELLA TUTTO LO STORICO RICHIESTE"):
            pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
            st.success("Database richieste svuotato.")
            st.rerun()

# --- SEZIONE DIPENDENTE ---
else:
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    
    # Caricamento sicuro richieste per calcolo residuo individuale
    df_f = pd.read_csv(FILE_FERIE)
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum() if not df_f.empty else 0.0
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum() if not df_f.empty else 0.0

    st.header(f"Benvenuto {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("Saldo Ferie", f"{round(dati_u['Ferie'] - usato_f, 2)} h")
    c2.metric("Saldo ROL", f"{round(dati_u['ROL'] - usato_r, 2)} h")

    st.divider()

    with st.form("richiesta"):
        st.subheader("Nuova Richiesta")
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        inizio = st.date_input("Dalla data")
        fine = st.date_input("Alla data")
        if st.form_submit_button("INVIA"):
            # Controllo 3 persone
            conflitto = False
            if not df_f.empty:
                df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
                df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
                for g in pd.date_range(inizio, fine).date:
                    count = len(df_f[(df_f['Inizio'] <= g) & (df_f['Fine'] >= g)])
                    if count >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        conflitto = True
                        st.error(f"Limite assenze raggiunto per il giorno {g}")
                        break
            
            if not conflitto:
                gg = int(np.busday_count(inizio, fine + timedelta(days=1)))
                ore_totale = round(gg * ORE_GIORNATA, 2)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Risorsa':[risorsa],'Ore':[ore_totale],'Note':[""]})
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success("Richiesta inviata con successo!")
                time.sleep(1)
                st.rerun()
