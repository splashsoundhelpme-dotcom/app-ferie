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

# Parametri maturazione mensile
MAT_FERIE_GUARDIA = 1.917
MAT_FERIE_FIDUCIARIO = 2.16 
MAT_ROL_FIDUCIARIO = 0.60   

# --- 2. FUNZIONI DI SISTEMA (EMAIL & CONFIG) ---
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
        pd.DataFrame([{"limite": 3, "ultimo_mese": datetime.now().month}]).to_csv(FILE_CONFIG, index=False)
    
    config_df = pd.read_csv(FILE_CONFIG)
    if 'ultimo_mese' not in config_df.columns:
        config_df['ultimo_mese'] = datetime.now().month
        config_df.to_csv(FILE_CONFIG, index=False)
    return config_df.iloc[0]

def salva_config(nuovo_limite, nuovo_mese):
    pd.DataFrame([{"limite": nuovo_limite, "ultimo_mese": nuovo_mese}]).to_csv(FILE_CONFIG, index=False)

# --- 3. LOGICA MATURAZIONE AUTOMATICA ---
def aggiorna_maturazioni_mensili(df_dip, config):
    oggi = datetime.now()
    try:
        ultimo_mese_registrato = int(config['ultimo_mese'])
    except:
        ultimo_mese_registrato = oggi.month

    # Se il mese corrente è diverso da quello salvato, aggiungo la maturazione
    if oggi.month != ultimo_mese_registrato:
        st.warning("🔄 Cambio mese rilevato! Aggiornamento saldi in corso...")
        for idx, row in df_dip.iterrows():
            if row['Contratto'] == "Guardia":
                df_dip.at[idx, 'Ferie'] += MAT_FERIE_GUARDIA
            else:
                df_dip.at[idx, 'Ferie'] += MAT_FERIE_FIDUCIARIO
                df_dip.at[idx, 'ROL'] += MAT_ROL_FIDUCIARIO
        
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
        salva_config(config['limite'], oggi.month)
        st.success("Saldi aggiornati con successo!")
        time.sleep(2)
        st.rerun()
    return df_dip

# --- 4. INIZIALIZZAZIONE DATABASE (42+ RECORD) ---
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
        # Verifica se mancano colonne (Escluso) in file esistente
        df_e = pd.read_csv(FILE_DIPENDENTI)
        if 'Escluso' not in df_e.columns:
            df_e['Escluso'] = False
            df_e.to_csv(FILE_DIPENDENTI, index=False)
            
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

# --- 5. AVVIO STREAMLIT ---
st.set_page_config(page_title="Battistolli HR v46.0", layout="wide")
df_dip, df_ferie = inizializza_database()
config = carica_config()
df_dip = aggiorna_maturazioni_mensili(df_dip, config)

