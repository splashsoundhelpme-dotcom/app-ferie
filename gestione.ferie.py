import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE RIGIDA ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_STANDARD_DEFAULT = "12345"
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67
COLONNE_FERIE = ['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']

st.set_page_config(page_title="Battistolli HR Portal v9.0", layout="wide")

# --- INIZIALIZZAZIONE DATABASE ---
def inizializza_sistema():
    dati_iniziali = [
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
    
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_iniziali, columns=['Nome', 'Ferie', 'ROL'])
        df['Password'] = PASSWORD_STANDARD_DEFAULT
        df.to_csv(FILE_DIPENDENTI, index=False)
    
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
        pd.DataFrame(columns=COLONNE_FERIE).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI)

def carica_richieste():
    try:
        df = pd.read_csv(FILE_FERIE)
        return df if not df.empty else pd.DataFrame(columns=COLONNE_FERIE)
    except:
        return pd.DataFrame(columns=COLONNE_FERIE)

df_dip = inizializza_sistema()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Battistolli HR")
    u_input = st.text_input("NOME COGNOME").upper().strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("ACCEDI"):
        if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        else:
            match = df_dip[df_dip['Nome'] == u_input]
            if not match.empty and str(match.iloc[0]['Password']) == p_input:
                st.session_state["user"] = u_input; st.rerun()
            else:
                st.error("Credenziali errate.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Utente: **{st.session_state['user']}**")
    if st.session_state["user"] != "admin":
        st.divider()
        st.subheader("Sicurezza")
        npw = st.text_input("Nuova PW", type="password")
        if st.button("Aggiorna Password"):
            df_dip.loc[df_dip['Nome'] == st.session_state['user'], 'Password'] = npw
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Password salvata!")
    st.divider()
    if st.button("LOGOUT"):
        del st.session_state["user"]; st.rerun()

# --- ADMIN ---
if st.session_state["user"] == "admin":
    st.title("👨‍💼 Console Amministratore")
    t1, t2, t3 = st.tabs(["Registro", "Saldi", "Reset"])
    
    with t1:
        df_f = carica_richieste()
        st.write("### Richieste Inviate")
        st.dataframe(df_f, use_container_width=True)
        if not df_f.empty:
            idx = st.number_input("Elimina ID riga", 0, len(df_f)-1, 0)
            if st.button("Elimina"):
                df_f.drop(df_f.index[idx]).to_csv(FILE_FERIE, index=False)
                st.rerun()

    with t2:
        df_f_all = carica_richieste()
        df_res = df_dip.copy()
        def calcola(row, t):
            u = df_f_all[(df_f_all['Nome'] == row['Nome']) & (df_f_all['Risorsa'] == t)]['Ore'].sum()
            return round(row[t] - u, 2)
        df_res['Ferie_R'] = df_res.apply(lambda r: calcola(r, 'Ferie'), axis=1)
        df_res['ROL_R'] = df_res.apply(lambda r: calcola(r, 'ROL'), axis=1)
        st.dataframe(df_res[['Nome', 'Ferie_R', 'ROL_R']], use_container_width=True)
        st.download_button("Scarica Report", df_res.to_csv(index=False).encode('utf-8'), "report.csv")

    with t3:
        if st.button("RESET DATABASE"):
            pd.DataFrame(columns=COLONNE_FERIE).to_csv(FILE_FERIE, index=False); st.rerun()

# --- DIPENDENTE ---
else:
    nome_u = st.session_state["user"]
    dati_u = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_f = carica_richieste()
    
    usato_f = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_r = df_f[(df_f['Nome'] == nome_u) & (df_f['Risorsa'] == 'ROL')]['Ore'].sum()
    
    st.header(f"Ciao {nome_u}")
    c1, c2 = st.columns(2)
    c1.metric("Ferie", f"{round(dati_u['Ferie'] - usato_f, 2)} h")
    c2.metric("ROL", f"{round(dati_u['ROL'] - usato_r, 2)} h")

    with st.form("invio"):
        tipo = st.selectbox("Causale", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia"])
        risorsa = st.radio("Scala da:", ["Ferie", "ROL"], horizontal=True)
        da = st.date_input("Inizio")
        al = st.date_input("Fine")
        if st.form_submit_button("Invia Richiesta"):
            # Controllo 3 persone
            df_f['Inizio'] = pd.to_datetime(df_f['Inizio']).dt.date
            df_f['Fine'] = pd.to_datetime(df_f['Fine']).dt.date
            conflitto = False
            for g in pd.date_range(da, al).date:
                if len(df_f[(df_f['Inizio'] <= g) & (df_f['Fine'] >= g)]) >= 3 and tipo not in ["104", "Donazione Sangue"]:
                    conflitto = True; st.error(f"Pieno il {g}"); break
            
            if not conflitto:
                gg = int(np.busday_count(da, al + timedelta(days=1)))
                ore = round(gg * ORE_GIORNATA, 2)
                # SCRITTURA CORRETTA:
                nuova = pd.DataFrame([[nome_u, da, al, tipo, risorsa, ore, ""]], columns=COLONNE_FERIE)
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                st.success("Richiesta inviata all'Admin!"); time.sleep(1); st.rerun()
