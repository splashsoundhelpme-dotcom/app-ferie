import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- 1. CONFIGURAZIONE E PARAMETRI FISSI ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
FILE_CONFIG = 'db_config.csv'
PASSWORD_ADMIN = "admin2024"

# Parametri maturazione mensile (Calcolati per il 2026)
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
        # Inizializzazione forzata per scatenare la maturazione di Gennaio su Febbraio
        mese_scorso = (datetime.now().month - 1) if datetime.now().month > 1 else 12
        pd.DataFrame([{"limite": 3, "ultimo_mese": mese_scorso}]).to_csv(FILE_CONFIG, index=False)
    
    config_df = pd.read_csv(FILE_CONFIG)
    if 'ultimo_mese' not in config_df.columns:
        config_df['ultimo_mese'] = datetime.now().month
        config_df.to_csv(FILE_CONFIG, index=False)
    return config_df.iloc[0]

def salva_config(nuovo_limite, nuovo_mese):
    pd.DataFrame([{"limite": nuovo_limite, "ultimo_mese": nuovo_mese}]).to_csv(FILE_CONFIG, index=False)

# --- 3. LOGICA MATURAZIONE AUTOMATICA (Fix v49) ---
def aggiorna_maturazioni_mensili(df_dip, config):
    oggi = datetime.now()
    try:
        ultimo_mese_registrato = int(config['ultimo_mese'])
    except:
        ultimo_mese_registrato = oggi.month

    # Se il mese corrente è diverso da quello salvato, esegue la maturazione
    if oggi.month != ultimo_mese_registrato:
        st.warning(f"🔄 Rilevato cambio mese. Aggiornamento saldi per {oggi.strftime('%B %Y')}...")
        for idx, row in df_dip.iterrows():
            if row['Contratto'] == "Guardia":
                df_dip.at[idx, 'Ferie'] += MAT_FERIE_GUARDIA
            else:
                df_dip.at[idx, 'Ferie'] += MAT_FERIE_FIDUCIARIO
                df_dip.at[idx, 'ROL'] += MAT_ROL_FIDUCIARIO
        
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
        salva_config(config['limite'], oggi.month)
        st.success("Maturazione completata con successo!")
        time.sleep(2)
        st.rerun()
    return df_dip

# --- 4. INIZIALIZZAZIONE DATABASE (Anagrafica Estesa 42 Record) ---
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
        # Verifica colonne mancanti (Retrocompatibilità)
        df_e = pd.read_csv(FILE_DIPENDENTI)
        cambiato = False
        for col in cols:
            if col not in df_e.columns:
                df_e[col] = False if col == 'Escluso' else (True if col == 'PrimoAccesso' else "12345")
                cambiato = True
        if cambiato:
            df_e.to_csv(FILE_DIPENDENTI, index=False)
            
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

# --- 5. INTERFACCIA E LOGICA APPLICATIVA ---
st.set_page_config(page_title="Battistolli HR Consolidata v51.0", layout="wide")
df_dip, df_ferie = inizializza_database()
config = carica_config()

# Esecuzione Maturazione Mensile
df_dip = aggiorna_maturazioni_mensili(df_dip, config)

# --- GESTIONE SESSIONE LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale Gestione Battistolli")
    col_log_1, col_log_2 = st.columns([1, 1])
    
    with col_log_1:
        u_in = st.text_input("COGNOME NOME").strip().upper()
        p_in = st.text_input("PASSWORD", type="password").strip()
        
        if st.button("ACCEDI AL SISTEMA"):
            if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
                st.session_state["user"] = "admin"
                st.rerun()
            
            # Ricerca utente con logica parole separate
            u_words = set(u_in.split())
            for idx, row in df_dip.iterrows():
                if set(str(row['Nome']).split()) == u_words and str(row['Password']) == p_in:
                    st.session_state["user"] = row['Nome']
                    st.session_state["primo_accesso"] = row['PrimoAccesso']
                    st.rerun()
            st.error("Credenziali non valide. Riprovare.")
    st.stop()

user = st.session_state["user"]

# --- 6. AREA AMMINISTRATORE (Fix v48 Real-time) ---
if user == "admin":
    st.header("👨‍💼 Pannello Controllo Amministratore")
    tab_1, tab_2, tab_3 = st.tabs(["Registro O.D.S.", "Gestione Personale", "Configurazione Sistema"])
    
    with tab_1:
        st.subheader("Storico Richieste Totali")
        st.dataframe(df_ferie, use_container_width=True)
        if st.button("Logout Admin"):
            del st.session_state["user"]
            st.rerun()
        
    with tab_2:
        st.subheader("Editor Anagrafica e Esclusioni")
        st.info("Nota: Gli utenti con 'Escluso' attivo non saturano il limite operativo del reparto.")
        
        # Editor Tabellare con Refresh forzato
        df_editor_admin = st.data_editor(
            df_dip[['Nome', 'Contratto', 'Escluso', 'Ferie', 'ROL']],
            column_config={
                "Escluso": st.column_config.CheckboxColumn("Escluso Limiti", default=False),
                "Ferie": st.column_config.NumberColumn("Saldo Ferie"),
                "ROL": st.column_config.NumberColumn("Saldo ROL")
            },
            disabled=["Nome"], 
            use_container_width=True,
            key="master_admin_editor"
        )
        
        if st.button("💾 SALVA MODIFICHE E SINCRONIZZA"):
            df_dip.update(df_editor_admin)
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Database aggiornato istantaneamente!")
            time.sleep(1)
            st.rerun()

    with tab_3:
        st.subheader("Parametri di Soglia")
        nuova_soglia = st.slider("Limite operatori assenti contemporaneamente", 1, 15, int(config['limite']))
        if st.button("Applica Nuova Soglia"):
            salva_config(nuova_soglia, config['ultimo_mese'])
            st.success("Configurazione aggiornata!")
            st.rerun()

