import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import numpy as np
import time

# --- CONFIGURAZIONE E SETUP ---
PASSWORD_ADMIN = "admin2024" 
PASSWORD_STANDARD = "12345" 
FILE_DIPENDENTI = 'db_dipendenti.csv'
FILE_FERIE = 'db_ferie.csv'
EMAIL_NOTIFICA = "lorenzo.rossini@battistolli.it"

st.set_page_config(page_title="Battistolli Ferie Premium", layout="wide")

# --- FUNZIONI DI GESTIONE DATI ---
def carica_dati():
    # Gestione Anagrafica Dipendenti
    if not os.path.exists(FILE_DIPENDENTI) or os.stat(FILE_DIPENDENTI).st_size == 0:
        df_dip = pd.DataFrame(columns=['Nome', 'Saldo_Arretrato', 'Password', 'Primo_Accesso'])
        df_dip.to_csv(FILE_DIPENDENTI, index=False)
    else:
        df_dip = pd.read_csv(FILE_DIPENDENTI)
    
    # Gestione Database Ferie
    if not os.path.exists(FILE_FERIE) or os.stat(FILE_FERIE).st_size == 0:
        df_ferie = pd.DataFrame(columns=['Nome', 'Inizio', 'Fine', 'Tipo', 'Giorni', 'Note'])
        df_ferie.to_csv(FILE_FERIE, index=False)
    else:
        df_ferie = pd.read_csv(FILE_FERIE)
        # Convertiamo le date dal CSV in oggetti data di Python
        df_ferie['Inizio'] = pd.to_datetime(df_ferie['Inizio']).dt.date
        df_ferie['Fine'] = pd.to_datetime(df_ferie['Fine']).dt.date
    return df_dip, df_ferie

def calcola_giorni_lavorativi(start, end):
    # Calcola i giorni escludendo i weekend
    return int(np.busday_count(start, end + timedelta(days=1)))

def calcola_ferie_maturate_2026(saldo_arretrato):
    # Logica 2.33 giorni al mese maturati nell'anno corrente
    oggi = date.today()
    mesi_trascorsi = oggi.month if oggi.year == 2026 else (12 if oggi.year > 2026 else 0)
    maturazione_anno = mesi_trascorsi * 2.33
    return round(float(saldo_arretrato) + maturazione_anno, 2)

def verifica_disponibilita(inizio, fine, df_esistente, tipo_richiesta):
    # REGOLE SPECIALI (SALTA-FILA)
    # Donazione Sangue, 104 e Congedo Parentale passano SEMPRE
    salta_fila = ["104", "Congedo Parentale", "Donazione Sangue"]
    if tipo_richiesta in salta_fila:
        return True, None
    
    # CONTROLLO LIMITE 3 PERSONE PER FERIE STANDARD
    intervallo_richiesto = pd.date_range(start=inizio, end=fine).date
    for singolo_giorno in intervallo_richiesto:
        # Controlliamo quanti dipendenti sono assenti in questo specifico giorno
        contatore_assenti = 0
        for _, riga in df_esistente.iterrows():
            if riga['Inizio'] <= singolo_giorno <= riga['Fine']:
                contatore_assenti += 1
        
        if contatore_assenti >= 3:
            return False, singolo_giorno
    return True, None

# Carichiamo i database all'avvio
df_dipendenti, df_ferie = carica_dati()

# --- SISTEMA DI AUTENTICAZIONE ---
if "user" not in st.session_state:
    st.title("🔐 Accesso Portale Battistolli")
    col_log1, col_log2 = st.columns(2)
    u_in = col_log1.text_input("Utente")
    p_in = col_log2.text_input("Password", type="password")
    
    if st.button("LOG IN", use_container_width=True):
        if u_in == "admin" and p_in == PASSWORD_ADMIN:
            st.session_state["user"] = "admin"
            st.rerun()
        elif not df_dipendenti.empty:
            # Controllo case-insensitive (non importa maiuscole/minuscole)
            df_dipendenti['Nome_Check'] = df_dipendenti['Nome'].str.lower().str.strip()
            u_clean = u_in.lower().strip()
            match = df_dipendenti[(df_dipendenti['Nome_Check'] == u_clean) & (df_dipendenti['Password'].astype(str) == p_in)]
            if not match.empty:
                st.session_state["user"] = match.iloc[0]['Nome']
                st.rerun()
            else: st.error("❌ Credenziali errate.")
    st.stop()

# --- BARRA LATERALE (NAVIGAZIONE) ---
with st.sidebar:
    st.title("🏢 Menu")
    st.write(f"Connesso come: **{st.session_state['user']}**")
    if st.button("🔴 Esci dal sistema"):
        del st.session_state["user"]
        st.rerun()

