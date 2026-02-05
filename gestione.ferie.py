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
ORE_GIORNATA = 6.67  # 6 ore e 40 minuti

st.set_page_config(page_title="Battistolli HR Portal", layout="wide", page_icon="🏢")

# --- DATABASE INTEGRALE (DATI ESTRATTI DAL TUO EXCEL) ---
def reset_database_totale():
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
        ["NACCARATO MICHELE", 83.1, 46.5], ["NICOLAIDIS GIOVANNI", 111.45, 57.05],
        ["ONESTO MARCO", 5.2, 0.0], ["ORLANDO GIUSY", 243.61, 93.9],
        ["PACE ROSA", 3.01, 10.15], ["PADOVANO MICHELE", 122.5, 47.21],
        ["PALMIERI VALERIA", 33.35, 42.45], ["PAPAGNA NICOLA", 46.01, 11.4],
        ["PASTORE PASQUALE", 158.02, 57.17], ["PERRUCCI CARLO", 136.21, 57.0],
        ["PIGNATARO ANTONIO", 114.7, 50.15], ["QUERO MARCO", 110.1, 44.22],
        ["RIZZI FILOMENA", 114.65, 57.01], ["RUTIGLIANO MARCO", 44.3, 10.0],
        ["SANSONNE NICOLA", 120.5, 44.0], ["SANTORO GIUSEPPE", 33.1, 12.5],
        ["ROSSINI LORENZO", 80.0, 20.0]
    ]
    df = pd.DataFrame(dati, columns=['Nome', 'Ferie', 'ROL'])
    df['Password'] = PASSWORD_STANDARD
    df.to_csv(FILE_DIPENDENTI, index=False)
    return df

# Controllo esistenza file
if os.path.exists(FILE_DIPENDENTI):
    df_dip = pd.read_csv(FILE_DIPENDENTI)
    # Se il file esiste ma è sbagliato (manca Rossini o Molinaro), resetta
    if "ROSSINI LORENZO" not in df_dip['Nome'].values:
        df_dip = reset_database_totale()
else:
    df_dip = reset_database_totale()

if not os.path.exists(FILE_FERIE):
    pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)

# --- LOGICA DI ACCESSO ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Battistolli HR")
    u_input = st.text_input("NOME COGNOME").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ENTRA"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        else:
            user = df_dip[df_dip['Nome'] == u_input]
            if not user.empty and str(user.iloc[0]['Password']).split('.')[0] == p_input:
                st.session_state["user"] = u_input
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# --- INTERFACCIA UTENTE ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()

if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    # Calcolo usato e residui
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    res_f = round(dati_u['Ferie'] - usato_f, 2)
    res_r = round(dati_u['ROL'] - usato_r, 2)
    
    st.header(f"Pannello Dipendente: {nome_u}")
    
    col1, col2 = st.columns(2)
    col1.metric("Ore Ferie Disponibili", f"{res_f} h")
    col2.metric("Ore ROL Disponibili", f"{res_r} h")

    st.divider()

    with st.form("nuova_richiesta"):
        st.subheader("Richiedi Assenza")
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = c2.radio("Scala da:", ["Ferie", "ROL"])
        
        d_inizio = st.date_input("Dalla data")
        d_fine = st.date_input("Alla data")
        nota = st.text_area("Note aggiuntive")
        
        if st.form_submit_button("INVIA RICHIESTA"):
            if d_inizio > d_fine:
                st.error("Errore: la data di fine è precedente all'inizio.")
            else:
                # Controllo limite 3 persone
                giorni_r = pd.date_range(d_inizio, d_fine).date
                conflitto = False
                if not df_f.empty:
                    df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
                    df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
                    for g in giorni_r:
                        contatore = len(df_f[(df_f['Inizio'] <= g) & (df_f['Fine'] >= g)])
                        if contatore >= 3 and tipo not in ["104", "Donazione Sangue"]:
                            conflitto = True
                            st.error(f"Limite raggiunto per il giorno {g}")
                            break
                
                if not conflitto:
                    gg_lav = int(np.busday_count(d_inizio, d_fine + timedelta(days=1)))
                    ore_calc = round(gg_lav * ORE_GIORNATA, 2)
                    nuova_r = pd.DataFrame({'Nome':[nome_u],'Inizio':[d_inizio],'Fine':[d_fine],'Tipo':[tipo],'Risorsa':[risorsa],'Ore':[ore_calc],'Note':[nota]})
                    nuova_r.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                    st.success(f"Richiesta registrata per {ore_calc} ore.")
                    time.sleep(1)
                    st.rerun()

# --- INTERFACCIA ADMIN ---
else:
    st.title("📊 Pannello Amministratore")
    
    tab_r, tab_d = st.tabs(["Richieste Ricevute", "Anagrafica Dipendenti"])
    
    with tab_r:
        df_visualizza = pd.read_csv(FILE_FERIE)
        st.dataframe(df_visualizza, use_container_width=True)
        if st.button("Pulisci storico richieste"):
            pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
            st.rerun()

    with tab_d:
        st.dataframe(df_dip[['Nome', 'Ferie', 'ROL']], use_container_width=True)
        if st.button("RESET FORZATO DATABASE"):
            reset_database_totale()
            st.warning("Database ripristinato ai valori originali del file Excel.")
            st.rerun()
