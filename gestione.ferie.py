import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- 1. CONFIGURAZIONE FILE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
FILE_CONFIG = 'db_config.csv'
PASSWORD_ADMIN = "admin2024"

# --- 2. FUNZIONI DI SISTEMA ---
def invia_email(oggetto, corpo):
    try:
        if "email" not in st.secrets: return False
        msg = MIMEText(corpo)
        msg['Subject'] = oggetto
        msg['From'] = st.secrets["email"]["user"]
        msg['To'] = st.secrets["email"]["admin_email"]
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["email"]["user"], st.secrets["email"]["password"])
            server.sendmail(st.secrets["email"]["user"], [msg['To']], msg.as_string())
        return True
    except: return False

def carica_config():
    if not os.path.exists(FILE_CONFIG):
        pd.DataFrame([{"limite": 3}]).to_csv(FILE_CONFIG, index=False)
    return int(pd.read_csv(FILE_CONFIG).iloc[0]['limite'])

def salva_config(nuovo_limite):
    pd.DataFrame([{"limite": nuovo_limite}]).to_csv(FILE_CONFIG, index=False)

# --- 3. DATABASE INTEGRALE (TUTTI I 42 RECORD) ---
def inizializza_database():
    elenco = [
        ["BOZZI RAFFAELLA", 258.08, 106.6, "Fiduciario", "12345", True],
        ["LAMADDALENA ANTONIO", 47.31, 0, "Guardia", "12345", True],
        ["BUQUICCHIO ANGELA", 259.03, 48.65, "Fiduciario", "12345", True],
        ["FIORE ANTONIO", 39.55, 0, "Guardia", "12345", True],
        ["PALTERA CRISTINA", 227.03, 48.65, "Fiduciario", "12345", True],
        ["VISTA NICOLA", 207.03, 45.6, "Fiduciario", "12345", True],
        ["SISTO FEDERICA", 193.91, 50.65, "Fiduciario", "12345", True],
        ["MANGIONE FRANCESCO", 200.25, 43.98, "Fiduciario", "12345", True],
        ["LOBASCIO MICHELE", 34.04, 0, "Guardia", "12345", True],
        ["BERGAMASCO COSIMO DAMIANO", 186.6, 47.81, "Fiduciario", "12345", True],
        ["GENTILE SAVERIO", 202.77, 25.62, "Fiduciario", "12345", True],
        ["MILILLO GENNARO", 32.60, 0, "Guardia", "12345", True],
        ["GIANNINI CAMILLA", 135.33, 85.08, "Fiduciario", "12345", True],
        ["PALERMO DOMENICO", 167.08, 48.01, "Fiduciario", "12345", True],
        ["MOSCA SIMONA", 166.51, 47.68, "Fiduciario", "12345", True],
        ["ACQUAVIVA ANNALISA", 126.4, 72.63, "Fiduciario", "12345", True],
        ["DILISO CLARA ANNARITA", 152.13, 44.23, "Fiduciario", "12345", True],
        ["ANTONACCI MARIO", 146.92, 43.98, "Fiduciario", "12345", True],
        ["MENGA LEONARDO", 174.0, 16.0, "Fiduciario", "12345", True],
        ["DI RELLA COSIMO DAMIANO", 153.41, 29.01, "Fiduciario", "12345", True],
        ["RANA DONATO", 146.41, 30.98, "Fiduciario", "12345", True],
        ["DI BARI GIORGIA", 112.76, 54.03, "Fiduciario", "12345", True],
        ["RAFASCHIERI ANNA ILENIA", 117.30, 32.73, "Fiduciario", "12345", True],
        ["BOTTALICO LEONARDO", 133.42, 9.33, "Fiduciario", "12345", True],
        ["DE NAPOLI SERENA", 26.49, 115.55, "Fiduciario", "12345", True],
        ["CAMPANILE DENNIS", 92.73, 47.85, "Fiduciario", "12345", True],
        ["MASTRONARDI ANNA GUENDALINA", 100.91, 27.15, "Fiduciario", "12345", True],
        ["ZIFARELLI ROBERTA", 72.96, 44.11, "Fiduciario", "12345", True],
        ["CARBONE ROBERTA", 66.64, 47.2, "Fiduciario", "12345", True],
        ["TRENTADUE ANNARITA", 65.95, 47.2, "Fiduciario", "12345", True],
        ["RENNA GIUSEPPE", 14.81, 0, "Guardia", "12345", True],
        ["MARTINO ALESSANDRO", 79.83, 21.12, "Fiduciario", "12345", True],
        ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18, "Fiduciario", "12345", True],
        ["FUCCI LUCIA", 59.39, 26.15, "Fiduciario", "12345", True],
        ["CINQUEPALMI NICOLANTONIO", 53.69, 30.83, "Fiduciario", "12345", True],
        ["CISTERNINO BENITO", 93.14, -19.35, "Fiduciario", "12345", True],
        ["ABBATICCHIO ANTONIO", 53.13, 11.24, "Fiduciario", "12345", True],
        ["SANO' MORENA", 39.81, 24.0, "Fiduciario", "12345", True],
        ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95, "Fiduciario", "12345", True],
        ["ROSSINI LORENZO", 6.40, 0, "Guardia", "12345", True],
        ["PORCARO NICOLA", 3.10, 0.64, "Fiduciario", "12345", True],
        ["TANGARI FRANCESCO", -39.85, 6.91, "Fiduciario", "12345", True]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(elenco, columns=['Nome','Ferie','ROL','Contratto','Password','PrimoAccesso']).to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

