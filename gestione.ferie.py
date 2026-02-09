import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
import time

# --- CONFIGURAZIONE ---
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
PASSWORD_ADMIN = "admin2024"
LIMITE_CONTEMPORANEITA = 3 
ORE_GIORNATA_FIDUCIARI = 6.67

# --- FUNZIONI ---
def formatta_data_it(data_obj):
    if isinstance(data_obj, str):
        try: data_obj = datetime.strptime(data_obj, '%Y-%m-%d')
        except: return data_obj
    return data_obj.strftime('%d/%m/%Y')

def invia_email(oggetto, corpo):
    try:
        if "email" not in st.secrets: return False
        mittente = st.secrets["email"]["user"]
        pw = st.secrets["email"]["password"]
        dest = st.secrets["email"]["admin_email"]
        msg = MIMEText(corpo)
        msg['Subject'] = oggetto
        msg['From'] = mittente
        msg['To'] = dest
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(mittente, pw)
            server.sendmail(mittente, dest, msg.as_string())
        return True
    except: return False

# --- DATABASE ---
def refresh_db():
    elenco_reale = [
        ["ROSSINI LORENZO", 6.40, 0.0, "Guardia", "12345", True], # Nome, Ferie, ROL, Tipo, PW, PrimoAccesso
        ["ABBATICCHIO ANTONIO", 10.0, 8.0, "Fiduciario", "12345", True],
        ["ACQUAVIVA ANNALISA", 10.0, 8.0, "Fiduciario", "12345", True]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        pd.DataFrame(elenco_reale, columns=['Nome','Ferie','ROL','Contratto','Password', 'PrimoAccesso']).to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_db()

st.set_page_config(page_title="Battistolli HR", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale Battistolli")
    u_in = st.text_input("NOME E COGNOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        
        for i, row in df_dip.iterrows():
            if u_in == row['Nome'] or u_in == " ".join(row['Nome'].split()[::-1]):
                if str(row['Password']) == p_in:
                    st.session_state["user"] = row['Nome']
                    st.session_state["primo_accesso"] = row['PrimoAccesso']
                    st.rerun()
        st.error("Credenziali errate.")
    st.stop()

user = st.session_state["user"]

# --- GESTIONE CAMBIO PASSWORD PRIMO ACCESSO ---
if user != "admin" and st.session_state.get("primo_accesso", False):
    st.warning(f"Benvenuto {user}. È necessario cambiare la password al primo accesso.")
    new_pw = st.text_input("Nuova Password", type="password")
    conf_pw = st.text_input("Conferma Nuova Password", type="password")
    if st.button("Aggiorna Password"):
        if new_pw == conf_pw and len(new_pw) >= 5:
            df_dip.loc[df_dip['Nome'] == user, 'Password'] = new_pw
            df_dip.loc[df_dip['Nome'] == user, 'PrimoAccesso'] = False
            df_dip.to_csv(FILE_DIPENDENTI, index=False)
            st.session_state["primo_accesso"] = False
            st.success("Password aggiornata! Caricamento app...")
            time.sleep(1.5); st.rerun()
        else: st.error("Le password non coincidono o sono troppo corte.")
    st.stop()

# --- AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Console Admin")
    if st.button("Logout"): del st.session_state["user"]; st.rerun()
    st.dataframe(df_ferie, use_container_width=True)

# --- AREA UTENTE ---
else:
    info = df_dip[df_dip['Nome'] == user].iloc[0]
    
    # LOGICA 1: Saldo sempre a GIORNI per tutti (Fiduciari inclusi)
    u_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    u_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    u_d = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Donazione Sangue')]['Valore'].sum()
    
    st.header(f"Ciao {user}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo Ferie (Giorni)", round(float(info['Ferie']) - u_f, 2))
    
    # LOGICA 2: Le guardie non hanno ROL (visualizza 0 o N/A)
    if info['Contratto'] == "Guardia":
        c2.metric("ROL (Giorni)", "N/A")
    else:
        c2.metric("ROL (Giorni)", round(float(info['ROL']) - u_r, 2))
    
    if c4.button("Logout"): del st.session_state["user"]; st.rerun()

    st.divider()
    
    # LOGICA 3: Visualizzazione Orizzontale Posti
    st.subheader("📅 Disponibilità Reparto (Semaforo)")
    giorni = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols = st.columns(len(giorni))
    for i, g in enumerate(giorni):
        occ = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g)]) if not df_ferie.empty else 0
        with cols[i]:
            st.markdown(f"**{g.strftime('%d/%m')}**")
            st.write("🟢" if occ < LIMITE_CONTEMPORANEITA else "🔴")
            st.caption(f"{occ}/3")

    st.divider()

    with st.form("richiesta"):
        # LOGICA 4: Nuove opzioni (104, Donazione, Congedo)
        causale = st.selectbox("Causale", ["Ferie", "ROL", "Permesso 104", "Donazione Sangue", "Congedo Parentale"])
        da = st.date_input("Inizio", min_value=date.today()+timedelta(days=1))
        al = st.date_input("Fine", min_value=date.today()+timedelta(days=1))
        
        if st.form_submit_button("INVIA"):
            intervallo = pd.date_range(da, al).date
            
            # LOGICA ECCEZIONI: 104 e Congedo non bloccano il limite dei 3
            if causale in ["Permesso 104", "Congedo Parentale"]:
                conflitto = False
            else:
                conflitto = any(len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= d) & (pd.to_datetime(df_ferie['Fine']).dt.date >= d) & (~df_ferie['Tipo'].isin(["Permesso 104", "Congedo Parentale"]))]) >= LIMITE_CONTEMPORANEITA for d in intervallo)

            if conflitto:
                st.error("Limite di contemporaneità raggiunto per le date scelte.")
            else:
                val = len(intervallo) # Saldo calcolato a GIORNI
                nuovo = pd.DataFrame([[user, str(da), str(al), causale, causale, val, "Giorni"]], columns=df_ferie.columns)
                nuovo.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                invia_email(f"Richiesta {causale} - {user}", f"{user} chiede {causale} dal {da} al {al}")
                st.success("Richiesta registrata!")
                time.sleep(1); st.rerun()
