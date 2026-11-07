import streamlit as st

if "agendamentos" not in st.session_state:
    st.session_state.agendamentos = []
    from supabase import create_client
import pandas as pd
from datetime import datetime

# --- CONFIG SUPABASE (mantém o seu que já funciona) ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ÍCONE OFICIAL CAT ---
st.set_page_config(
    page_title="Agendas Clínica CAT",
    layout="wide",
    page_icon="CAT_Agenda_512.png",
    initial_sidebar_state="expanded"
)

# --- ESTILO OFICIAL CAT ---
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0F2F5E; }
[data-testid="stSidebar"] * { color: white; }
.stButton>button[kind="primary"] { background-color: #00B4D8; border: none; }
.cat-header {
    background: #0A1931;
    padding: 18px 25px;
    border-radius: 0px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -60px -60px 20px -60px;
    padding-left: 40px;
}
</style>
""", unsafe_allow_html=True)

# --- LOGIN (mantém seu login atual) ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("### Login Clínica CAT")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # aqui mantém sua lógica de login do Supabase
        st.session_state.logado = True
        st.rerun()
else:
    # --- HEADER ---
    st.markdown("""
    <div class="cat-header">
        <div style="display:flex; align-items:center; gap:15px">
            <img src="https://via.placeholder.com/80x80/0A1931/FFFFFF?text=CAT" style="height:50px">
            <div style="color:white">
                <div style="font-weight:bold">CAT Segurança e Saúde no Trabalho</div>
                <div style="font-size:22px; font-weight:bold">Agendas Clínica CAT</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR SETORES ---
    with st.sidebar:
        st.markdown("#### SETORES")
        setor = st.radio("Setor", ["Recepção", "Visita técnica", "Treinamentos NRs", "Viagens", "Palestras NR1", "Palestras Saúde", "OUTROS"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("+ Novo Agendamento", use_container_width=True):
            st.session_state.novo = True
        # --- FORMULÁRIO NOVO AGENDAMENTO ---
if st.session_state.get("novo", False):
    with st.form("novo_agendamento"):
        nome = st.text_input("Nome do colaborador")
        data = st.date_input("Data")
        horario = st.time_input("Horário")
        setor_novo = st.selectbox("Setor", ["Recepção", "Enfermagem", "Médico", "Outros"])
        obs = st.text_area("Observação")
        salvar = st.form_submit_button("Salvar Agendamento", use_container_width=True)
        cancelar = st.form_submit_button("Cancelar", use_container_width=True)
        if salvar:
            st.session_state.agendamentos.append({
                "nome": nome,
                "data": str(data),
                "horario": str(horario),
                "setor": setor_novo,
                "obs": obs
            })
            st.success(f"Agendamento salvo para {nome} em {data}!")
            st.session_state.novo = False
            st.rerun()
        if cancelar:
            st.session_state.novo = False
            st.rerun()
            st.session_state.agendamentos.append({
                "nome": nome,
                "data": str(data),
                "horario": str(horario),
                "setor": setor_novo,
                "obs": obs
            })
            st.success(f"Agendamento salvo para {nome} em {data}!")
            st.session_state.novo = False
            st.rerun()
        if cancelar:
            st.session_state.novo = False
            st.rerun()

# --- CONTEÚDO PRINCIPAL NO LEIAUTE DA FOTO ---
    # --- CONTEÚDO PRINCIPAL NO LEIAUTE DA FOTO ---
    col_cal, col_alertas = st.columns([2.5, 1])

    with col_cal:
        st.markdown(f"### Calendário Mensal • Novembro 2024 - {setor}")
        # Aqui entra seu calendário que já funciona
        # Exemplo: buscar agendamentos do setor selecionado
        try:
            dados = supabase.table("agendamentos").select("*").eq("setor", setor).execute()
            df = pd.DataFrame(dados.data)
            st.dataframe(df, use_container_width=True)
        except:
            st.info(f"Mostrando agendamentos de {setor} - calendário mensal")

    with col_alertas:
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
