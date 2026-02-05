import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE E COSTANTI ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67

st.set_page_config(page_title="Battistolli HR Portal v3.0", layout="wide", page_icon="🏢")

# --- DATABASE REALE (44 DIPENDENTI) ---
def inizializza_sistema():
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
    
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
    return df

df_dip = inizializza_sistema()

# --- GESTIONE LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale HR Battistolli")
    u_input = st.text_input("NOME COGNOME").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI", use_container_width=True):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            user_exists = df_dip[df_dip['Nome'] == u_input]
            if not user_exists.empty and p_input == PASSWORD_STANDARD:
                st.session_state["user"] = u_input
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Opzioni")
    st.info(f"Connesso: {st.session_state['user']}")
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()

# --- INTERFACCIA AMMINISTRATORE ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Dashboard Amministrativa")
    
    t1, t2, t3 = st.tabs(["Registro Richieste", "Saldi Personale", "Strumenti Reset"])
    
    with t1:
        st.subheader("Tutte le richieste di assenza")
        if os.path.exists(FILE_FERIE):
            df_f = pd.read_csv(FILE_FERIE)
            if not df_f.empty:
                filtro_nome = st.selectbox("Filtra per Dipendente", ["Tutti"] + list(df_dip['Nome'].unique()))
                if filtro_nome != "Tutti":
                    df_f = df_f[df_f['Nome'] == filtro_nome]
                
                st.dataframe(df_f, use_container_width=True)
                
                # Funzione per eliminare riga specifica
                st.divider()
                st.write("### Elimina una richiesta")
                riga_da_eliminare = st.number_input("Inserisci l'indice della riga da cancellare", min_value=0, max_value=len(df_f)-1, step=1)
                if st.button("Elimina selezionata"):
                    df_f_orig = pd.read_csv(FILE_FERIE)
                    df_f_orig = df_f_orig.drop(riga_da_eliminare)
                    df_f_orig.to_csv(FILE_FERIE, index=False)
                    st.success("Richiesta eliminata!")
                    time.sleep(1); st.rerun()
            else:
                st.info("Nessuna richiesta presente.")

    with t2:
        st.subheader("Riepilogo ore residue")
        df_f_all = pd.read_csv(FILE_FERIE)
        df_view = df_dip.copy()
        
        # Calcolo dinamico per tutti i dipendenti
        def get_residuo(row, tipo):
            usato = df_f_all[(df_f_all['Nome'] == row['Nome']) & (df_f_all['Risorsa'] == tipo)]['Ore'].sum()
            return round(row[tipo] - usato, 2)
        
        df_view['Ferie Residue'] = df_view.apply(lambda r: get_residuo(r, 'Ferie'), axis=1)
        df_view['ROL Residui'] = df_view.apply(lambda r: get_residuo(r, 'ROL'), axis=1)
        st.dataframe(df_view[['Nome', 'Ferie Residue', 'ROL Residui']], use_container_width=True)
        
        # Bottone Export
        csv = df_view.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica Report Excel (CSV)", data=csv, file_name="report_hr_battistolli.csv", mime="text/csv")

    with t3:
        st.warning("⚠️ Area Pericolosa")
        if st.button("RESET TOTALE RICHIESTE"):
            pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
            st.rerun()

# --- INTERFACCIA DIPENDENTE ---
else:
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    st.header(f"Benvenuto {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("Saldo Ferie", f"{round(dati_u['Ferie'] - usato_f, 2)} h")
    c2.metric("Saldo ROL", f"{round(dati_u['ROL'] - usato_r, 2)} h")

    st.divider()

    with st.form("invio_richiesta"):
        st.subheader("Nuova Richiesta")
        col1, col2 = st.columns(2)
        tipo = col1.selectbox("Tipo", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = col2.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        
        if st.form_submit_button("INVIA RICHIESTA"):
            if da > al:
                st.error("Date non valide.")
            else:
                # Logica Blocco 3 persone
                df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
                df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
                conflitto = False
                for g in pd.date_range(da, al).date:
                    count = len(df_f[(df_f['Inizio'] <= g) & (df_f['Fine'] >= g)])
                    if count >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        conflitto = True
                        st.error(f"Spiacenti, il giorno {g} ci sono già 3 persone assenti.")
                        break
                
                if not conflitto:
                    gg = int(np.busday_count(da, al + timedelta(days=1)))
                    ore = round(gg * ORE_GIORNATA, 2)
                    nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[da],'Fine':[al],'Tipo':[tipo],'Risorsa':[risorsa],'Ore':[ore],'Note':[""]})
                    nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                    st.success("Richiesta registrata con successo!")
                    time.sleep(1); st.rerun()