# --- 7. AREA UTENTE (Annullamento & Richieste) ---
else:
    # Gestione Cambio Password Obbligatorio
    if st.session_state.get("primo_accesso", False):
        st.warning("⚠️ Sicurezza: Cambio password richiesto al primo accesso.")
        pass_1 = st.text_input("Nuova Password", type="password")
        pass_2 = st.text_input("Conferma Password", type="password")
        
        if st.button("SALVA NUOVA PASSWORD"):
            if pass_1 == pass_2 and len(pass_1) > 4:
                df_dip.loc[df_dip['Nome'] == user, ['Password', 'PrimoAccesso']] = [pass_1, False]
                df_dip.to_csv(FILE_DIPENDENTI, index=False)
                st.session_state["primo_accesso"] = False
                st.success("Password aggiornata! Accesso in corso...")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Le password non corrispondono o sono troppo corte (min 5 car).")
        st.stop()

    # Recupero Info Utente e Saldi
    info_u = df_dip[df_dip['Nome'] == user].iloc[0]
    usato_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()

    st.header(f"Area Personale: {user}")
    
    # Widget Saldi
    met_1, met_2, met_3 = st.columns(3)
    met_1.metric("Saldo Ferie (GG)", round(info_u['Ferie'] - usato_f, 2))
    if info_u['Contratto'] == "Fiduciario":
        met_2.metric("Saldo ROL (GG)", round(info_u['ROL'] - usato_r, 2))
    
    if met_3.button("LOGOUT"):
        del st.session_state["user"]
        st.rerun()

    # --- LISTA RICHIESTE E ANNULLAMENTO ---
    st.subheader("Le tue prenotazioni attive")
    mie_richieste = df_ferie[df_ferie['Nome'] == user]
    
    if mie_richieste.empty:
        st.info("Non hai prenotazioni in archivio.")
    else:
        for i_rich, r_rich in mie_richieste.iterrows():
            col_info, col_btn = st.columns([5, 1])
            col_info.info(f"📅 **{r_rich['Tipo']}** | Dal: {r_rich['Inizio']} Al: {r_rich['Fine']}")
            if col_btn.button("Annulla", key=f"del_btn_{i_rich}"):
                df_ferie = df_ferie.drop(i_rich)
                df_ferie.to_csv(FILE_FERIE, index=False)
                invia_email(f"Richiesta Annullata: {user}", f"L'utente ha rimosso la richiesta di {r_rich['Tipo']} dal {r_rich['Inizio']}")
                st.rerun()

    st.divider()
    
    # LOGICA SATURAZIONE REPARTO
    def calcola_occupazione(giorno_check):
        # Merge con info dipendenti per filtrare gli esclusi
        df_m = df_ferie.merge(df_dip[['Nome', 'Escluso']], on='Nome')
        # Conto solo chi non è escluso e non ha causali speciali (104/Congedo)
        attivi = df_m[
            (pd.to_datetime(df_m['Inizio']).dt.date <= giorno_check) & 
            (pd.to_datetime(df_m['Fine']).dt.date >= giorno_check) & 
            (~df_m['Tipo'].isin(["Permesso 104", "Congedo Parentale"])) & 
            (df_m['Escluso'] == False)
        ]
        return len(attivi)

    st.subheader(f"Disponibilità Operativa (Soglia: {config['limite']})")
    prossimi_gg = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    col_gg = st.columns(len(prossimi_gg))
    
    for idx_g, gg_obj in enumerate(prossimi_gg):
        n_occupati = calcola_occupazione(gg_obj)
        with col_gg[idx_g]:
            st.write(f"**{gg_obj.strftime('%d/%m')}**")
            st.write("🟢" if n_occupati < config['limite'] else "🔴")
            st.caption(f"{n_occupati}/{config['limite']}")

    # MODULO INSERIMENTO
    with st.form("form_richiesta_hr"):
        st.subheader("Nuova Richiesta O.D.S.")
        lista_opz = ["Ferie", "Permesso 104", "Donazione Sangue", "Congedo Parentale"]
        if info_u['Contratto'] == "Fiduciario":
            lista_opz.insert(1, "ROL")
            
        c_tipo = st.selectbox("Seleziona Causale", lista_opz)
        c_dal = st.date_input("Data Inizio", min_value=date.today() + timedelta(days=1))
        c_al = st.date_input("Data Fine", min_value=date.today() + timedelta(days=1))
        
        if st.form_submit_button("INVIA RICHIESTA"):
            intervallo = pd.date_range(c_dal, c_al).date
            bloccato = False
            
            # Controllo limiti (solo se non escluso e non causale protetta)
            if not info_u['Escluso'] and c_tipo not in ["Permesso 104", "Congedo Parentale"]:
                if any(calcola_occupazione(d_p) >= config['limite'] for d_p in intervallo):
                    bloccato = True
            
            if bloccato:
                st.error(f"Spiacente, per le date selezionate è stato raggiunto il limite di {config['limite']} operatori.")
            else:
                nuova_r = pd.DataFrame([[user, str(c_dal), str(c_al), c_tipo, c_tipo, len(intervallo), "GG"]], columns=df_ferie.columns)
                nuova_r.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                invia_email(f"Nuova Richiesta {c_tipo}: {user}", f"{user} ha richiesto {c_tipo} dal {c_dal} al {c_al}")
                st.success("Richiesta inviata correttamente!")
                time.sleep(1)
                st.rerun()
