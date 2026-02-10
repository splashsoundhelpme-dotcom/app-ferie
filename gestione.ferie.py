import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# ==============================================================================
# 1. CONFIGURAZIONE E COSTANTI DI SISTEMA
# ==============================================================================
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE      = 'db_ferie.csv'
FILE_CONFIG     = 'db_config.csv'
PASSWORD_ADMIN  = "admin2024"

# Quote di maturazione mensile (Valori aggiornati al 2026)
MAT_FERIE_GUARDIA    = 1.917
MAT_FERIE_FIDUCIARIO = 2.16 
MAT_ROL_FIDUCIARIO   = 0.60   

# ==============================================================================
# 2. FUNZIONI DI SUPPORTO (EMAIL E CONFIGURAZIONE)
# ==============================================================================
def invia_email(oggetto, corpo):
    """Gestisce l'invio delle notifiche email all'amministratore."""
    try:
        if "email" not in st.secrets:
            return False
            
        msg = MIMEText(corpo)
        msg['Subject'] = oggetto
        msg['From'] = st.secrets["email"]["user"]
        msg['To'] = st.secrets["email"]["admin_email"]
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["email"]["user"], st.secrets["email"]["password"])
            server.sendmail(st.secrets["email"]["user"], [msg['To']], msg.as_string())
        return True
    except Exception as e:
        return False


def carica_config():
    """Carica i parametri di configurazione dal file CSV."""
    if not os.path.exists(FILE_CONFIG):
        # Inizializzazione forzata per far scattare l'aggiornamento a Febbraio
        mese_scorso = (datetime.now().month - 1) if datetime.now().month > 1 else 12
        pd.DataFrame([{"limite": 3, "ultimo_mese": mese_scorso}]).to_csv(FILE_CONFIG, index=False)
    
    config_df = pd.read_csv(FILE_CONFIG)
    
    # Controllo integrità colonne
    if 'ultimo_mese' not in config_df.columns:
        config_df['ultimo_mese'] = datetime.now().month
        config_df.to_csv(FILE_CONFIG, index=False)
        
    return config_df.iloc[0]


def salva_config(nuovo_limite, nuovo_mese):
    """Salva le impostazioni di sistema nel file di configurazione."""
    pd.DataFrame([{"limite": nuovo_limite, "ultimo_mese": nuovo_mese}]).to_csv(FILE_CONFIG, index=False)


# ==============================================================================
# 3. MOTORE DI CALCOLO MATURAZIONE (Fix v49)
# ==============================================================================
def aggiorna_maturazioni_mensili(df_dip, config):
    """Verifica se è iniziato un nuovo mese e aggiorna i saldi dei dipendenti."""
    oggi = datetime.now()
    
    try:
        ultimo_mese_registrato = int(config['ultimo_mese'])
    except:
        ultimo_mese_registrato = oggi.month

    # Confronto tra mese attuale e ultimo salvato (Esempio: 2 != 1)
    if oggi.month != ultimo_mese_registrato:
        st.warning(f"🔄 Rilevato nuovo mese: {oggi.strftime('%B %Y')}. Aggiornamento saldi...")
        
        for idx, row in df_dip.iterrows():
            if row['Contratto'] == "Guardia":
                df_dip.at[idx, 'Ferie'] += MAT_FERIE_GUARDIA
            else:
                df_dip.at[idx, 'Ferie'] += MAT_FERIE_FIDUCIARIO
                df_dip.at[idx, 'ROL'] += MAT_ROL_FIDUCIARIO
        
        # Salvataggio dati e aggiornamento stato configurazione
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
        salva_config(config['limite'], oggi.month)
        
        st.success("Saldi aggiornati con successo!")
        time.sleep(1.5)
        st.rerun()
        
    return df_dip


# ==============================================================================
# 4. INIZIALIZZAZIONE DATABASE (Anagrafica Completa 42 Record)
# ==============================================================================
def inizializza_database():
    """Crea o carica i file CSV necessari al funzionamento dell'app."""
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
        df_e = pd.read_csv(FILE_DIPENDENTI)
        # Sincronizzazione colonne mancanti
        for col in cols:
            if col not in df_e.columns:
                df_e[col] = False if col == 'Escluso' else (True if col == 'PrimoAccesso' else "12345")
        df_e.to_csv(FILE_DIPENDENTI, index=False)
            
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)


