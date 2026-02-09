import streamlit as st
import pd
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

# --- 1. FUNZIONE INVIO EMAIL ---
def invia_email(oggetto, corpo):
    try:
        mittente = st.secrets["email"]["user"]
        password = st.secrets["email"]["password"]
        destinatario = st.secrets["email"]["admin_email"]
        msg = MIMEText(corpo)
        msg['Subject'] = oggetto
        msg['From'] = mittente
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(mittente, password)
            server.sendmail(mittente, destinatario, msg.as_string())
        return True
    except:
        return False

# --- 2. GESTIONE DATABASE ---
def refresh_database():
    dati_test = [
        ["ROSSINI LORENZO", 6.40, 12.0, "Guardia", "12345"],
        ["TEST GUARDIA 1", 10.0, 8.0, "Guardia", "test1"],
        ["TEST GUARDIA 2", 10.0, 8.0, "Guardia", "test2"],
        ["TEST FIDUCIARIO 1", 100.0, 40.0, "Fiduciario", "test3"],
        ["TEST FIDUCIARIO 2", 100.0, 40.0, "Fiduciario", "test4"]
    ]
    if not os.path.exists(FILE_DIPENDENTI):
        df = pd.DataFrame(dati_test, columns=['Nome','Ferie','ROL','Contratto','Password'])
        df.to_csv(FILE_DIPENDENTI, index=False)
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
    return pd.read_csv(FILE_DIPENDENTI), pd.read_csv(FILE_FERIE)

df_dip, df_ferie = refresh_database()

st.set_page_config(page_title="Battistolli HR v26.1", layout="wide")

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Accesso Portale Battistolli")
    u_in = st.text_input("NOME").strip().upper()
    p_in = st.text_input("PASSWORD", type="password").strip()
    if st.button("ACCEDI"):
        if u_in == "ADMIN" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"; st.rerun()
        elif u_in in df_dip['Nome'].values:
            row = df_dip[df_dip['Nome'] == u_in].iloc[0]
            if str(row['Password']) == p_in:
                st.session_state["user"] = u_in; st.rerun()
            else: st.error("Password errata.")
    st.stop()

user = st.session_state["user"]

# --- AREA ADMIN ---
if user == "admin":
    st.header("👨‍💼 Console Amministratore")
    
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🚪 LOGOUT"): 
            del st.session_state["user"]; st.rerun()
        
        st.write("---")
        st.warning("⚠️ ZONA PERICOLO")
        if st.button("🗑️ RESET RICHIESTE", help="Cancella tutte le ferie prenotate"):
            pd.DataFrame(columns=['Nome','Inizio','Fine','Tipo','Risorsa','Valore','Unita']).to_csv(FILE_FERIE, index=False)
            st.success("Registro svuotato!")
            time.sleep(1); st.rerun()

    with col_a:
        st.subheader("📋 Registro O.D.S. Settimanale")
        if not df_ferie.empty:
            st.dataframe(df_ferie, use_container_width=True)
        else:
            st.info("Nessuna richiesta in archivio.")

# --- AREA UTENTE ---
else:
    dati = df_dip[df_dip['Nome'] == user].iloc[0]
    unita = "Giorni" if dati['Contratto'] == "Guardia" else "Ore"
    
    st.header(f"Benvenuto {user}")
    
    # Saldi aggiornati
    usato_f = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'Ferie')]['Valore'].sum()
    usato_r = df_ferie[(df_ferie['Nome'] == user) & (df_ferie['Risorsa'] == 'ROL')]['Valore'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Ferie ({unita})", round(dati['Ferie'] - usato_f, 2))
    c2.metric(f"ROL ({unita})", round(dati['ROL'] - usato_r, 2))
    if c3.button("Logout"): del st.session_state["user"]; st.rerun()

    st.divider()
    
    # Calendario Privacy
    st.subheader("📅 Disponibilità")
    giorni = pd.date_range(date.today() + timedelta(days=1), periods=10).date
    cols = st.columns(len(giorni))
    for i, g in enumerate(giorni):
        occ = len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g)])
        col_color = "🟢" if occ < LIMITE_CONTEMPORANEITA else "🔴"
        cols[i].markdown(f"**{g.strftime('%d/%m')}**\n\n{col_color}\n\n{occ}/{LIMITE_CONTEMPORANEITA}")

    st.divider()

    with st.form("invio"):
        tipo = st.selectbox("Tipo", ["Ferie", "ROL"])
        domani = date.today() + timedelta(days=1)
        da = st.date_input("Inizio", value=domani, min_value=domani)
        al = st.date_input("Fine", value=domani, min_value=domani)
        
        if st.form_submit_button("Invia"):
            intervallo = pd.date_range(da, al).date
            conflitto = False
            for g in intervallo:
                if len(df_ferie[(pd.to_datetime(df_ferie['Inizio']).dt.date <= g) & (pd.to_datetime(df_ferie['Fine']).dt.date >= g)]) >= LIMITE_CONTEMPORANEITA:
                    conflitto = True; break
            
            if conflitto:
                st.error("Giorno occupato!")
            else:
                val = len(intervallo) if dati['Contratto'] == "Guardia" else round(len(intervallo)*6.67, 2)
                nuova = pd.DataFrame([[user, str(da), str(al), tipo, tipo, val, unita]], columns=df_ferie.columns)
                nuova.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                
                # Email
                inviata = invia_email(f"Richiesta {tipo} - {user}", f"{user} ha chiesto {val} {unita} dal {da} al {al}")
                st.success("Richiesta salvata!")
                time.sleep(1); st.rerun()
