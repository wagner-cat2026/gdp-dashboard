import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Agendas Clinica CAT", layout="wide")
st.title("Agendas Clinica CAT")
st.subheader("CAT Segurança e Saúde no Trabalho")

SUPABASE_URL = "https://SEU_PROJETO.supabase.co"
SUPABASE_KEY = "SUA_ANON_KEY"
ZAPI_INSTANCE = "SUA_INSTANCIA"
ZAPI_TOKEN = "SEU_TOKEN"

NUMEROS_ALERTA = ["5564999955603", "5564981318325", "5564999255538"]
setores = ["TST - Segurança do Trabalho", "Fonoaudiologia", "Psicologia", "Recepção", "Técnico Enfermagem"]
tipos = ["Visita técnica", "Treinamento", "Viagem", "Ausência", "Troca cobertura"]

col1, col2 = st.columns(2)
with col1:
    tipo = st.selectbox("Tipo", tipos)
    prof_origem = st.text_input("Profissional Origem")
    cliente = st.text_input("Cliente")
    data = st.date_input("Data")
with col2:
    setor = st.selectbox("Setor", setores)
    prof_sub = st.text_input("Profissional Substituto")
    inicio = st.time_input("Inicio")
    fim = st.time_input("Fim")

if st.button("SALVAR AGENDAMENTO", type="primary"):
    payload = {
        "tipo": tipo, "setor": setor,
        "prof_origem": prof_origem, "prof_sub": prof_sub,
        "cliente": cliente,
        "data_inicio": f"{data}T{inicio}",
        "data_fim": f"{data}T{fim}",
        "status": "agendado"
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/agenda", json=payload,
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"})
    if r.status_code == 201:
        st.success("Agendamento salvo!")
    else:
        st.error(r.text)

st.divider()
st.subheader("Agendamentos - Lista")
try:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/agenda?order=data_inicio.desc&limit=50",
                     headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    if r.status_code == 200:
        st.dataframe(r.json(), use_container_width=True)
except Exception as e:
    st.info("Configure SUPABASE_URL e KEY para ver a lista")

if st.button("Verificar Atrasos e Enviar WhatsApp"):
    agora = datetime.now().isoformat()
    url = f"{SUPABASE_URL}/rest/v1/agenda?status=eq.agendado&data_fim=lt.{agora}"
    r = requests.get(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})
    for ag in r.json():
        msg = f"⚠️ AGENDAS CLINICA CAT\nAtraso: {ag['tipo']} - {ag['prof_origem']} p/ {ag['cliente']}"
        for num in NUMEROS_ALERTA:
            requests.post(f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text",
                          json={"phone": num, "message": msg})
    st.success("Alertas enviados!")