# LOGIN
if "user" not in st.session_state:
    st.title("🏢 Gestione Personale Battistolli")
    u_in = st.text_input("COGNOME NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        # Controllo fuzzy sui nomi (separa parole)
        u_words = set(u_in.split())
        for idx, row in df_dip.iterrows():
            if set(str(row['Nome']).split()) == u_words and str(row['Password']) == p_in:
                st.session_state["user"] = row['Nome']
                st.session_state["primo_accesso"] = row['PrimoAccesso']
                st.rerun()
        st.error("Credenziali non valide.")
    st.stop()

user = st.session_state["user"]

# --- 6. AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Pannello Controllo Admin")
    t1, t2, t3 = st.tabs(["Registro Richieste", "Editor Personale (Esclusi)", "Setup Limiti"])
    
    with t1:
        st.dataframe(df_ferie, use_container_width=True)
        if st.button("Logout"): del st.session_state["user"]; st.rerun()
        
    with t2:
        st.subheader("Gestione Diretta Dipendenti")
        st.info("Qui puoi fleggare la colonna 'Escluso' per chi non deve saturare i limiti.")
        # Editor Tabellare
        df_edit = st.data_editor(
            df_dip[['Nome', 'Contratto', 'Escluso', 'Ferie', 'ROL']],
            column_config={"Escluso": st.column_config.CheckboxColumn("Escluso", default=False)},
            disabled=["Nome"], use_container_width=True, key="admin_edit"
        )
        if st.button("💾 SALVA DATABASE"):
            df_dip.update(df_edit)
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Modifiche salvate!"); time.sleep(1); st.rerun()

    with t3:
        n_lim = st.slider("Limite assenze operative contemporanee", 1, 15, int(config['limite']))
        if st.button("Salva Configurazione"):
            salva_config(n_lim, config['ultimo_mese']); st.success("Fatto!"); st.rerun()

# --- 7. AREA UTENTE ---
else:
    # Cambio password obbligatorio
    if st.session_state.get("primo_accesso", False):
        st.warning("🔒 Sicurezza: Cambia la password per il primo accesso.")
        p1 = st.text_input("Nuova Password", type="password")
        p2 = st.text_input("Conferma Password", type="password")
        if st.button("CAMBIA PASSWORD"):
            if p1 == p2 and len(p1) > 3:
                df_dip.loc[df_dip['Nome'] == user, ['Password', 'PrimoAccesso']] = [p1, False]
                df_dip.to_csv(FILE_DIPENDENTI, index=False)
                st.session_state["primo_accesso"] = False
                st.success("Password aggiornata!"); time.sleep(1); st.rerun()
            else: st.error("Errore password.")
        st.stop()

    info = df_dip[df_dip['Nome'] == user].iloc[0]
    usato_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()

    st.header(f"Benvenuto, {user}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo Ferie (GG)", round(info['Ferie'] - usato_f, 2))
    if info['Contratto'] == "Fiduciario":
        c2.metric("Saldo ROL (GG)", round(info['ROL'] - usato_r, 2))
    if c3.button("Logout"): del st.session_state["user"]; st.rerun()

    # VISUALIZZAZIONE E ANNULLAMENTO (RIPRISTINATO)
    st.subheader("Riepilogo mie richieste")
    mie_r = df_ferie[df_ferie['Nome'] == user]
    if mie_r.empty: st.info("Non hai richieste attive.")
    for i, r in mie_r.iterrows():
        col_a, col_b = st.columns([4, 1])
        col_a.write(f"📅 **{r['Tipo']}** dal {r['Inizio']} al {r['Fine']}")
        if col_b.button("Annulla", key=f"btn_{i}"):
            df_ferie = df_ferie.drop(i)
            df_ferie.to_csv(FILE_FERIE, index=False)
            invia_email(f"CANCELLAZIONE: {user}", f"Annullata richiesta {r['Tipo']} ({r['Inizio']} - {r['Fine']})")
            st.rerun()

    st.divider()
    
    # Logica Saturazione
    def check_lim(g):
        m = df_ferie.merge(df_dip[['Nome', 'Escluso']], on='Nome')
        att = m[(pd.to_datetime(m['Inizio']).dt.date <= g) & (pd.to_datetime(m['Fine']).dt.date >= g) & 
                (~m['Tipo'].isin(["Permesso 104", "Congedo Parentale"])) & (m['Escluso'] == False)]
        return len(att)

    st.subheader(f"Disponibilità Reparto (Soglia: {config['limite']})")
    gg_view = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols = st.columns(len(gg_view))
    for idx, d in enumerate(gg_view):
        n = check_lim(d)
        with cols[idx]:
            st.write(f"**{d.strftime('%d/%m')}**")
            st.write("🟢" if n < config['limite'] else "🔴")
            st.caption(f"{n}/{config['limite']}")

    with st.form("new_req"):
        st.subheader("Nuova Prenotazione")
        opz = ["Ferie", "Permesso 104", "Donazione Sangue", "Congedo Parentale"]
        if info['Contratto'] == "Fiduciario": opz.insert(1, "ROL")
        scelta = st.selectbox("Causale", opz)
        da = st.date_input("Dal", min_value=date.today()+timedelta(days=1))
        al = st.date_input("Al", min_value=date.today()+timedelta(days=1))
        
        if st.form_submit_button("INVIA O.D.S."):
            range_gg = pd.date_range(da, al).date
            if not info['Escluso'] and scelta not in ["Permesso 104", "Congedo Parentale"] and any(check_lim(d) >= config['limite'] for d in range_gg):
                st.error("Limite raggiunto per le date selezionate.")
            else:
                nuovo = pd.DataFrame([[user, str(da), str(al), scelta, scelta, len(range_gg), "GG"]], columns=df_ferie.columns)
                nuovo.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                invia_email(f"Richiesta {scelta}: {user}", f"{user} dal {da} al {al}")
                st.success("Richiesta registrata!"); time.sleep(1); st.rerun()