# --- INTERFACCIA DIPENDENTE ---
if st.session_state["user"] != "admin":
    nome_utente = st.session_state["user"]
    st.header(f"👋 Benvenuto, {nome_utente}")
    
    # Recupero dati dipendente
    dati_d = df_dipendenti[df_dipendenti['Nome'] == nome_utente].iloc[0]
    
    # Calcolo Saldo Real-Time
    tot_maturato = calcola_ferie_maturate_2026(dati_d['Saldo_Arretrato'])
    tot_usate = df_ferie[(df_ferie['Nome'] == nome_utente) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
    saldo_finale = round(tot_maturato - tot_usate, 2)
    
    # Widget Visivo Saldo
    st.metric("SALDO FERIE RESIDUO (Incluso maturato 2026)", f"{saldo_finale} giorni")

    # Modulo Richiesta Assenza
    with st.form("nuova_richiesta_completa"):
        st.subheader("📝 Nuova Richiesta Assenza")
        tipo_assenza = st.selectbox("Seleziona Motivo", ["Ferie", "104", "Congedo Parentale", "Donazione Sangue", "Altro"])
        c1, c2 = st.columns(2)
        data_inizio = c1.date_input("Dalla data (inclusa)", format="DD/MM/YYYY")
        data_fine = c2.date_input("Alla data (inclusa)", format="DD/MM/YYYY")
        campo_note = st.text_area("Note e precisazioni (es. orari visita o motivi)", placeholder="Opzionale...")
        
        if st.form_submit_button("INVIA RICHIESTA ALL'AMMINISTRAZIONE"):
            if data_inizio > data_fine:
                st.error("Errore: la data di inizio non può essere dopo quella di fine.")
            else:
                esito, giorno_off = verifica_disponibilita(data_inizio, data_fine, df_ferie, tipo_assenza)
                if esito:
                    giorni_calc = calcola_giorni_lavorativi(data_inizio, data_fine)
                    nuova_riga = pd.DataFrame({
                        'Nome': [nome_utente], 'Inizio': [data_inizio], 'Fine': [data_fine],
                        'Tipo': [tipo_assenza], 'Giorni': [giorni_calc], 'Note': [campo_note]
                    })
                    df_ferie = pd.concat([df_ferie, nuova_riga], ignore_index=True)
                    df_ferie.to_csv(FILE_FERIE, index=False)
                    st.success(f"✅ Richiesta inoltrata correttamente! (Notifica a {EMAIL_NOTIFICA})")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(f"⚠️ Limite raggiunto: il giorno {giorno_off.strftime('%d/%m/%Y')} ci sono già 3 persone assenti.")

# --- INTERFACCIA AMMINISTRATORE ---
else:
    st.title("👨‍💼 Pannello di Controllo Admin")
    t1, t2, t3 = st.tabs(["🗓️ Planning Settimanale", "📊 Statistiche & Note", "⚙️ Gestione Database"])

    with t1:
        st.subheader("Visualizzazione Presenze")
        data_focus = st.date_input("Mostra a partire dal:", date.today(), format="DD/MM/YYYY")
        giorni_settimana = [data_focus + timedelta(days=i) for i in range(7)]
        
        corpo_tabella = []
        for _, dipendente in df_dipendenti.iterrows():
            riga_p = {"Dipendente": dipendente['Nome']}
            for g in giorni_settimana:
                # Cerchiamo se il dipendente è assente in quel giorno
                match = df_ferie[(df_ferie['Nome'] == dipendente['Nome']) & (df_ferie['Inizio'] <= g) & (df_ferie['Fine'] >= g)]
                if not match.empty:
                    tipo = match.iloc[0]['Tipo']
                    icona = "🔵" if tipo in ["104", "Donazione Sangue", "Congedo Parentale"] else "❌"
                    riga_p[g.strftime("%d/%m")] = f"{icona} {tipo}"
                else:
                    riga_p[g.strftime("%d/%m")] = "✅"
            corpo_tabella.append(riga_p)
        st.table(pd.DataFrame(corpo_tabella))

    with t2:
        st.subheader("Analisi Saldi e Comunicazioni")
        # Grafico dei Saldi Residui
        if not df_dipendenti.empty:
            lista_saldi = []
            for _, r in df_dipendenti.iterrows():
                mat = calcola_ferie_maturate_2026(r['Saldo_Arretrato'])
                use = df_ferie[(df_ferie['Nome'] == r['Nome']) & (df_ferie['Tipo'] == 'Ferie')]['Giorni'].sum()
                lista_saldi.append({"Persona": r['Nome'], "Giorni Residui": mat - use})
            
            st.bar_chart(pd.DataFrame(lista_saldi).set_index("Persona"))
        
        st.divider()
        st.subheader("Ultime Richieste con Note")
        if not df_ferie.empty:
            for i, r in df_ferie.tail(15).iterrows():
                with st.expander(f"📌 {r['Nome']} - {r['Tipo']} ({r['Inizio'].strftime('%d/%m/%Y')})"):
                    st.write(f"**Periodo:** dal {r['Inizio']} al {r['Fine']}")
                    st.write(f"**Note del dipendente:** {r['Note'] if str(r['Note']) != 'nan' else 'Nessuna nota'}")
                    if st.button("ELIMINA", key=f"btn_del_{i}"):
                        df_ferie = df_ferie.drop(i)
                        df_ferie.to_csv(FILE_FERIE, index=False)
                        st.rerun()

    with t3:
        st.subheader("Gestione Anagrafica Personale")
        with st.form("aggiunta_rapida"):
            col_n, col_s = st.columns(2)
            nome_nuovo = col_n.text_input("Nome e Cognome")
            saldo_2025 = col_s.number_input("Saldo residuo fine 2025", value=0.0)
            if st.form_submit_button("AGGIUNGI A DATABASE"):
                nuovo_dip = pd.DataFrame({
                    'Nome': [nome_nuovo], 'Saldo_Arretrato': [saldo_2025], 
                    'Password': [PASSWORD_STANDARD], 'Primo_Accesso': [True]
                })
                df_dipendenti = pd.concat([df_dipendenti, nuovo_dip], ignore_index=True)
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.success("Utente aggiunto correttamente!")
                st.rerun()
        
        st.divider()
        if not df_dipendenti.empty:
            u_da_gestire = st.selectbox("Seleziona Utente per modifiche", df_dipendenti['Nome'])
            if st.button("🗑️ ELIMINA UTENTE DEFINITIVAMENTE"):
                df_dipendenti = df_dipendenti[df_dipendenti['Nome'] != u_da_gestire]
                df_dipendenti.to_csv(FILE_DIPENDENTI, index=False)
                st.warning(f"Utente {u_da_gestire} rimosso.")
                st.rerun()
