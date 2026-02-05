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
ORE_GIORNATA = 6.67

st.set_page_config(page_title="Battistolli HR Portal", layout="wide", page_icon="🏢")

# --- GENERAZIONE DATABASE REALE (DA TUO TESTO) ---
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
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
    return df

# Avvio forzato con i tuoi dati reali
df_dip = inizializza_sistema()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Personale Battistolli")
    u_input = st.text_input("NOME COGNOME").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            user_data = df_dip[df_dip['Nome'] == u_input]
            if not user_data.empty and p_input == PASSWORD_STANDARD:
                st.session_state["user"] = u_input
                st.rerun()
            else:
                st.error("Credenziali non valide. Assicurati di scrivere correttamente NOME e COGNOME.")
    st.stop()

# --- LOGICA POST-LOGIN ---
with st.sidebar:
    st.success(f"Utente: {st.session_state['user']}")
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()

if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_ferie_attuali = pd.read_csv(FILE_FERIE)
    
    # Calcolo residui sottraendo l'usato dal saldo iniziale
    usato_f = df_ferie_attuali[(df_ferie_attuali['Nome'] == nome_u) & (df_ferie_attuali['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_ferie_attuali[(df_ferie_attuali['Nome'] == nome_u) & (df_ferie_attuali['Risorsa'] == 'ROL')]['Ore'].sum()
    
    st.header(f"Pannello di {nome_u}")
    col1, col2 = st.columns(2)
    col1.metric("RESIDUO FERIE", f"{round(dati_u['Ferie'] - usato_f, 2)} ore")
    col2.metric("RESIDUO ROL", f"{round(dati_u['ROL'] - usato_r, 2)} ore")

    st.divider()

    # Form Richiesta
    with st.form("richiesta_form"):
        st.subheader("Inserisci nuova richiesta")
        tipo = st.selectbox("Motivazione", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala ore da:", ["Ferie", "ROL"], horizontal=True)
        inizio = st.date_input("Data inizio")
        fine = st.date_input("Data fine")
        note = st.text_area("Note (opzionale)")
        
        if st.form_submit_button("INVIA RICHIESTA"):
            if inizio > fine:
                st.error("La data di fine deve essere successiva a quella di inizio.")
            else:
                # Controllo Limite 3 Persone Contemporaneamente
                giorni_richiesti = pd.date_range(inizio, fine).date
                conflitto = False
                if not df_ferie_attuali.empty:
                    df_ferie_attuali['Inizio'] = pd.to_datetime(df_ferie_attuali['Inizio']).dt.date
                    df_ferie_attuali['Fine'] = pd.to_datetime(df_ferie_attuali['Fine']).dt.date
                    
                    for g in giorni_richiesti:
                        count = len(df_ferie_attuali[(df_ferie_attuali['Inizio'] <= g) & (df_ferie_attuali['Fine'] >= g)])
                        if count >= 3 and tipo not in ["104", "Donazione Sangue"]:
                            conflitto = True
                            st.error(f"Spiacenti, il giorno {g} ci sono già 3 persone assenti.")
                            break
                
                if not conflitto:
                    giorni_lav = int(np.busday_count(inizio, fine + timedelta(days=1)))
                    ore_tot = round(giorni_lav * ORE_GIORNATA, 2)
                    nuova_riga = pd.DataFrame({'Nome':[nome_u],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Risorsa':[risorsa],'Ore':[ore_tot],'Note':[note]})
                    nuova_riga.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                    st.success(f"Richiesta inviata! Totale ore scalate: {ore_tot}")
                    time.sleep(1.5)
                    st.rerun()

else:
    # SEZIONE AMMINISTRATORE
    st.title("👨‍💼 Gestione Amministrativa")
    tab1, tab2 = st.tabs(["Storico Richieste", "Anagrafica Saldi"])
    
    with tab1:
        st.write("Tutte le richieste effettuate dai dipendenti:")
        if os.path.exists(FILE_FERIE):
            st.dataframe(pd.read_csv(FILE_FERIE), use_container_width=True)
            if st.button("Resetta Registro Richieste"):
                pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
                st.rerun()

    with tab2:
        st.write("Situazione attuale dei saldi 2025:")
        st.dataframe(df_dip[['Nome', 'Ferie', 'ROL']], use_container_width=True)
