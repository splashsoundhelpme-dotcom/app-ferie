import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- 1. CONFIGURAZIONE E MATURAZIONI ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
FILE_CONFIG = 'db_config.csv'
PASSWORD_ADMIN = "admin2024"

# Parametri di maturazione forniti
MAT_FERIE_GUARDIA = 1.917
MAT_FERIE_FIDUCIARIO = 2.16 
MAT_ROL_FIDUCIARIO = 0.60   

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

# --- 3. DATABASE INTEGRALE ---
def inizializza_database():
    elenco = [
        ["BOZZI RAFFAELLA", 258.08, 106.6, "Fiduciario", "12345", True, False],
        ["LAMADDALENA ANTONIO", 47.31, 0, "Guardia", "12345", True, False],
        ["BUQUICCHIO ANGELA", 259.03, 48.65, "Fiduciario", "12345", True, False],
        ["FIORE ANTONIO", 39.55, 0, "Guardia", "12345", True, False],
        ["PALTERA CRISTINA", 227.03, 48.65, "Fiduciario", "12345", True, False],
        ["VISTA NICOLA", 207.03, 45.6, "Fiduciario", "12345", True, False],
        ["SISTO FEDERICA", 193.91, 50.65, "Fiduciario", "12345", True, False],
        ["MANGIONE FRANCESCO", 200.25, 43.98, "Fiduciario", "12345", True, False],
        ["LOBASCIO MICHELE", 34.04, 0, "Guardia", "12345", True, False],
        ["BERGAMASCO COSIMO DAMIANO", 186.6, 47.81, "Fiduciario", "12345", True, False],
        ["GENTILE SAVERIO", 202.77, 25.62, "Fiduciario", "12345", True, False],
        ["MILILLO GENNARO", 32.60, 0, "Guardia", "12345", True, False],
        ["GIANNINI CAMILLA", 135.33, 85.08, "Fiduciario", "12345", True, False],
        ["PALERMO DOMENICO", 167.08, 48.01, "Fiduciario", "12345", True, False],
        ["MOSCA SIMONA", 166.51, 47.68, "Fiduciario", "12345", True, False],
        ["ACQUAVIVA ANNALISA", 126.4, 72.63, "Fiduciario", "12345", True, False],
        ["DILISO CLARA ANNARITA", 152.13, 44.23, "Fiduciario", "12345", True, False],
        ["ANTONACCI MARIO", 146.92, 43.98, "Fiduciario", "12345", True, False],
        ["MENGA LEONARDO", 174.0, 16.0, "Fiduciario", "12345", True, False],
        ["DI RELLA COSIMO DAMIANO", 153.41, 29.01, "Fiduciario", "12345", True, False],
        ["RANA DONATO", 146.41, 30.98, "Fiduciario", "12345", True, False],
        ["DI BARI GIORGIA", 112.76, 54.03, "Fiduciario", "12345", True, False],
        ["RAFASCHIERI ANNA ILENIA", 117.30, 32.73, "Fiduciario", "12345", True, False],
        ["BOTTALICO LEONARDO", 133.42, 9.33, "Fiduciario", "12345", True, False],
        ["DE NAPOLI SERENA", 26.49, 115.55, "Fiduciario", "12345", True, False],
        ["CAMPANILE DENNIS", 92.73, 47.85, "Fiduciario", "12345", True, False],
        ["MASTRONARDI ANNA GUENDALINA", 100.91, 27.15, "Fiduciario", "12345", True, False],
        ["ZIFARELLI ROBERTA", 72.96, 44.11, "Fiduciario", "12345", True, False],
        ["CARBONE ROBERTA", 66.64, 47.2, "Fiduciario", "12345", True, False],
        ["TRENTADUE ANNARITA", 65.95, 47.2, "Fiduciario", "12345", True, False],
        ["RENNA GIUSEPPE", 14.81, 0, "Guardia", "12345", True, False],
        ["MARTINO ALESSANDRO", 79.83, 21.12, "Fiduciario", "12345", True, False],
        ["GIORDANO DOMENICA ANNAMARIA", 53.37, 46.18, "Fiduciario", "12345", True, False],
        ["FUCCI LUCIA", 59.39, 26.15, "Fiduciario", "12345", True, False],
        ["CINQUEPALMI NICOLANTONIO", 53.69, 30.83, "Fiduciario", "12345", True, False],
        ["CISTERNINO BENITO", 93.14, -19.35, "Fiduciario", "12345", True, False],
        ["ABBATICCHIO ANTONIO", 53.13, 11.24, "Fiduciario", "12345", True, False],
        ["SANO' MORENA", 39.81, 24.0, "Fiduciario", "12345", True, False],
        ["CACUCCIOLO ROBERTA NICOLETTA", -33.95, 95.95, "Fiduciario", "12345", True, False],
        ["ROSSINI LORENZO", 6.40, 0, "Guardia", "12345", True, False],
        ["PORCARO NICOLA", 3.10, 0.64, "Fiduciario", "12345", True, False],
        ["TANGARI FRANCESCO", -39.85, 6.91, "Fiduciario", "12345", True, False]
    ]
    cols = ['Nome','Ferie','ROL','Contratto','Password','PrimoAccesso','Escluso']
    
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(elenco, columns=cols).to_csv(FILE_DIPENDENTI, index=False)
    else:
        temp_df = pd.read_csv(FILE_DIPENDENTI)
        if 'Escluso' not in temp_df.columns:
            temp_df['Escluso'] = False
            temp_df.to_csv(FILE_DIPENDENTI, index=False)
            
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

