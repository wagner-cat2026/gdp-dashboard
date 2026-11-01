import streamlit as st
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
