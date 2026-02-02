import streamlit as st

import pandas as pd

import os

from datetime import date, timedelta

import numpy as np



# --- CONFIGURAZIONE ---

PASSWORD_PAPA = "admin2024" # Password per tuo padre

PASSWORD_DIPENDENTI = "team2024" # Password comune per i dipendenti



FILE_DIPENDENTI = 'db_dipendenti.csv'

FILE_FERIE = 'db_ferie.csv'



def carica_dati():

    if not os.path.exists(FILE_DIPENDENTI):

        df_dip = pd.DataFrame(columns=['Nome', 'Ferie_Totali_Anno'])

        df_dip.to_csv(FILE_DIPENDENTI, index=False)

    else:

        df_dip = pd.read_csv(FILE_DIPENDENTI)



    if not os.path.exists(FILE_FERIE):

        df_ferie = pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Giorni'])

        df_ferie.to_csv(FILE_FERIE, index=False)

    else:

        df_ferie = pd.read_csv(FILE_FERIE)

    return df_dip, df_ferie



def calcola_giorni_lavorativi(start, end):

    return np.busday_count(start, end + timedelta(days=1))



# --- GESTIONE ACCESSO ---

if "ruolo" not in st.session_state:

    st.title("🔐 Portale Aziendale")

    pwd = st.text_input("Inserisci la password di accesso:", type="password")

    if st.button("Entra"):

        if pwd == PASSWORD_PAPA:

            st.session_state["ruolo"] = "admin"

            st.rerun()

        elif pwd == PASSWORD_DIPENDENTI:

            st.session_state["ruolo"] = "dipendente"

            st.rerun()

        else:

            st.error("Password errata")

    st.stop()



# --- LOGOUT ---

if st.sidebar.button("Logout"):

    del st.session_state["ruolo"]

    st.rerun()



df_dipendenti, df_ferie = carica_dati()



# --- INTERFACCIA DIPENDENTE ---

if st.session_state["ruolo"] == "dipendente":

    st.title("👋 Area Dipendenti")

    st.info("Benvenuto! Qui puoi inserire le tue ferie.")

    

    if df_dipendenti.empty:

        st.error("Errore: Non ci sono dipendenti registrati. Contatta l'amministratore.")

    else:

        with st.form("form_richiesta"):

            chi_sei = st.selectbox("Seleziona il tuo nome", df_dipendenti['Nome'])

            tipo = st.selectbox("Cosa vuoi richiedere?", ["Ferie", "Permesso", "Malattia"])

            c1, c2 = st.columns(2)

            inizio = c1.date_input("Inizio", date.today())

            fine = c2.date_input("Fine", date.today())

            

            if st.form_submit_button("Invia Richiesta"):

                giorni = calcola_giorni_lavorativi(inizio, fine)

                nuova = pd.DataFrame({'Nome':[chi_sei],'Inizio':[inizio],'Fine':[fine],'Tipo':[tipo],'Giorni':[giorni]})

                df_ferie = pd.concat([df_ferie, nuova], ignore_index=True)

                df_ferie.to_csv(FILE_FERIE, index=False)

                st.success(f"Richiesta inviata con successo per {giorni} giorni!")



        st.divider()

        st.subheader("Le tue ferie registrate")

        mie_ferie = df_ferie[df_ferie['Nome'] == chi_sei]

        st.dataframe(mie_ferie, use_container_width=True)



# --- INTERFACCIA PAPÀ (ADMIN) ---

elif st.session_state["ruolo"] == "admin":

    st.title("👨‍💼 Pannello Titolare")

    menu = st.sidebar.radio("Navigazione", ["Riepilogo Generale", "Gestione Personale"])

    

    if menu == "Riepilogo Generale":

        st.header("📊 Situazione Ferie")

        # Calcolo dei saldi

        riepilogo = []

        for _, row in df_dipendenti.iterrows():

            nome = row['Nome']

            tot = row['Ferie_Totali_Anno']

            usate = df_ferie[(df_ferie['Nome'] == nome) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()

            riepilogo.append({'Dipendente': nome, 'Spettanti': tot, 'Usate': usate, 'Residuo': tot - usate})

        st.table(pd.DataFrame(riepilogo))

        

        st.subheader("🔍 Dettaglio Cronologico (Tutti)")

        st.dataframe(df_ferie.sort_values(by="Inizio", ascending=False), use_container_width=True)



    elif menu == "Gestione Personale":

        st.header("👥 Configurazione")

        with st.form("aggiungi"):

            n = st.text_input("Nome Nuovo Dipendente")

            f = st.number_input("Giorni all'anno", value=26)

            if st.form_submit_button("Aggiungi"):

                new_d = pd.DataFrame({'Nome':[n], 'Ferie_Totali_Anno':[f]})

                df_dipendenti = pd.concat([df_dipendenti, new_d], ignore_index=True)

                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)

                st.rerun()
