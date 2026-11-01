import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="GDP Dashboard - CAT",
    page_icon="https://catseguranca.com.br/wp-content/uploads/2023/02/favicon-cat.png",
    layout="wide"
)

st.markdown("""
<div style="display:flex; align-items:center; gap:15px;">
    <img src="https://catseguranca.com.br/wp-content/uploads/2023/02/logo-cat-clinica-alta-tecnologia.png" width="180">
    <h2 style="margin:0; color:#0D2A54;">GDP Dashboard - CAT</h2>
</div><hr>
""", unsafe_allow_html=True)

# ========== SUPABASE ==========
SUPABASE_URL = "https://yukhcpvgnxoqoblhmyuw.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== USUÁRIOS ==========
USUARIOS = {
    "Wagner Carlos": {"senha": "RioVerde@2026!clinica", "setor": "Admin"},
    "comercial@cat": {"senha": "cat123", "setor": "Comercial"},
    "adm@cat": {"senha": "cat123", "setor": "ADM"},
    "seguranca@cat": {"senha": "cat123", "setor": "Segurança"},
    "clinica@cat": {"senha": "cat123", "setor": "Clínica"},
    "rh@cat": {"senha": "cat123", "setor": "RH"},
}

TELEFONES_ALERTA = ["5564999955603", "5564999255538"]

# ========== LOGIN ==========
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.setor = USUARIOS[usuario]["setor"]
            st.rerun()
        else:
            st.error("Login inválido")
    st.stop()

st.sidebar.success(f"{st.session_state.usuario} | {st.session_state.setor}")

# ========== FUNÇÕES SUPABASE ==========
def buscar_agendas():
    try:
        query = supabase.table("agendamentos").select("*").order("data").execute()
        df = pd.DataFrame(query.data)
        if st.session_state.setor != "Admin" and not df.empty:
            df = df[df["setor"] == st.session_state.setor]
        return df
    except Exception as e:
        st.error(f"Erro ao buscar: {e}")
        return pd.DataFrame()

def salvar_agenda(dados):
    supabase.table("agendamentos").insert(dados).execute()

def atualizar_status(id_agenda, status):
    supabase.table("agendamentos").update({"status": status}).eq("id", id_agenda).execute()

# ========== DASHBOARD ==========
df = buscar_agendas()

tab1, tab2 = st.tabs(["📅 Agendas de Hoje", "➕ Nova Agenda"])

with tab1:
    if df.empty:
        st.info("Nenhuma agenda encontrada")
    else:
        hoje = str(date.today())
        df_hoje = df[df["data"] == hoje] if "data" in df.columns else df
        
        for idx, row in df_hoje.iterrows():
            col1, col2, col3, col4 = st.columns([3,2,2,1])
            with col1:
                st.write(f"**{row.get('cliente','')}** - {row.get('tarefa','')} às {row.get('horario','')}")
            with col2:
                st.write(f"Setor: {row.get('setor','')}")
            with col3:
                status = row.get('status','pendente')
                cor = "🟢" if status == "cumprida" else "🔴"
                st.write(f"{cor} {status}")
            with col4:
                if st.button("Concluir", key=row.get('id', idx)):
                    atualizar_status(row.get('id'), "cumprida")
                    st.rerun()

        # ALERTA 18H
        if datetime.now().hour >= 18:
            pendentes = df_hoje[df_hoje["status"] != "cumprida"] if "status" in df_hoje.columns else pd.DataFrame()
            if not pendentes.empty:
                msg = f"🚨 CAT - {len(pendentes)} agendas NÃO cumpridas hoje: " + ", ".join(pendentes["tarefa"].tolist())
                st.error(msg)
                # Aqui dispara para os 2 telefones via sua API
                # requests.post(API, json={"numbers": TELEFONES_ALERTA, "message": msg})

with tab2:
    with st.form("nova_agenda"):
        cliente = st.text_input("Cliente")
        tarefa = st.text_input("Tarefa / Agenda")
        horario = st.time_input("Horário")
        setor = st.selectbox("Setor", ["Comercial","ADM","Segurança","Clínica","RH"]) if st.session_state.setor == "Admin" else st.text_input("Setor", value=st.session_state.setor, disabled=True)
        if st.form_submit_button("Salvar Agenda"):
            dados = {
                "cliente": cliente,
                "tarefa": tarefa,
                "horario": str(horario),
                "setor": setor,
                "data": str(date.today()),
                "status": "pendente",
                "criado_por": st.session_state.usuario
            }
            salvar_agenda(dados)
            st.success("Agenda salva!")

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()