# ==============================================================================
# 5. LOGICA DI AUTENTICAZIONE (Fix v52 Rossini)
# ==============================================================================
st.set_page_config(page_title="Battistolli HR Pro v55.0", layout="wide")
df_dip, df_ferie = inizializza_database()
config = carica_config()
df_dip = aggiorna_maturazioni_mensili(df_dip, config)

# CSS Personalizzato
st.markdown("""
    <style>
    .metric-container { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; }
    .stMetric { color: #1f1f1f; }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.title("🏢 Accesso Area Riservata Battistolli")
    
    with st.container():
        u_in = st.text_input("COGNOME NOME").strip().upper()
        p_in = st.text_input("PASSWORD", type="password").strip()
        
        if st.button("ESEGUI LOGIN"):
            if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
                st.session_state["user"] = "admin"
                st.rerun()
            
            # Logic Set per gestire l'inversione Nome/Cognome (Lorenzo Rossini)
            input_set = set(u_in.split())
            
            for idx, row in df_dip.iterrows():
                db_set = set(str(row['Nome']).upper().split())
                
                if input_set == db_set and str(row['Password']) == p_in:
                    st.session_state["user"] = row['Nome']
                    st.session_state["primo_accesso"] = row['PrimoAccesso']
                    st.rerun()
                    
            st.error("Accesso negato. Verificare i dati inseriti.")
    st.stop()


user = st.session_state["user"]


# ==============================================================================
# 6. AREA AMMINISTRATORE (Pannello di Controllo)
# ==============================================================================
if user == "admin":
    st.header("👨‍💼 Gestione Amministrativa")
    
    t1, t2, t3 = st.tabs(["Monitoraggio Assenze", "Anagrafica Personale", "Impostazioni Sistema"])
    
    with t1:
        st.subheader("Registro O.D.S. Completo")
        st.dataframe(df_ferie, use_container_width=True)
        
        if st.button("Disconnetti Admin"):
            del st.session_state["user"]
            st.rerun()
            
    with t2:
        st.subheader("Modifica Dati e Saldi (Fix v48)")
        st.info("Le modifiche apportate qui sono salvate in tempo reale nel database.")
        
        df_edit = st.data_editor(
            df_dip[['Nome', 'Contratto', 'Escluso', 'Ferie', 'ROL']],
            column_config={
                "Escluso": st.column_config.CheckboxColumn("Escluso Limiti", default=False),
                "Ferie": st.column_config.NumberColumn("Ferie (GG)", format="%.2f"),
                "ROL": st.column_config.NumberColumn("ROL (GG)", format="%.2f")
            },
            disabled=["Nome"], 
            use_container_width=True, 
            key="admin_v55_editor"
        )
        
        if st.button("💾 SALVA E SINCRONIZZA"):
            df_dip.update(df_edit)
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.success("Database sincronizzato!")
            time.sleep(1)
            st.rerun()

    with t3:
        st.subheader("Parametri Operativi")
        soglia = st.slider("Numero massimo di assenze contemporanee", 1, 15, int(config['limite']))
        
        if st.button("Aggiorna Configurazione"):
            salva_config(soglia, config['ultimo_mese'])
            st.success("Parametri salvati!")
            st.rerun()


# ==============================================================================
# 7. AREA UTENTE (Richieste e Saldi Personali)
# ==============================================================================
else:
    # Gestione Cambio Password Obbligatorio
    if st.session_state.get("primo_accesso", False):
        st.warning("🔒 Sicurezza: È obbligatorio cambiare la password al primo accesso.")
        
        np1 = st.text_input("Nuova Password", type="password")
        np2 = st.text_input("Conferma Password", type="password")
        
        if st.button("IMPOSTA PASSWORD"):
            if np1 == np2 and len(np1) >= 5:
                df_dip.loc[df_dip['Nome'] == user, ['Password', 'PrimoAccesso']] = [np1, False]
                df_dip.to_csv(FILE_DIPENDENTI, index=False)
                st.session_state["primo_accesso"] = False
                st.success("Password aggiornata correttamente!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Errore: le password devono coincidere e avere almeno 5 caratteri.")
        st.stop()

    # Calcolo Saldi Attuali
    info_u = df_dip[df_dip['Nome'] == user].iloc[0]
    uso_f  = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    uso_r  = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()

    st.header(f"Benvenuto, {user}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Ferie (GG)", round(info_u['Ferie'] - uso_f, 2))
    
    if info_u['Contratto'] == "Fiduciario":
        col2.metric("Saldo ROL (GG)", round(info_u['ROL'] - uso_r, 2))
        
    if col3.button("LOGOUT"):
        del st.session_state["user"]
        st.rerun()

    # Sezione Annullamento (Fix v47)
    st.subheader("Le tue richieste attive")
    mie_rich = df_ferie[df_ferie['Nome'] == user]
    
    if mie_rich.empty:
        st.info("Non ci sono richieste in attesa.")
    else:
        for idx, r in mie_rich.iterrows():
            c_a, c_b = st.columns([5, 1])
            c_a.info(f"📅 **{r['Tipo']}** - Dal {r['Inizio']} al {r['Fine']}")
            if c_b.button("❌", key=f"del_{idx}"):
                df_ferie = df_ferie.drop(idx)
                df_ferie.to_csv(FILE_FERIE, index=False)
                invia_email(f"CANCELLAZIONE: {user}", f"Annullato {r['Tipo']} ({r['Inizio']})")
                st.rerun()

    st.divider()
    
    # Visualizzazione Disponibilità Reparto
    def check_limite(d):
        m = df_ferie.merge(df_dip[['Nome', 'Escluso']], on='Nome')
        count = m[
            (pd.to_datetime(m['Inizio']).dt.date <= d) & 
            (pd.to_datetime(m['Fine']).dt.date >= d) & 
            (~m['Tipo'].isin(["Permesso 104", "Congedo Parentale"])) & 
            (m['Escluso'] == False)
        ]
        return len(count)

    st.subheader(f"Disponibilità Personale (Limite: {config['limite']})")
    
    giorni = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols = st.columns(len(giorni))
    
    for i, g in enumerate(giorni):
        occupati = check_limite(g)
        with cols[i]:
            st.write(f"**{g.strftime('%d/%m')}**")
            st.write("🟢" if occupati < config['limite'] else "🔴")
            st.caption(f"{occupati}/{config['limite']}")

    # Form Richiesta O.D.S.
    with st.form("nuova_richiesta_ods"):
        st.subheader("Compila Nuova Richiesta")
        opz = ["Ferie", "Permesso 104", "Donazione Sangue", "Congedo Parentale"]
        if info_u['Contratto'] == "Fiduciario":
            opz.insert(1, "ROL")
            
        tipo = st.selectbox("Causale", opz)
        dal  = st.date_input("Inizio", min_value=date.today() + timedelta(days=1))
        al   = st.date_input("Fine", min_value=date.today() + timedelta(days=1))
        
        if st.form_submit_button("INVIA O.D.S."):
            range_gg = pd.date_range(dal, al).date
            bloccato = False
            
            if not info_u['Escluso'] and tipo not in ["Permesso 104", "Congedo Parentale"]:
                if any(check_limite(d) >= config['limite'] for d in range_gg):
                    bloccato = True
            
            if bloccato:
                st.error("Spiacente, una o più date selezionate hanno raggiunto il limite massimo.")
            else:
                nuovo_r = pd.DataFrame([[user, str(dal), str(al), tipo, tipo, len(range_gg), "GG"]], columns=df_ferie.columns)
                nuovo_r.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                invia_email(f"RICHIESTA: {user}", f"{tipo} dal {dal} al {al}")
                st.success("Richiesta inviata con successo!")
                time.sleep(1)
                st.rerun()
