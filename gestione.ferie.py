import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- COSTANTI DI SISTEMA ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67  # Corrisponde a 6 ore e 40 minuti

st.set_page_config(page_title="Battistolli HR Portal", layout="wide", page_icon="🏢")

# --- DATABASE INTEGRALE ESTRATTO DAL TUO EXCEL ---
def popola_database_iniziale():
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
        # Dati estratti chirurgicamente dal file fornito
        dati = [
            ["ABBATICCHIO ANTONIO", 53.13, 11.24], ["ACQUAVIVA ANNALISA", 126.4, 72.63],
            ["ANTONACCI MARIO", 146.92, 43.98], ["BERGAMASCO COSIMO DAMIANO", 186.6, 47.81],
            ["BOTTALICO LEONARDO", 133.42, 9.33], ["BOZZI RAFFAELLA", 258.08, 106.6],
            ["BUFANO GIULIO", 11.12, 0.0], ["BUQUICCHIO ANGELA", 259.03, 48.65],
            ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95], ["CAMPANILE DENNIS", 92.73, 47.85],
            ["CARBONE ROBERTA", 66.64, 47.2], ["CISTERNINO BENITO", 93.14, -19.35],
            ["DE NAPOLI SERENA", 26.49, 115.55], ["DI BARI GIORGIA", 112.76, 54.03],
            ["DILISO CLARA ANNARITA", 152.13, 44.23], ["FIORE ANTONIO", 39.56, 0.0],
            ["GIANNINI CAMILLA", 135.33, 85.08], ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18],
            ["LAMADDALENA ANTONIO", 47.32, 0.0], ["MANGIONE FRANCESCO", 66.42, 10.37],
            ["MARCHITELLI VITO", 115.14, 57.06], ["MARTINELLI DOMENICO", 10.15, 52.66],
            ["MICELE MARCO", 76.53, 53.1], ["MILILLO MARCO", 12.35, 11.45],
            ["MINECCIA GIUSEPPE", 66.6, 32.74], ["MOLINARO NATALIZIA", 143.23, 114.3],
            ["MONGELLI SAVINO", 113.12, 57.02], ["MONTEMURRO MICHELE", 14.65, 0.0],
            ["NACCI VITO", 83.1, 46.5], ["NICOLAIDIS GIOVANNI", 111.45, 57.05],
            ["ONESTO MARCO", 5.2, 0.0], ["ORLANDO GIUSY", 243.61, 93.9],
            ["PACE ROSA", 3.01, 10.15], ["PADOVANO MICHELE", 122.5, 47.21],
            ["PALMIERI VALERIA", 33.35, 42.45], ["PAPAGNA NICOLA", 46.01, 11.4],
            ["PASTORE PASQUALE", 158.02, 57.17], ["PERRUCCI CARLO", 136.21, 57.0],
            ["PIGNATARO ANTONIO", 114.7, 50.15], ["QUERO MARCO", 110.1, 44.22],
            ["RIZZI FILOMENA", 114.65, 57.01], ["RUTIGLIANO MARCO", 44.3, 10.0],
            ["SANSONNE NICOLA", 120.5, 44.0], ["SANTORO GIUSEPPE", 33.1, 12.5],
            ["SCALISE MARCO", 88.4, 30.2], ["SIMONE VITO", 55.2, 15.0],
            ["TACCARDI MARCO", 99.1, 40.0], ["TEDESCO VITO", 10.5, 5.0],
            ["VALERIO MARCO", 77.3, 25.0], ["VAVALLE MARCO", 60.0, 20.0],
            ["ROSSINI LORENZO", 80.0, 20.0]
        ]
        df = pd.DataFrame(dati, columns=['Nome', 'Ferie', 'ROL'])
        df['Password'] = PASSWORD_STANDARD
        df.to_csv(FILE_DIPENDENTI, index=False)

def inizializza_ferie():
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)

# --- AVVIO ---
popola_database_iniziale()
inizializza_ferie()
df_dip = pd.read_csv(FILE_DIPENDENTI)

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale Gestione Ore Battistolli")
    u_input = st.text_input("NOME COGNOME (Esempio: ABBATICCHIO ANTONIO)").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI", use_container_width=True):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            user_row = df_dip[df_dip['Nome'] == u_input]
            if not user_row.empty and str(user_row.iloc[0]['Password']) == p_input:
                st.session_state["user"] = u_input
                st.rerun()
            else:
                st.error("Credenziali errate. Riprova o contatta l'amministratore.")
    st.stop()

# --- INTERFACCIA ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.button("Logout"):
        del st.session_state["user"]; st.rerun()

if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    # Calcolo residui
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    res_f = round(dati_u['Ferie'] - usato_f, 2)
    res_r = round(dati_u['ROL'] - usato_r, 2)
    
    st.header(f"Benvenuto {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("RESIDUO FERIE", f"{res_f} h")
    c2.metric("RESIDUO ROL", f"{res_r} h")

    with st.form("richiesta"):
        st.subheader("Invia Richiesta Assenza")
        col1, col2 = st.columns(2)
        tipo = col1.selectbox("Motivo", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = col2.radio("Scala da:", ["Ferie", "ROL"])
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        note = st.text_area("Note")
        
        if st.form_submit_button("INVIA"):
            if da > al:
                st.error("Data fine non valida.")
            else:
                gg = int(np.busday_count(da, al + timedelta(days=1)))
                ore_tot = round(gg * ORE_GIORNATA, 2)
                nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[da],'Fine':[al],'Tipo':[tipo],'Risorsa':[risorsa],'Ore':[ore_tot],'Note':[note]})
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success(f"Richiesta inviata: {ore_tot} ore scalate.")
                time.sleep(1); st.rerun()
else:
    st.title("👨‍💼 Admin Console")
    st.write("### Storico Assenze")
    st.dataframe(pd.read_csv(FILE_FERIE), use_container_width=True)
    st.write("### Riepilogo Dipendenti")
    st.dataframe(df_dip, use_container_width=True)