# --- 4. AVVIO APP ---
st.set_page_config(page_title="Battistolli HR v41.0", layout="wide")
df_dip, df_ferie = inizializza_database()
LIMITE_ATTUALE = carica_config()

# --- 5. LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale Battistolli")
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
        st.error("Accesso negato.")
    st.stop()

user = st.session_state["user"]

# --- 6. AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Pannello Amministrazione")
    t1, t2, t3 = st.tabs(["Registro Ferie", "Anagrafica Personale", "Impostazioni Sistema"])

    with t1:
        st.subheader("O.D.S. Attivi")
        st.dataframe(df_ferie, use_container_width=True)
        st.download_button("📥 Scarica CSV", df_ferie.to_csv(index=False), "registro_completo.csv")
        if st.button("Logout Admin"): del st.session_state["user"]; st.rerun()

    with t2:
        st.subheader("Gestione Dipendenti")
        with st.form("new_entry"):
            c1, c2 = st.columns(2)
            n_nome = c1.text_input("Cognome Nome").upper()
            n_tipo = c2.selectbox("Contratto", ["Fiduciario", "Guardia"])
            n_f = c1.number_input("Saldo Ferie Iniziale (GG)", value=0.0)
            n_r = c2.number_input("Saldo ROL Iniziale (GG)", value=0.0)
            n_excl = st.checkbox("Escludi questo utente dal limite dei blocchi (es. Uffici)")
            if st.form_submit_button("REGISTRA"):
                if n_nome:
                    nuovo_df = pd.DataFrame([[n_nome, n_f, (n_r if n_tipo=="Fiduciario" else 0), n_tipo, "12345", True, n_excl]], columns=df_dip.columns)
                    df_dip = pd.concat([df_dip, nuovo_df], ignore_index=True)
                    df_dip.to_csv(FILE_DIPENDENTI, index=False)
                    st.success("Operatore registrato!"); time.sleep(1); st.rerun()
        st.divider()
        st.dataframe(df_dip[['Nome', 'Contratto', 'Escluso', 'Ferie', 'ROL']], use_container_width=True)

    with t3:
        st.subheader("Configurazione Soglie")
        st.write(f"Limite attuale per dipendenti operativi: **{LIMITE_ATTUALE}**")
        nuovo_lim = st.slider("Seleziona limite massimo assenze contemporanee", 1, 15, LIMITE_ATTUALE)
        if st.button("Salva Configurazione"):
            salva_config(nuovo_lim)
            st.success("Limite aggiornato!"); time.sleep(1); st.rerun()

