import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
ORE_GIORNATA_FIDUCIARI = 6.67

# 1. FUNZIONE DI REFRESH (Assicura che gli utenti TEST esistano)
def refresh_database():
    dati_test_e_reali = [
        ["ROSSINI LORENZO", 6.40, 0.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 0.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 0.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 20.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 20.0, "Fiduciario", "test4"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_test_e_reali, columns=['Nome', 'Ferie', 'ROL', 'Contratto', 'Password'])
        df.to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()

st.set_page_config(page_title="Battistolli HR v23.3", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Area Test")
    u_in = st.text_input("NOME UTENTE").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            row = df_dip[df_dip['Nome'] == u_in].iloc[0]
            if str(row['Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Password errata.")
        else: st.error("Utente non trovato.")
    st.stop()

# --- INTERFACCIA UTENTE ---
user = st.session_state["user"]

if user == "admin":
    st.header("👨‍💼 Console Amministratore")
    st.write("Registro Richieste:")
    st.dataframe(df_ferie, use_container_width=True)
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()
else:
    # --- AREA RICHIESTA FERIE ---
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto {user}")
    
    # Calcolo saldo aggiornato sottraendo le richieste già fatte
    usato = df_ferie[df_ferie['Nome'] == user]['Valore'].sum()
    saldo_attuale = round(dati['Ferie'] - usato, 2)
    
    col1, col2 = st.columns(2)
    col1.metric(f"Il tuo Saldo ({unita})", saldo_attuale)
    if col2.button("Esci / Logout"): del st.session_state["user"]; st.rerun()

    st.markdown("---")
    st.subheader("📝 Inserisci Nuova Richiesta")
    
    with st.form("form_richiesta"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104"])
        da = st.date_input("Data Inizio", value=date.today())
        al = st.date_input("Data Fine", value=date.today())
        
        submit = st.form_submit_button("INVIA RICHIESTA")
        
        if submit:
            # Calcolo giorni (esclude solo le domeniche per ora)
            giorni_sel = pd.date_range(da, al).date
            g_lavorativi = len([g for g in giorni_sel if g.weekday() < 6])
            
            if g_lavorativi > 0:
                # Calcolo valore da scalare
                valore_scalo = g_lavorativi if dati['Contratto'] == "Guardia" else round(g_lavorativi * ORE_GIORNATA_FIDUCIARI, 2)
                
                if valore_scalo <= saldo_attuale:
                    nuova_riga = pd.DataFrame([[user, str(da), str(al), tipo, "Ferie", valore_scalo, unita]], 
                                             columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                    nuova_riga.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                    st.success(f"Richiesta inviata! Scalati {valore_scalo} {unita}.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Saldo insufficiente!")
            else:
                st.error("Seleziona almeno un giorno lavorativo (non domenica).")
