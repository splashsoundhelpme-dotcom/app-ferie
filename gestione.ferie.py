import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np

# --- CONFIGURAZIONE ---
PASSWORD_ADMIN = "admin2024"
PASSWORD_DEFAULT = "12345"  # Password per tutti i dipendenti
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
ORE_GIORNATA = 6.67  # 6 ore e 40 minuti

st.set_page_config(page_title="Battistolli HR", layout="wide", page_icon="🏢")

# --- FUNZIONI DI UTILITÀ ---
def pulisci_password(valore):
    """
    Pulisce il valore della password per evitare errori 
    tra numeri (12345), stringhe ('12345') e decimali (12345.0)
    """
    if pd.isna(valore) or valore == "":
        return str(PASSWORD_DEFAULT)
    # Converte in stringa, rimuove spazi e rimuove .0 se presente
    return str(valore).split('.')[0].strip()

def carica_dati():
    """
    Carica i dati direttamente dal file CSV dell'utente.
    Gestisce automaticamente i nomi delle colonne.
    """
    if not os.path.exists(FILE_DIPENDENTI):
        st.error(f"⚠️ Manca il file '{FILE_DIPENDENTI}' nella cartella! Inserisci il file CSV con i nomi.")
        st.stop()
    
    # Legge il file
    df = pd.read_csv(FILE_DIPENDENTI)
    
    # Normalizza i nomi delle colonne (toglie spazi e mette minuscolo per intercettare errori)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Mappa le colonne del tuo file (es. 'nome e cognome' -> 'Nome')
    col_mapping = {
        'nome e cognome': 'Nome',
        'nome': 'Nome',
        'dipendente': 'Nome',
        'saldo ferie': 'Ferie',
        'ferie': 'Ferie',
        'saldo ferie 2025': 'Ferie',
        'rol': 'ROL',
        'saldo rol': 'ROL',
        'saldo rol 2025': 'ROL'
    }
    
    df = df.rename(columns=col_mapping)
    
    # Verifica che le colonne essenziali esistano
    if 'Nome' not in df.columns or 'Ferie' not in df.columns:
        st.error("Errore nel file CSV: Assicurati che le colonne si chiamino 'Nome', 'Ferie' e 'ROL'.")
        st.stop()
        
    # Se manca la colonna ROL, la crea a zero
    if 'ROL' not in df.columns:
        df['ROL'] = 0.0
        
    # Se manca la colonna Password, la crea
    if 'Password' not in df.columns:
        df['Password'] = PASSWORD_DEFAULT
        
    # Pulisce i dati
    df['Nome'] = df['Nome'].astype(str).str.strip().str.upper()
    df['Password'] = df['Password'].apply(pulisci_password)
    
    return df

def inizializza_ferie():
    if not os.path.exists(FILE_FERIE):
        pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)

# --- AVVIO LOGICA ---
inizializza_ferie()

# Caricamento dinamico dal tuo file
try:
    df_dip = carica_dati()
except Exception as e:
    st.error(f"Errore nella lettura del file CSV: {e}")
    st.stop()

