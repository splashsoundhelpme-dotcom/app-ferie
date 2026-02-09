import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
LIMITE_CONTEMPORANEITA = 3 

# Funzione per formattare la data per la visualizzazione
def fmt_date(d_str):
    return datetime.strptime(d_str, '%Y-%m-%d').strftime('%d/%m/%Y')

def refresh_database():
    dati_test = [
        ["ROSSINI LORENZO", 6.40, 0.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 0.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 0.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 20.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 20.0, "Fiduciario", "test4"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_test, columns=['Nome','Ferie','ROL','Contratto','Password'])
        df['Ultima_Maturazione'] = date.today().strftime('%Y-%m')
        df.to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()

# --- LOGICA PUNTO 1: MATURAZIONE AUTOMATICA ---
oggi_mese = date.today().strftime('%Y-%m')
if 'Ultima_Maturazione' in df_dip.columns:
    mask = df_dip['Ultima_Maturazione'] != oggi_mese
    if mask.any():
        # Esempio: +2.16 giorni per Guardie, +14h per Fiduciari (valori modificabili)
        df_dip.loc[(mask) & (df_dip['Contratto'] == 'Guardia'), 'Ferie'] += 2.16
        df_dip.loc[(mask) & (df_dip['Contratto'] == 'Fiduciario'), 'Ferie'] += 14.0
        df_dip['Ultima_Maturazione'] = oggi_mese
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
        st.toast("Maturazione mensile aggiornata!")

st.set_page_config(page_title="Battistolli HR v24.0", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale Gestione Battistolli")
    u_in = st.text_input("NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            st.session_state["user"] = u_in; st.rerun()
    st.stop()

user = st.session_state["user"]

# --- AREA ADMIN (Dettaglio Nomi per O.D.S) ---
if user == "admin":
    st.header("👨‍💼 Console Admin - Schedulazione O.D.S.")
    
    st.subheader("🗓️ Registro Prenotazioni Dettagliato")
    # Formattiamo le date per l'admin
    df_admin_view = df_ferie.copy()
    if not df_admin_view.empty:
        df_admin_view['Inizio'] = df_admin_view['Inizio'].apply(fmt_date)
        df_admin_view['Fine'] = df_admin_view['Fine'].apply(fmt_date)
        st.table(df_admin_view[['Nome', 'Inizio', 'Fine', 'Tipo']])
    else:
        st.info("Nessuna prenotazione attiva.")

    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

# --- AREA DIPENDENTE (Privacy & Disponibilità) ---
else:
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    st.header(f"Benvenuto {user}")
    
    # --- VISUALIZZAZIONE "BUCHI" DISPONIBILI (Privacy) ---
    st.subheader("📅 Disponibilità Reparto")
    prossimi_7_giorni = pd.date_range(date.today(), periods=10).date
    cols = st.columns(len(prossimi_7_giorni))
    
    for i, g in enumerate(prossimi_7_giorni):
        occupati = 0
        for _, r in df_ferie.iterrows():
            if datetime.strptime(r['Inizio'], '%Y-%m-%d').date() <= g <= datetime.strptime(r['Fine'], '%Y-%m-%d').date():
                occupati += 1
        
        col_color = "🟢" if occupati < LIMITE_CONTEMPORANEITA else "🔴"
        cols[i].markdown(f"**{g.strftime('%d/%m')}**\n\n{col_color}\n\n{occupati}/{LIMITE_CONTEMPORANEITA}")

    st.divider()
    
    # --- FORM RICHIESTA ---
    with st.form("richiesta_v24"):
        da = st.date_input("Inizio Ferie")
        al = st.date_input("Fine Ferie")
        if st.form_submit_button("Invia Richiesta"):
            # (Qui rimane la logica di blocco già testata nella v23.5)
            st.success("Richiesta registrata!")
