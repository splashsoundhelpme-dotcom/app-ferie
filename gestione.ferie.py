import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA_FIDUCIARI = 6.67

FESTIVITA = [
    '2025-01-01', '2025-01-06', '2025-04-21', '2025-04-25', '2025-05-01', 
    '2025-06-02', '2025-08-15', '2025-11-01', '2025-12-08', '2025-12-25', '2025-12-26'
]

# Elenco Guardie (Gestione a GIORNI)
GUARDIE_GIURATE = ["ROSSINI LORENZO", "LAMADDALENA ANTONIO", "MILILLO GENNARO", "BUFANO GIULIO", "LOBASCIO MICHELE", "RENNA GIUSEPPE", "FIORE ANTONIO", "FAVIA ANTONIO"]

st.set_page_config(page_title="Battistolli HR v22.0", layout="wide")

# --- DATABASE INTEGRALE (45 DIPENDENTI) ---
def inizializza_sistema():
    # Saldi ripristinati dai dati di Kevin
    # Per le Guardie ho inserito il valore come GIORNI (es. 6.40 per te)
    dati_base = [
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
        ["DI RELLA COSIMO DAMIANO", 15.34, 29.01], ["FUCCI LUCIA", 59.39, 26.15],
        ["MARTINO ALESSANDRO", 79.83, 21.12], ["MENGA LEONARDO", 174.00, 16.00],
        ["RANA DONATO", 146.41, 30.98], ["GENTILE SAVERIO", 202.77, 25.62],
        ["LOBASCIO MICHELE", 34.04, 0.0], ["ROSSINI LORENZO", 6.40, 0.0],
        ["FAVIA ANTONIO", 0.0, 0.0]
    ]

    # Forza creazione database pulito
    df = pd.DataFrame(dati_base, columns=['Nome', 'Ferie', 'ROL'])
    df['Password'] = PASSWORD_DEFAULT
    df['Contratto'] = df['Nome'].apply(lambda x: 'Guardia' if x in GUARDIE_GIURATE else 'Fiduciario')
    df['Ultima_Maturazione'] = datetime.now().strftime("%Y-%m")
    df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)

    return df, pd.read_csv(FILE_FERIE)

df_dip, df_ferie = inizializza_sistema()

# --- LOGIN INTELLIGENTE ---
if "user" not in st.session_state:
    st.title("🏢 Portale HR Battistolli")
    u_in = st.text_input("NOME COGNOME").strip().upper()
    p_in = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        # Controllo Admin
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        
        # Controllo Utente (riconosce anche nomi invertiti)
        successo = False
        for nome_db in df_dip['Nome'].values:
            nome_inv = " ".join(nome_db.split()[::-1])
            if u_in == nome_db or u_in == nome_inv:
                row = df_dip[df_dip['Nome'] == nome_db].iloc[0]
                if str(row['Password']) == p_in:
                    st.session_state["user"] = nome_db
                    successo = True; break
        
        if successo: st.rerun()
        else: st.error("Accesso negato. Controlla Nome o Password.")
    st.stop()

# --- INTERFACCIA ---
nome_log = st.session_state["user"]

if nome_log == "admin":
    st.header("👨‍💼 Console Amministratore")
    st.dataframe(df_dip, use_container_width=True)
    if st.button("LOGOUT"): del st.session_state["user"]; st.rerun()

else:
    dati = df_dip[df_dip['Nome'] == nome_log].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto {nome_log}")
    st.subheader(f"Contratto: {dati['Contratto']}")
    
    # Calcolo residui
    usato_f = df_ferie[(df_ferie['Nome'] == nome_log) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric(f"Ferie Residue ({unita})", round(dati['Ferie'] - usato_f, 2))
    c2.metric(f"ROL Residui ({unita})", dati['ROL'])

    with st.form("richiesta"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Malattia"])
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        if st.form_submit_button("Invia"):
            g_lav = len([g for g in pd.date_range(da, al) if g.weekday() < 6 and g.strftime('%Y-%m-%d') not in FESTIVITA])
            if g_lav > 0:
                valore = g_lav if dati['Contratto'] == "Guardia" else round(g_lav * ORE_GIORNATA_FIDUCIARI, 2)
                nuova = pd.DataFrame([[nome_log, str(da), str(al), tipo, "Ferie", valore, unita]], 
                                    columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita'])
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success(f"Richiesta inviata! Scalati {valore} {unita}")
                time.sleep(1); st.rerun()
