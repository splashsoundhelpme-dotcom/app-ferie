import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA_FIDUCIARI = 6.67

# Festività 2025/2026
FESTIVITA = ['2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26']

st.set_page_config(page_title="Battistolli HR - LABORATORIO TEST", layout="wide")

# --- ENGINE DATABASE ---
def inizializza_sistema():
    # Inseriamo i 4 profili test + Lorenzo Rossini
    dati_test = [
        ["ROSSINI LORENZO", 6.40, 0.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 0.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 0.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 20.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 20.0, "Fiduciario", "test4"]
    ]
    
    # Se il file non esiste o è vecchio, lo ricreiamo per includere i test
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_test, columns=['Nome', 'Ferie', 'ROL', 'Contratto', 'Password'])
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)

    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = inizializza_sistema()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Area Test Battistolli")
    u_in = st.text_input("NOME UTENTE TEST").strip().upper()
    p_in = st.text_input("PASSWORD").strip()
    
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            row = df_dip[df_dip['Nome'] == u_in].iloc[0]
            if str(row['Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
        else: st.error("Dati non validi.")
    st.stop()

# --- LOGICA APPLICATIVA ---
user = st.session_state["user"]

if user == "admin":
    st.header("👨‍💼 Console Admin - Monitoraggio Test")
    
    # Tasti rapidi
    c1, c2 = st.columns(2)
    if c1.button("🗑️ Svuota Registro Ferie (Reset Test)"):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
        st.rerun()
    if c2.button("🚪 Logout"):
        del st.session_state["user"]; st.rerun()

    # Tabella Saldi
    st.subheader("Situazione Saldi Test")
    df_view = df_dip.copy()
    for i, r in df_view.iterrows():
        usato = df_ferie[df_ferie['Nome'] == r['Nome']]['Valore'].sum()
        df_view.at[i, 'Saldo Attuale'] = round(r['Ferie'] - usato, 2)
    st.dataframe(df_view[['Nome', 'Contratto', 'Ferie', 'Saldo Attuale']], use_container_width=True)

    # Registro Richieste
    st.subheader("Registro Movimenti")
    st.dataframe(df_ferie, use_container_width=True)

else:
    # --- INTERFACCIA UTENTE TEST ---
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Profilo: {user}")
    usato = df_ferie[df_ferie['Nome'] == user]['Valore'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric(f"Saldo Residuo ({unita})", round(dati['Ferie'] - usato, 2))
    if st.button("Logout"): del st.session_state["user"]; st.rerun()

    with st.form("invio_richiesta"):
        st.write("### Simula una richiesta")
        da = st.date_input("Dal", value=date.today())
        al = st.date_input("Al", value=date.today())
        if st.form_submit_button("Invia Richiesta"):
            # Calcolo giorni lavorativi (esclude Domenica e Festivi)
            range_date = pd.date_range(da, al).date
            g_lav = 0
            for g in range_date:
                if g.weekday() < 6 and g.strftime('%Y-%m-%d') not in FESTIVITA:
                    g_lav += 1
            
            if g_lav > 0:
                valore = g_lav if dati['Contratto'] == "Guardia" else round(g_lav * ORE_GIORNATA_FIDUCIARI, 2)
                nuova = pd.DataFrame([[user, str(da), str(al), "Ferie", "Ferie", valore, unita]], 
                                    columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success(f"Richiesta salvata! Scalati {valore} {unita}")
                time.sleep(1); st.rerun()
            else:
                st.error("Il periodo selezionato non ha giorni lavorativi.")
