import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE AZIENDALE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67  # 6 ore e 40 minuti

# Maturazione mensile 2026 (2.33gg * 6.67h)
MAT_FERIE_MESE = 15.54 
MAT_ROL_MESE = 6.0    

st.set_page_config(page_title="Battistolli HR Portal", layout="wide", page_icon="🏢")

# --- DATABASE INTEGRALE (45 NOMI DAL TUO EXCEL) ---
def popola_database_iniziale():
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
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
            ["MARCHITELLI VITO", 115.14, 57.06], ["MARTINELLI DOMENICO", 10.0, 52.6],
            ["MICELE MARCO", 76.53, 53.1], ["MILILLO MARCO", 12.35, 11.0],
            ["MINECCIA GIUSEPPE", 66.6, 32.7], ["ONESTO MARCO", 5.2, 0.0],
            ["ORLANDO GIUSY", 243.61, 93.9], ["PACE ROSA", 3.01, 10.15],
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
        df = pd.DataFrame(dati, columns=['Nome', 'Saldo_Ferie_2025', 'Saldo_ROL_2025'])
        df['Password'] = PASSWORD_STANDARD
        df['Primo_Accesso'] = True
        df.to_csv(FILE_DIPENDENTI, index=False)

def inizializza_files():
    popola_database_iniziale()
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo_A', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)

def calcola_maturazione_2026(saldo_2025, tipo="Ferie"):
    # Calcola maturazione basata sul mese corrente del 2026
    oggi = date.today()
    mesi = oggi.month if oggi.year == 2026 else (12 if oggi.year > 2026 else 0)
    quota = MAT_FERIE_MESE if tipo == "Ferie" else MAT_ROL_MESE
    return round(float(saldo_2025) + (mesi * quota), 2)

# --- AVVIO SISTEMA ---
inizializza_files()
df_dip = pd.read_csv(FILE_DIPENDENTI)

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale Risorse Umane Battistolli")
    st.markdown("### Inserisci le tue credenziali per accedere ai saldi Ore/ROL")
    
    u_input = st.text_input("Nome e Cognome (es. ABBATICCHIO ANTONIO)")
    p_input = st.text_input("Password", type="password")
    
    if st.button("ACCEDI", use_container_width=True):
        if u_input.lower() == "admin" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        else:
            df_dip['N_L'] = df_dip['Nome'].str.lower().str.strip()
            user = df_dip[(df_dip['N_L'] == u_input.lower().strip()) & (df_dip['Password'].astype(str) == p_input)]
            if not user.empty:
                st.session_state["user"] = user.iloc[0]['Nome']; st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"👤 Utente: **{st.session_state['user']}**")
    if st.button("Logout"):
        del st.session_state["user"]; st.rerun()

# --- AREA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    dati = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = pd.read_csv(FILE_FERIE)
    
    # Calcolo Saldi Attuali
    f_att = round(calcola_maturazione_2026(dati['Saldo_Ferie_2025'], "Ferie") - df_f[(df_f['Nome']==nome_u) & (df_f['Risorsa']=="Ferie")]['Ore'].sum(), 2)
    r_att = round(calcola_maturazione_2026(dati['Saldo_ROL_2025'], "ROL") - df_f[(df_f['Nome']==nome_u) & (df_f['Risorsa']=="ROL")]['Ore'].sum(), 2)
    
    st.header(f"👋 Benvenuto, {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("SALDO FERIE (Ore)", f"{f_att} h")
    c2.metric("SALDO ROL (Ore)", f"{r_att} h")

    with st.form("richiesta_form"):
        st.subheader("📝 Nuova Richiesta")
        col1, col2 = st.columns(2)
        t_ass = col1.selectbox("Motivo", ["Ferie", "104", "Donazione Sangue", "Congedo Parentale", "Altro"])
        t_ris = col2.selectbox("Usa ore da:", ["Ferie", "ROL"])
        
        d1, d2 = st.columns(2)
        da = d1.date_input("Dalla data", format="DD/MM/YYYY")
        al = d2.date_input("Alla data", format="DD/MM/YYYY")
        nota = st.text_area("Note (es. orari visita)")
        
        if st.form_submit_button("INVIA RICHIESTA"):
            if da > al:
                st.error("La data di inizio non può superare la fine.")
            else:
                # Controllo limite 3 persone
                giorni = pd.date_range(da, al).date
                conflitto = False
                df_c = pd.read_csv(FILE_FERIE)
                if not df_c.empty:
                    df_c['Inizio'] = pd.to_datetime(df_c['Inizio']).dt.date
                    df_c['Fine'] = pd.to_datetime(df_c['Fine']).dt.date
                    for g in giorni:
                        if len(df_c[(df_c['Inizio'] <= g) & (df_c['Fine'] >= g)]) >= 3:
                            if t_ass not in ["104", "Donazione Sangue"]:
                                conflitto = True; g_err = g; break
                
                if conflitto:
                    st.error(f"Limite raggiunto il {g_err.strftime('%d/%m/%Y')}")
                else:
                    gg_lav = int(np.busday_count(da, al + timedelta(days=1)))
                    ore_tot = round(gg_lav * ORE_GIORNATA, 2)
                    nuova = pd.DataFrame({'Nome':[nome_u],'Inizio':[da],'Fine':[al],'Tipo_A':[t_ass],'Risorsa':[t_ris],'Ore':[ore_tot],'Note':[nota]})
                    nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                    st.success(f"Richiesta salvata: {ore_tot} ore scalate da {t_ris}")
                    time.sleep(1); st.rerun()

# --- AREA ADMIN ---
else:
    st.title("👨‍💼 Admin Console")
    tab1, tab2 = st.tabs(["🗓️ Planning & Storico", "📊 Analisi Saldi"])
    with tab1:
        st.subheader("Storico Richieste")
        st.dataframe(pd.read_csv(FILE_FERIE), use_container_width=True)
    with tab2:
        st.subheader("Confronto Ore Residue 2025")
        st.bar_chart(df_dip.set_index("Nome")[['Saldo_Ferie_2025', 'Saldo_ROL_2025']])