# --- LOGIN ---
if "user" not in st.session_state:
    st.title("🏢 Portale Dipendenti Battistolli")
    st.markdown("### Accesso al sistema")
    
    col_l1, col_l2 = st.columns([2,1])
    with col_l1:
        u_input = st.text_input("Inserisci NOME e COGNOME").upper().strip()
        p_input = st.text_input("Password", type="password").strip()
        
        if st.button("ACCEDI", type="primary"):
            # Login Admin
            if u_input == "ADMIN" and p_input == PASSWORD_ADMIN:
                st.session_state["user"] = "admin"
                st.rerun()
            
            # Login Dipendente
            else:
                user_row = df_dip[df_dip['Nome'] == u_input]
                
                if not user_row.empty:
                    # Recupera la password salvata e la pulisce
                    stored_pass = user_row.iloc[0]['Password']
                    
                    if p_input == stored_pass:
                        st.session_state["user"] = u_input
                        st.rerun()
                    else:
                        st.error("🔒 Password errata.")
                else:
                    st.error("👤 Utente non trovato. Controlla di aver digitato il nome esattamente come nel file Excel.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.success(f"Loggato come: **{st.session_state['user']}**")
    if st.button("Esci"):
        del st.session_state["user"]
        st.rerun()

# --- DASHBOARD DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_u = st.session_state["user"]
    
    # Rilegge i dati freschi dell'utente
    dati_user = df_dip[df_dip['Nome'] == nome_u].iloc[0]
    df_richieste = pd.read_csv(FILE_FERIE)
    
    # Calcolo Usato
    usato_ferie = df_richieste[(df_richieste['Nome'] == nome_u) & (df_richieste['Risorsa'] == 'Ferie')]['Ore'].sum()
    usato_rol = df_richieste[(df_richieste['Nome'] == nome_u) & (df_richieste['Risorsa'] == 'ROL')]['Ore'].sum()
    
    # Calcolo Residuo (Saldo Iniziale + Maturazione approssimativa - Usato)
    # Nota: Qui usiamo il saldo iniziale del CSV. Se vuoi aggiungere la maturazione, si somma qui.
    # Per ora mostriamo Saldo CSV - Usato per chiarezza.
    residuo_ferie = round(float(dati_user['Ferie']) - usato_ferie, 2)
    residuo_rol = round(float(dati_user['ROL']) - usato_rol, 2)
    
    st.title(f"Benvenuto, {nome_u}")
    
    # Visualizzazione Saldi
    c1, c2 = st.columns(2)
    c1.metric("💰 Saldo Ferie Residuo", f"{residuo_ferie} ore", delta=f"-{usato_ferie} usate")
    c2.metric("💰 Saldo ROL Residuo", f"{residuo_rol} ore", delta=f"-{usato_rol} usate")
    
    st.divider()
    
    # Modulo Richiesta
    with st.form("form_richiesta"):
        st.subheader("Nuova Richiesta Assenza")
        col_a, col_b = st.columns(2)
        tipo = col_a.selectbox("Motivazione", ["Ferie", "ROL", "104", "Donazione Sangue", "Malattia", "Altro"])
        risorsa = col_b.radio("Da dove scalare le ore?", ["Ferie", "ROL"], horizontal=True)
        
        col_c, col_d = st.columns(2)
        data_inizio = col_c.date_input("Dal giorno")
        data_fine = col_d.date_input("Al giorno")
        note = st.text_area("Note (facoltativo)")
        
        if st.form_submit_button("Invia Richiesta"):
            if data_inizio > data_fine:
                st.error("La data di fine deve essere successiva all'inizio.")
            else:
                # Controlli
                giorni_range = pd.date_range(data_inizio, data_fine).date
                df_check = pd.read_csv(FILE_FERIE)
                conflitto = False
                
                # Verifica limite 3 persone (escludendo 104 e Sangue)
                if not df_check.empty:
                    df_check['Inizio'] = pd.to_datetime(df_check['Inizio']).dt.date
                    df_check['Fine'] = pd.to_datetime(df_check['Fine']).dt.date
                    
                    for giorno in giorni_range:
                        assenti_oggi = df_check[
                            (df_check['Inizio'] <= giorno) & 
                            (df_check['Fine'] >= giorno)
                        ]
                        if len(assenti_oggi) >= 3 and tipo not in ["104", "Donazione Sangue"]:
                            conflitto = True
                            st.error(f"⛔ Impossibile richiedere il {giorno.strftime('%d/%m/%Y')}: limite di 3 persone già raggiunto.")
                            break
                
                if not conflitto:
                    giorni_lavorativi = int(np.busday_count(data_inizio, data_fine + timedelta(days=1)))
                    ore_totali = round(giorni_lavorativi * ORE_GIORNATA, 2)
                    
                    nuova_riga = pd.DataFrame({
                        'Nome': [nome_u],
                        'Inizio': [data_inizio],
                        'Fine': [data_fine],
                        'Tipo': [tipo],
                        'Risorsa': [risorsa],
                        'Ore': [ore_totali],
                        'Note': [note]
                    })
                    
                    nuova_riga.to_csv(FILE_FERIE, mode='a', header=False, index=False)
                    st.success(f"✅ Richiesta approvata! Scalate {ore_totali} ore da {risorsa}.")
                    time.sleep(1.5)
                    st.rerun()

# --- DASHBOARD ADMIN ---
else:
    st.title("Pannello Amministratore")
    
    tab1, tab2 = st.tabs(["📋 Riepilogo Richieste", "👥 Anagrafica Dipendenti"])
    
    with tab1:
        if os.path.exists(FILE_FERIE):
            df_f = pd.read_csv(FILE_FERIE)
            st.dataframe(df_f, use_container_width=True)
            
            # Export Excel
            # (Per semplicità qui usiamo csv, per excel serve openpyxl)
            st.download_button("Scarica Storico CSV", df_f.to_csv(index=False).encode('utf-8'), "storico_ferie.csv")
            
            if st.button("🗑️ CANCELLA TUTTE LE RICHIESTE (Reset Anno)"):
                pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Risorsa', 'Ore', 'Note']).to_csv(FILE_FERIE, index=False)
                st.warning("Database richieste azzerato.")
                st.rerun()
        else:
            st.info("Nessuna richiesta presente.")

    with tab2:
        st.write("Dati letti dal file `db_dipendenti.csv`:")
        st.dataframe(df_dip, use_container_width=True)
        st.info("Per modificare questi dati, modifica il file CSV nella cartella e riavvia l'app.")
