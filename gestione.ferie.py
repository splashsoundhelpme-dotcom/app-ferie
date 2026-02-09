import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- CONFIGURAZIONE INTEGRALE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA_FIDUCIARI = 6.67

FESTIVITA = [
    '2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', 
    '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26'
]

GUARDIE_GIURATE = ["ROSSINI LORENZO", "LAMADDALENA ANTONIO", "MILILLO GENNARO", "BUFANO GIULIO", "LOBASCIO MICHELE", "RENNA GIUSEPPE", "FIORE ANTONIO", "FAVIA ANTONIO"]

st.set_page_config(page_title="Battistolli HR v21.3", layout="wide")

# --- FUNZIONE DI VERIFICA E RIPRISTINO (Risolve i bug delle tue foto) ---
def verifica_database():
    dati_originali = [
        ["ABBATICCHIO ANTONIO", 53.13, 11.24], ["ACQUAVIVA ANNALISA", 126.40, 72.63],
        ["ANTONACCI MARIO", 146.92, 43.98], ["BERGAMASCO COSIMO DAMIANO", 186.60, 47.81],
        ["BOTTALICO LEONARDO", 133.42, 9.33], ["BOZZI RAFFAELLA", 258.08, 106.60],
        ["BUFANO GIULIO", 1.66, 0.0], ["BUQUICCHIO ANGELA", 259.03, 48.65],
        ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95], ["CAMPANILE DENNIS", 92.73, 47.85],
        ["CARBONE ROBERTA", 66.64, 47.20], ["CISTERNINO BENITO", 93.14, -19.35],
        ["DE NAPOLI SERENA", 26.49, 115.55], ["DI BARI GIORGIA", 112.76, 54.03],
        ["DILISO CLARA ANNARITA", 152.13, 44.23], ["FIORE ANTONIO", 5.93, 0.0],
        ["GIANNINI CAMILLA", 135.33, 85.08], ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18],
        ["LAMADDALENA ANTONIO", 7.09, 0.0], ["MANGIONE FRANCESCO", 200.25, 43.98],
        ["MASTRONARDI ANNA GUENDALINA", 100.92, 27.15], ["MILILLO GENNARO", 4.88, 0.0],
        ["MOSCA SIMONA", 166.51, 47.68], ["PALERMO DOMENICO", 167.08, 48.01],
        ["PALTERA CRISTINA", 227.03, 48.65], ["PORCARO NICOLA", 3.10, 0.64],
        ["PRIAMI LUCA", 33.00, 60.64], ["RAFASCHIERI ANNA ILENIA", 117.30, 32.73],
        ["RENNA GIUSEPPE", 2.22, 0.0], ["SANO' MORENA", 39.81, 24.00],
        ["SISTO FEDERICA", 193.91, 50.65], ["TANGARI FRANCESCO", -39.85, 6.91],
        ["TRENTADUE ANNARITA", 65.95, 47.20], ["VISTA NICOLA", 207.03, 45.60],
        ["ZIFARELLI ROBERTA", 72.96, 44.11], ["CINQUEPALMI NICOLANTONIO", 53.69, 30.83],
        ["DI RELLA COSIMO DAMIANO", 15.34, 29.01], ["FUCCI LUCIA", 59.39, 26.15],
        ["MARTINO ALESSANDRO", 79.83, 21.12], ["MENGA LEONARDO", 174.00, 16.00],
        ["RANA DONATO", 146.41, 30.98], ["GENTILE SAVERIO", 202.77, 25.62],
        ["LOBASCIO MICHELE", 5.10, 0.0], ["ROSSINI LORENZO", 0.96, 0.0],
        ["FAVIA ANTONIO", 0.0, 0.0]
    ]

    # Se il file non esiste o Lorenzo Rossini non è dentro, ricrealo da zero
    reset_necessario = False
    if not os.path.exists(FILE_DIPENDENTI):
        reset_necessario = True
    else:
        test_df = pd.read_csv(FILE_DIPENDENTI)
        if "ROSSINI LORENZO" not in test_df['Nome'].values or "Contratto" not in test_df.columns:
            reset_necessario = True

    if reset_necessario:
        df = pd.DataFrame(dati_originali, columns=['Nome', 'Ferie', 'ROL'])
        df['Password'] = PASSWORD_DEFAULT
        df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
        df['Ultima_Maturazione'] = datetime.now().strftime("%Y-%m")
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)

    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

# Inizializzazione sicura
df_dip, df_ferie = verifica_database()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale HR Battistolli")
    u_in = st.text_input("NOME COGNOME (es: LORENZO ROSSINI)").strip().upper()
    p_in = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            idx = df_dip.index[df_dip['Nome'] == u_in][0]
            if str(df_dip.at[idx, 'Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Password errata.")
        else:
            st.error(f"L'utente '{u_in}' non esiste. Controlla di aver scritto correttamente.")
    st.stop()

# --- LOGICA POST-LOGIN ---
nome_utente = st.session_state["user"]

with st.sidebar:
    st.write(f"Utente: **{nome_utente}**")
    if st.button("LOGOUT"):
        del st.session_state["user"]; st.rerun()

if nome_utente == "admin":
    st.header("👨‍💼 Console Admin")
    tab1, tab2 = st.tabs(["Saldi Attuali", "Storico Richieste"])
    with tab1:
        st.dataframe(df_dip, use_container_width=True)
    with tab2:
        st.dataframe(df_ferie, use_container_width=True)

else:
    # --- AREA LORENZO ROSSINI / DIPENDENTI ---
    dati = df_dip[df_dip['Nome'] == nome_utente].iloc[0]
    unita = "Giorni" if dati['Contratto'] == 'Guardia' else "Ore"
    
    # Calcolo residui leggendo dal registro ferie
    usato_f = df_ferie[(df_ferie['Nome'] == nome_utente) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == nome_utente) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    st.header(f"Ciao {nome_utente}")
    st.caption(f"Contratto: {dati['Contratto']} | Unità: {unita}")
    
    c1, c2 = st.columns(2)
    c1.metric(f"Ferie Residue ({unita})", round(dati['Ferie'] - usato_f, 2))
    c2.metric(f"ROL Residui ({unita})", round(dati['ROL'] - usato_r, 2))

    with st.form("richiesta_form"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        scelta_risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        inizio = st.date_input("Inizio periodo")
        fine = st.date_input("Fine periodo")
        
        if st.form_submit_button("Invia Richiesta"):
            giorni_lavorativi = 0
            for g in pd.date_range(inizio, fine).date:
                # Sabato incluso (weekday < 6), Domenica e Festività escluse
                if g.weekday() < 6 and g.strftime('%Y-%m-%d') not in FESTIVITA:
                    giorni_lavorativi += 1
            
            if giorni_lavorativi > 0:
                # Se Guardia scala giorni (1, 2, 3...), se Fiduciario scala ore (6.67, 13.34...)
                valore_scalo = giorni_lavorativi if dati['Contratto'] == 'Guardia' else round(giorni_lavorativi * ORE_GIORNATA_FIDUCIARI, 2)
                
                nuova_riga = pd.DataFrame([[nome_utente, str(inizio), str(fine), tipo, scelta_risorsa, valore_scalo, unita]], 
                                         columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                nuova_riga.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success(f"Richiesta salvata! Scalati {valore_scalo} {unita}.")
                time.sleep(1); st.rerun()
            else:
                st.warning("Il periodo selezionato non contiene giorni lavorativi (Domenica o Festivo).")
