import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date
import calendar

st.set_page_config(
    page_title="Agendas Clínica CAT",
    layout="wide",
    page_icon="CAT_Agenda_512.png",
    initial_sidebar_state="expanded"
)

# --- ESTADOS ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = False

# --- SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SETORES = ["Recepção", "Visita técnica", "Treinamentos NRs", "Viagens", "Palestras NR1", "Palestras Saúde", "OUTROS"]

# --- ESTILO ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0F2F5E; }
[data-testid="stSidebar"] * { color: white; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.logado:
    st.markdown("### Login Clínica CAT")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        st.session_state.logado = True
        st.rerun()
    st.stop()

# --- HEADER ---
st.markdown("""
<div style="background:#0A1931; padding:18px 25px; border-radius:10px; color:white">
    <div style="font-weight:bold">CAT Segurança e Saúde no Trabalho</div>
    <div style="font-size:22px; font-weight:bold">Agendas Clínica CAT</div>
</div>
""", unsafe_allow_html=True)

# --- MENU LATERAL ESQUERDO ---
with st.sidebar:
    st.markdown("### Setores")

    setor = st.radio(
        "",
        SETORES,
        label_visibility="collapsed"
    )

    st.write("---")

    if st.button("+ Novo Agendamento", use_container_width=True, type="primary"):
        st.session_state.mostrar_form = True
        st.rerun()

# --- FORMULÁRIO ---
if st.session_state.mostrar_form:
    st.markdown("### Novo Agendamento")
    col1, col2 = st.columns(2)
    with col1:
        setor_novo = st.selectbox("Setor do agendamento", SETORES, index=SETORES.index(setor))
        nome = st.text_input("Nome / Empresa")
    with col2:
        data = st.date_input("Data", value=date.today())
        obs = st.text_area("Observação")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Salvar", use_container_width=True, type="primary"):
            try:
                supabase.table("agendamentos").insert({
                    "setor": setor_novo,
                    "nome": nome,
                    "data": str(data),
                    "obs": obs
                }).execute()
                st.success(f"Agendamento salvo para {nome} em {data}!")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
            st.session_state.mostrar_form = False
            st.rerun()
    with c2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.mostrar_form = False
            st.rerun()

# --- CALENDÁRIO ---
hoje = date.today()
mes_nome = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"][hoje.month - 1]
st.markdown(f"### Calendário Mensal • {mes_nome} {hoje.year} - {setor}")

# --- LISTA ---
try:
    dados = supabase.table("agendamentos").select("*").eq("setor", setor).execute()
    df = pd.DataFrame(dados.data)
    if len(df) > 0:
        st.dataframe(df, use_container_width=True)
    else:
        st.info(f"Nenhum agendamento em {setor} ainda.")
except Exception as e:
    st.info(f"Mostrando agendamentos de {setor} - calendário mensal")

# --- ALERTAS + RESUMO ---
st.markdown("#### 🔔 Painel de Alertas")
st.warning("Exame Audiométrico - 3 colaboradores pendentes")
st.warning("ASO vencendo - 2 colaboradores")
st.info("Treinamento NR-35 - Amanhã às 09:00")

st.markdown("#### 📊 Resumo do Dia")
c1, c2 = st.columns(2)
c1.metric("Agendamentos", "14")
c2.metric("Confirmados", "9")
c1.metric("Pendentes", "5")
c2.metric("Taxa", "85%")
