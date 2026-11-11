import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, time
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
        tipo_novo = st.selectbox("Setor do agendamento", SETORES, index=SETORES.index(setor))
        cliente_novo = st.text_input("Nome / Empresa / Cliente")
        profissional_novo = st.text_input("Profissional")
    with col2:
        data_novo = st.date_input("Data", value=date.today())
        inicio_novo = st.time_input("Hora Início", value=time(8, 0))
        fim_novo = st.time_input("Hora Fim", value=time(9, 0))
        obs_novo = st.text_area("Observação - descreva o que vai agendar", placeholder="Ex: ASO, retorno, exame...")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Salvar", use_container_width=True, type="primary"):
            try:
                res = supabase.table("agendamentos").insert({
                    "tipo": tipo_novo,
                    "setor": tipo_novo,
                    "cliente": cliente_novo,
                    "profissional": profissional_novo,
                    "data": str(data_novo),
                    "inicio": inicio_novo.strftime("%H:%M"),
                    "fim": fim_novo.strftime("%H:%M"),
                    "obs": obs_novo
                }).execute()
                st.success(f"Salvo! {cliente_novo} em {data_novo} das {inicio_novo} às {fim_novo}")
                st.session_state.mostrar_form = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
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
    dados = supabase.table("agendamentos").select("setor, data, inicio, fim, cliente, profissional, obs").eq("setor", setor).execute()
    df = pd.DataFrame(dados.data)
    if len(df) > 0:
        df = df[["setor", "data", "inicio", "fim", "cliente", "profissional", "obs"]]
        df.columns = ["Setor", "Data", "Início", "Fim", "Cliente", "Profissional", "Observação"]
        df = df.fillna("")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(f"Nenhum agendamento em {setor} ainda.")
except Exception as e:
    st.info(f"Mostrando agendamentos de {setor} - calendário mensal")
    
# --- ALERTAS + RESUMO ---
st.markdown("### 🔔 Painel de Alertas")

# Todas as agendadas, sem filtro de data
agendados = df[df['status'] == 'agendado'].sort_values('data_inicio')

if len(agendados) == 0:
    st.success("Nenhuma tarefa agendada.")
else:
    for _, ag in agendados.iterrows():
        st.warning(f"📅 {ag['data_inicio']} - {ag['tipo']} - {ag['cliente']} - {ag['prof_origem']}")

st.markdown("### 📊 Resumo do Dia")

c1, c2 = st.columns(2)
total = len(df)
confirmados = len(df[df['status'] == 'confirmado'])
pendentes = len(df[df['status'] == 'agendado'])
taxa = int(confirmados / total * 100) if total > 0 else 0

c1.metric("Agendamentos", total)
c2.metric("Confirmados", confirmados)
c1.metric("Pendentes", pendentes)
c2.metric("Taxa", f"{taxa}%")
