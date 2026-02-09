import streamlit as st
import pandas as pd
import os
from datetime import date, datetime
import time

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA_FIDUCIARI = 6.67

FESTIVITA = [
    '2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', 
    '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26',
    '2026-01-01', '2026-01-06', '2026-04-06', '2026-04-25', '2026-05-01',
    '2026-06-02', '2026-08-15', '2026-11-01', '2026-12-08', '2026-12-25', '2026-12-26'
]

# Elenco Guardie (Gestione a GIORNI)
GUARDIE_GIURATE = ["ROSSINI LORENZO", "LAMADDALENA ANTONIO", "MILILLO GENNARO", "BUFANO GIULIO", "LOBASCIO MICHELE", "RENNA GIUSEPPE", "FIORE ANTONIO", "FAVIA ANTONIO"]

st.set_page_config(page_title="Battistolli HR v21.1", layout="wide")

# --- DATABASE ENGINE ---
def inizializza_sistema():
    nomi_e_saldi = [
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

    # RESET FORZATO: Ad ogni salvataggio del codice, ricreiamo il file per evitare errori di login
    df = pd.DataFrame(nomi_e_saldi, columns=['Nome', 'Ferie', 'ROL'])
    df['Password'] = PASSWORD_DEFAULT
    df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
    df['Ultima_Maturazione'] = datetime.now().strftime("%Y-%m")
    df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)

    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = inizializza_sistema()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale HR Battistolli")
    # Puliamo l'input da spazi e rendiamolo maiuscolo
    u_in = st.text_input("NOME COGNOME").strip().upper()
    p_in = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            user_data = df_dip[df_dip['Nome'] == u_in].iloc[0]
            if str(user_data['Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Password errata.")
        else:
            st.error(f"Utente '{u_in}' non trovato nel database.")
    st.stop()

# --- AREA UTENTE ---
nome_loggato = st.session_state["user"]
if nome_loggato != "admin":
    # Sidebar per cambio password visibile solo dopo il login
    with st.sidebar:
        st.write(f"Utente: **{nome_loggato}**")
        nuova_pw = st.text_input("Nuova Password", type="password")
        if st.button("Salva Password"):
            df_dip.loc[df_dip['Nome'] == nome_loggato, 'Password'] = nuova_pw
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Password aggiornata!")
        if st.button("LOGOUT"):
            del st.session_state["user"]; st.rerun()

    # Contenuto principale
    dati = df_dip[df_dip['Nome'] == nome_loggato].iloc[0]
    unita = "Giorni" if dati['Contratto'] == 'Guardia' else "Ore"
    
    # Calcolo residui leggendo dal file ferie
    usato_f = df_ferie[(df_ferie['Nome'] == nome_loggato) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == nome_loggato) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    st.header(f"Ciao {nome_loggato}")
    st.info(f"Contratto: {dati['Contratto']} (Gestione in {unita})")
    
    c1, c2 = st.columns(2)
    c1.metric(f"Ferie Residue ({unita})", round(dati['Ferie'] - usato_f, 2))
    c2.metric(f"ROL Residui ({unita})", round(dati['ROL'] - usato_r, 2))

    # Form per invio (mantenendo i blocchi dei 3 utenti)
    with st.form("richiesta_form"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        
        if st.form_submit_button("Invia Richiesta"):
            giorni_lav = 0
            conflitto = False
            for g in pd.date_range(da, al).date:
                if g.weekday() < 6 and g.strftime('%Y-%m-%d') not in FESTIVITA:
                    giorni_lav += 1
                    # Controllo occupazione
                    occupati = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & 
                                            (pd.to_datetime(df_ferie['Fine']).dt.date >= g) & 
                                            (~df_ferie['Tipo'].isin(["104", "Donazione Sangue"]))])
                    if occupati >= 3 and tipo not in ["104", "Donazione Sangue"]:
                        conflitto = True; st.error(f"Giorno {g} al completo."); break
            
            if not conflitto and giorni_lav > 0:
                valore = giorni_lav if dati['Contratto'] == 'Guardia' else round(giorni_lav * ORE_GIORNATA_FIDUCIARI, 2)
                nuova = pd.DataFrame([[nome_loggato, str(da), str(al), tipo, risorsa, valore, unita]], 
                                    columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success("Richiesta inviata!"); time.sleep(1); st.rerun()

# --- ADMIN ---
else:
    with st.sidebar:
        if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()
    st.title("👨‍💼 Console Admin")
    st.dataframe(df_dip) # Qui puoi vedere tutti i nomi e le password caricate
