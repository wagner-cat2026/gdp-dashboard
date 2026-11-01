import streamlit as st
USUARIOS = { ... } # código de login por setor
USUARIOS = {"comercial@cat":{"senha":"cat123","setor":"Comercial"},"adm@cat":{"senha":"cat123","setor":"ADM"},"seguranca@cat":{"senha":"cat123","setor":"Segurança"},"clinica@cat":{"senha":"cat123","setor":"Clínica"},"rh@cat":{"senha":"cat123","setor":"RH"}}
if "logado" not in st.session_state: st.session_state.logado=False
if not st.session_state.logado:
    st.set_page_config(page_title="CAT", page_icon="🛡️")
    st.markdown("<div style='background:#0A2342;padding:15px;border-radius:10px'><h1 style='color:white;margin:0'>CAT - Segurança e Saúde no Trabalho</h1></div>", unsafe_allow_html=True)
    u=st.text_input("Usuário"); s=st.text_input("Senha",type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["senha"]==s:
            st.session_state.logado=True; st.session_state.setor=USUARIOS[u]["setor"]; st.rerun()
        else: st.error("Login inválido")
    st.stop()
import requests
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="Agenda Clinica CAT")
st.title("Agenda Clinica CAT")
st.subheader("CAT Segurança e Saúde no Trabalho")

# Pega as chaves dos Secrets (que você já configurou)
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

# Cria conexão
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

NUMEROS_ALERTA = ["5564999955603", "556499998877"]
setores = ["TST - Segurança do Trabalho", "Clinica", "RH", "Administrativo"]
tipos = ["Visita técnica", "Treinamento", "Consulta", "Exame", "Reunião"]

col1, col2 = st.columns(2)
with col1:
    tipo = st.selectbox("Tipo", tipos)
    prof_origem = st.text_input("Profissional Origem")
    cliente = st.text_input("Cliente")
    data = st.date_input("Data", datetime.now())
with col2:
    setor = st.selectbox("Setor", setores)
    inicio = st.text_input("Inicio (ex: 08:00)")
    fim = st.text_input("Fim (ex: 09:00)")

if st.button("SALVAR AGENDAMENTO"):
    try:
        dados = {
            "tipo": tipo,
            "profissional": prof_origem,
            "cliente": cliente,
            "data": str(data),
            "setor": setor,
            "inicio": inicio,
            "fim": fim
        }
        supabase.table("agendamentos").insert(dados).execute()
        st.success("✅ Agendamento salvo com sucesso no banco!")
        st.balloons()
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