# --- 4. AVVIO APP ---
st.set_page_config(page_title="Battistolli HR v36.1", layout="wide")
df_dip, df_ferie = inizializza_database()
LIMITE_ATTUALE = carica_config()

# --- 5. LOGIN FLESSIBILE ---
if "user" not in st.session_state:
    st.title("🏢 Gestione Personale Battistolli")
    u_in = st.text_input("COGNOME NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        u_words = set(u_in.split())
        for idx, row in df_dip.iterrows():
            if set(str(row['Nome']).split()) == u_words and str(row['Password']) == p_in:
                st.session_state["user"] = row['Nome']
                st.session_state["primo_accesso"] = row['PrimoAccesso']
                st.rerun()
        st.error("Dati non corretti.")
    st.stop()

user = st.session_state["user"]

# --- 6. AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Pannello Admin O.D.S.")
    t1, t2, t3 = st.tabs(["Registro Richieste", "Anagrafica Operatori", "Parametri Limite"])

    with t1:
        st.dataframe(df_ferie, use_container_width=True)
        st.download_button("📥 Scarica Report CSV", df_ferie.to_csv(index=False), "report_ferie.csv")
        if st.button("Esci"): del st.session_state["user"]; st.rerun()

    with t2:
        st.subheader("Aggiungi nuovo dipendente")
        with st.form("nuovo_utente"):
            n_nome = st.text_input("Cognome Nome").upper()
            n_tipo = st.selectbox("Tipo Contratto", ["Fiduciario", "Guardia"])
            n_f = st.number_input("Saldo Ferie Iniziale", value=0.0)
            n_r = st.number_input("Saldo ROL Iniziale", value=0.0)
            if st.form_submit_button("SALVA NUOVO UTENTE"):
                if n_nome and n_nome not in df_dip['Nome'].values:
                    nuovo_row = pd.DataFrame([[n_nome, n_f, (n_r if n_tipo=="Fiduciario" else 0), n_tipo, "12345", True]], columns=df_dip.columns)
                    df_dip = pd.concat([df_dip, nuovo_row], ignore_index=True)
                    df_dip.to_csv(FILE_DIPENDENTI, index=False)
                    st.success("Utente aggiunto!"); time.sleep(1); st.rerun()
        st.divider()
        st.dataframe(df_dip[['Nome', 'Contratto', 'Ferie', 'ROL']], use_container_width=True)

    with t3:
        st.subheader("Configurazione Soglia Assenze")
        st.write(f"Limite attuale impostato a: **{LIMITE_ATTUALE}**")
        nuovo_lim = st.slider("Seleziona nuovo limite contemporaneità", 1, 10, LIMITE_ATTUALE)
        if st.button("Aggiorna Limite"):
            salva_config(nuovo_lim)
            st.success("Configurazione salvata!"); time.sleep(1); st.rerun()

# --- 7. AREA UTENTE ---
else:
    info = df_dip[df_dip['Nome'] == user].iloc[0]
    # Maturazioni (valori da definire domani)
    mat_f = info['Ferie'] + 1.83 
    mat_r = info['ROL'] + (0.90 if info['Contratto'] == "Fiduciario" else 0)
    usato_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    st.header(f"Profilo: {user}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo Ferie (GG)", round(mat_f - usato_f, 2))
    c2.metric("Saldo ROL (GG)", round(mat_r - usato_r, 2) if info['Contratto']=="Fiduciario" else "N/A")
    if c3.button("Logout"): del st.session_state["user"]; st.rerun()

    st.divider()
    st.subheader("Le mie prenotazioni")
    mie_r = df_ferie[df_ferie['Nome'] == user]
    if mie_r.empty: st.info("Nessuna richiesta presente.")
    else:
        for i, row in mie_r.iterrows():
            col_x, col_y = st.columns([4, 1])
            col_x.write(f"**{row['Tipo']}** | {row['Inizio']} -> {row['Fine']}")
            if col_y.button("Annulla", key=f"del_{i}"):
                df_ferie = df_ferie.drop(i)
                df_ferie.to_csv(FILE_FERIE, index=False)
                invia_email(f"Cancellazione: {user}", f"L'utente {user} ha annullato la richiesta di {row['Tipo']}")
                st.rerun()

    st.divider()
    st.subheader(f"Calendario Disponibilità (Soglia: {LIMITE_ATTUALE})")
    giorni = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols = st.columns(len(giorni))
    for i, g in enumerate(giorni):
        occ = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g) & (~df_ferie['Tipo'].isin(["Permesso 104", "Congedo Parentale"]))])
        with cols[i]:
            st.write(f"**{g.strftime('%d/%m')}**")
            st.write("🟢" if occ < LIMITE_ATTUALE else "🔴")
            st.caption(f"{occ}/{LIMITE_ATTUALE}")

    with st.form("invio"):
        opz = ["Ferie", "Permesso 104", "Donazione Sangue", "Congedo Parentale"]
        if info['Contratto'] == "Fiduciario": opz.insert(1, "ROL")
        tipo = st.selectbox("Causale", opz)
        d_dal = st.date_input("Inizio", min_value=date.today()+timedelta(days=1))
        d_al = st.date_input("Fine", min_value=date.today()+timedelta(days=1))
        if st.form_submit_button("Invia Richiesta"):
            range_gg = pd.date_range(d_dal, d_al).date
            conflitto = False
            if tipo not in ["Permesso 104", "Congedo Parentale"]:
                for d in range_gg:
                    if len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= d) & (pd.to_datetime(df_ferie['Fine']).dt.date >= d) & (~df_ferie['Tipo'].isin(["Permesso 104", "Congedo Parentale"]))]) >= LIMITE_ATTUALE:
                        conflitto = True; break
            if conflitto: st.error(f"Posti esauriti (max {LIMITE_ATTUALE}).")
            else:
                nuovo_f = pd.DataFrame([[user, str(d_dal), str(d_al), tipo, tipo, len(range_gg), "GG"]], columns=df_ferie.columns)
                nuovo_f.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                invia_email(f"Richiesta {tipo}: {user}", f"{user}: {tipo} dal {d_dal} al {d_al}")
                st.success("Richiesta inviata correttamente!"); time.sleep(1); st.rerun()
