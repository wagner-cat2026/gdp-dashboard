import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date, time

st.set_page_config(
    page_title="Agendas Clínica CAT",
    layout="wide",
    page_icon="CAT_Agenda_512.png",
    initial_sidebar_state="expanded"
)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = False

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SETORES = ["Recepção", "Visita técnica", "Treinamentos NRs", "Viagens", "Palestras NR1", "Palestras Saúde", "OUTROS"]

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0F2F5E; }
[data-testid="stSidebar"] * { color: white; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logado:
    st.markdown("### Login Clínica CAT")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        st.session_state.logado = True
        st.rerun()
    st.stop()

st.markdown("""
<div style="background:#0A1931; padding:18px 25px; border-radius:10px; color:white">
    <div style="font-weight:bold">CAT Segurança e Saúde no Trabalho</div>
    <div style="font-size:22px; font-weight:bold">Agendas Clínica CAT</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Setores")
    setor = st.radio("Setor", SETORES, label_visibility="collapsed")
    st.write("---")
    if st.button("+ Novo Agendamento", width="stretch", type="primary"):
        st.session_state.mostrar_form = True
        st.rerun()
        
        st.write("---")
        if st.button("🚪 Sair", width="stretch"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
if st.session_state.get("mostrar_form", False):
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
                supabase.table("agendamentos").insert({
                    "tipo": tipo_novo,
                    "setor": tipo_novo,
                    "cliente": cliente_novo,
                    "profissional": profissional_novo,
                    "data": str(data_novo),
                    "inicio": inicio_novo.strftime("%H:%M"),
                    "fim": fim_novo.strftime("%H:%M"),
                    "obs": obs_novo,
                    "status": "Pendente",
                    "motivo": ""
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

hoje = date.today()
mes_nome = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"][hoje.month - 1]
st.markdown(f"### Calendário Mensal • {mes_nome} {hoje.year} - {setor}")

# --- LISTA ---
try:
    dados = supabase.table("agendamentos").select("id,setor,data,inicio,fim,cliente,profissional,obs,status,motivo").eq("setor", setor).execute()
    df = pd.DataFrame(dados.data)
    if len(df) > 0:
        df = df.fillna("")
        st.dataframe(df[["setor","data","inicio","fim","cliente","profissional","obs"]], use_container_width=True, hide_index=True)
    else:
        st.info(f"Nenhum agendamento em {setor} ainda.")
        df = pd.DataFrame(columns=["id","setor","data","inicio","fim","cliente","profissional","obs","status","motivo"])
except Exception as e:
    st.info(f"Mostrando agendamentos de {setor} - calendário mensal")
    df = pd.DataFrame(columns=["id","setor","data","inicio","fim","cliente","profissional","obs","status","motivo"])

# --- ALERTAS + RESUMO ---
st.markdown("### 🔔 Painel de Alertas")

if 'status' not in df.columns:
    df['status'] = 'Pendente'
if 'motivo' not in df.columns:
    df['motivo'] = ''

hoje_dt = pd.to_datetime('today').normalize()

for idx, ag in df.iterrows():
    try:
        data_ag = pd.to_datetime(ag['data'])
    except:
        data_ag = hoje_dt
    status_atual = str(ag.get('status', 'Pendente') or 'Pendente').strip()
    if status_atual not in ['Concluído', 'Cancelado'] and data_ag < hoje_dt:
        status_atual = 'Pendente - Atrasado'
    elif status_atual not in ['Concluído', 'Cancelado']:
        status_atual = 'Pendente'

    cor = "🟢" if status_atual == 'Concluído' else "🔴" if status_atual == 'Cancelado' else "🟡"
    st.write(f"{cor} **{ag['data']} {ag['inicio']}-{ag['fim']}** - {ag['setor']} - {ag['cliente']} - {ag['profissional']} - **{status_atual}**")

    if status_atual == 'Cancelado' and str(ag.get('motivo','')) not in ['', 'None']:
        st.caption(f"Motivo: {ag.get('motivo','')}")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("✅ Concluído", key=f"conc_{idx}"):
            supabase.table("agendamentos").update({"status": "Concluído"}).eq("id", ag['id']).execute()
            st.rerun()
    with col2:
        if st.button("❌ Cancelado", key=f"canc_{idx}"):
            st.session_state[f"mostrar_motivo_{idx}"] = True
    with col3:
        if st.session_state.get(f"mostrar_motivo_{idx}", False):
            motivo = st.text_input("Motivo do cancelamento:", key=f"motivo_{idx}")
            if st.button("Salvar cancelamento", key=f"salvar_{idx}"):
                if motivo.strip() == "":
                    st.warning("Escreva o motivo antes de salvar.")
                else:
                    supabase.table("agendamentos").update({"status": "Cancelado", "motivo": motivo}).eq("id", ag['id']).execute()
                    st.rerun()

st.divider()

st.markdown("### 📊 Resumo do Dia")
c1, c2 = st.columns(2)
total = len(df)
confirmados = len(df[df['status'].astype(str) == 'Concluído']) if total > 0 else 0
cancelados = len(df[df['status'].astype(str) == 'Cancelado']) if total > 0 else 0
pendentes = total - confirmados - cancelados
taxa = int(confirmados / total * 100) if total > 0 else 0

c1.metric("Agendamentos", total)
c2.metric("Confirmados", confirmados)
c1.metric("Pendentes", pendentes)
c2.metric("Taxa", f"{taxa}%")