# --- 7. AREA UTENTE ---
else:
    info = df_dip[df_dip['Nome'] == user].iloc[0]
    
    # Calcolo maturazione mensile (Gennaio 2026)
    m_f = MAT_FERIE_FIDUCIARIO if info['Contratto'] == "Fiduciario" else MAT_FERIE_GUARDIA
    m_r = MAT_ROL_FIDUCIARIO if info['Contratto'] == "Fiduciario" else 0
    
    saldo_f = round((info['Ferie'] + m_f) - df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum(), 2)
    saldo_r = round((info['ROL'] + m_r) - df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum(), 2)
    
    st.header(f"Benvenuto, {user}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ferie (GG)", saldo_f)
    if info['Contratto'] == "Fiduciario":
        c2.metric("ROL (GG)", saldo_r)
    if c3.button("Esci"): del st.session_state["user"]; st.rerun()

    st.divider()
    
    # Funzione interna per contare le assenze pesanti (non escluse)
    def check_limite(giorno):
        merged = df_ferie.merge(df_dip[['Nome', 'Escluso']], on='Nome')
        occupati = merged[
            (pd.to_datetime(merged['Inizio']).dt.date <= giorno) & 
            (pd.to_datetime(merged['Fine']).dt.date >= giorno) & 
            (~merged['Tipo'].isin(["Permesso 104", "Congedo Parentale"])) &
            (merged['Escluso'] == False)
        ]
        return len(occupati)

    st.subheader(f"Stato Reparto (Soglia: {LIMITE_ATTUALE})")
    giorni_view = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols_v = st.columns(len(giorni_view))
    for i, g in enumerate(giorni_view):
        n_occ = check_limite(g)
        with cols_v[i]:
            st.write(f"**{g.strftime('%d/%m')}**")
            st.write("🟢" if n_occ < LIMITE_ATTUALE else "🔴")
            st.caption(f"{n_occ}/{LIMITE_ATTUALE}")

    st.divider()
    st.subheader("Le tue prenotazioni")
    mie_ferie = df_ferie[df_ferie['Nome'] == user]
    if mie_ferie.empty: st.info("Nessuna richiesta inserita.")
    for idx, row in mie_ferie.iterrows():
        ca, cb = st.columns([4, 1])
        ca.write(f"**{row['Tipo']}** dal {row['Inizio']} al {row['Fine']}")
        if cb.button("Annulla", key=f"del_{idx}"):
            df_ferie = df_ferie.drop(idx)
            df_ferie.to_csv(FILE_FERIE, index=False)
            invia_email(f"Richiesta CANCELLATA: {user}", f"L'utente {user} ha rimosso la richiesta di {row['Tipo']}.")
            st.rerun()

    with st.form("request_form"):
        st.subheader("Nuova Richiesta")
        opz_causali = ["Ferie", "Permesso 104", "Donazione Sangue", "Congedo Parentale"]
        if info['Contratto'] == "Fiduciario": opz_causali.insert(1, "ROL")
        sel_tipo = st.selectbox("Causale", opz_causali)
        d_dal = st.date_input("Inizio", min_value=date.today()+timedelta(days=1))
        d_al = st.date_input("Fine", min_value=date.today()+timedelta(days=1))
        
        if st.form_submit_button("INVIA O.D.S."):
            giorni_richiesti = pd.date_range(d_dal, d_al).date
            bloccato = False
            
            # Applica limite solo se l'utente non è escluso e non è 104/Congedo
            if not info['Escluso'] and sel_tipo not in ["Permesso 104", "Congedo Parentale"]:
                for d in giorni_richiesti:
                    if check_limite(d) >= LIMITE_ATTUALE:
                        bloccato = True; break
            
            if bloccato:
                st.error(f"Spiacente, per le date selezionate è già stato raggiunto il limite di {LIMITE_ATTUALE} assenze.")
            else:
                nuova_r = pd.DataFrame([[user, str(d_dal), str(d_al), sel_tipo, sel_tipo, len(giorni_richiesti), "GG"]], columns=df_ferie.columns)
                nuova_r.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                invia_email(f"Nuova Richiesta {sel_tipo}: {user}", f"{user} ha richiesto {sel_tipo} dal {d_dal} al {d_al}")
                st.success("Richiesta inviata con successo!"); time.sleep(1); st.rerun()
