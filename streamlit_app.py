
import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client

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

# --- CONEXÃO COM SUPABASE VIA SECRETS ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://yukhcpvgnxoqoblhmyuw.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if not SUPABASE_KEY:
    st.error("⚠️ Configure o SUPABASE_KEY em Manage app > Settings > Secrets")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

USUARIOS = {
    "Wagner Carlos": {"senha": "RioVerde@2026!clinica", "setor": "Admin"},
    "comercial@cat": {"senha": "cat123", "setor": "Comercial"},
    "adm@cat": {"senha": "cat123", "setor": "ADM"},
    "seguranca@cat": {"senha": "cat123", "setor": "Segurança"},
    "clinica@cat": {"senha": "cat123", "setor": "Clínica"},
    "rh@cat": {"senha": "cat123", "setor": "RH"},
    "viagens@cat": {"senha": "cat123", "setor": "Agenda de Viagens"},
}

TELEFONES_ALERTA = ["5564999955603", "5564999255538"]

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.subheader("Login - CAT")
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

def buscar_agendas():
    try:
        q = supabase.table("agendamentos").select("*").order("data", desc=False).execute()
        df = pd.DataFrame(q.data)
        # VISIBILIDADE TOTAL - TODOS VEEM TUDO
        return df
    except Exception as e:
        st.error(f"Erro ao buscar: {e}")
        return pd.DataFrame()
        def salvar_agenda(dados):
    try:
        st.write("Tentando salvar:", dados)
        dados_limpos = {k: str(v) for k, v in dados.items() if v is not None and v != ""}
        res = supabase.table("agendamentos").insert(dados_limpos).execute()
        st.success("Salvou com sucesso!")
        return res
    except Exception as e:
        st.error(f"ERRO REAL DO BANCO: {e}")
        st.json(dados)
        raise
    try:
    # Mostra o que está tentando salvar
    st.write("Tentando salvar:", dados)
    dados_limpos = {k: str(v) for k,v in dados.items() if v is not None}
    res = supabase.table("agendamentos").insert(dados_limpos).execute()
    st.success("Salvou!")
    return res
except Exception as e:
    st.error(f"ERRO REAL DO BANCO: {e}")
    st.json(dados)
    raise
    # Mostra o que está tentando salvar
    st.write("Tentando salvar:", dados)
    dados_limpos = {k: str(v) for k,v in dados.items() if v is not None}
    res = supabase.table("agendamentos").insert(dados_limpos).execute()
    st.success("Salvou!")
    return res
except Exception as e:
    st.error(f"ERRO REAL DO BANCO: {e}")
    st.json(dados)
    raise

def atualizar_status(id_a, status):
    supabase.table("agendamentos").update({"status": status}).eq("id", id_a).execute()

df = buscar_agendas()

tab1, tab2 = st.tabs(["📅 Todas as Agendas (Todos veem tudo)", "➕ Nova Agenda"])

with tab1:
    if df.empty:
        st.info("Nenhuma agenda cadastrada")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("Ações de Hoje")
        hoje = str(date.today())
        df_hoje = df[df["data"] == hoje] if "data" in df.columns else df
        for idx, row in df_hoje.iterrows():
            c1,c2,c3,c4 = st.columns([3,2,2,1])
            c1.write(f"**{row.get('cliente','')}** - {row.get('tarefa','')} às {row.get('horario','')} [{row.get('setor','')}]")
            c2.write(f"Por: {row.get('criado_por','')}")
            status = row.get('status','pendente')
            c3.write(f"{'🟢' if status=='cumprida' else '🔴'} {status}")
            if c4.button("Concluir", key=f"c_{row.get('id')}"):
                atualizar_status(row.get('id'), "cumprida")
                st.rerun()

with tab2:
    with st.form("nova"):
        cliente = st.text_input("Cliente")
        tarefa = st.text_input("Tarefa / Agenda")
        horario = st.time_input("Horário")
        setor_opcoes = ["Comercial","ADM","Segurança","Clínica","RH","Agenda de Viagens"]
        setor = st.selectbox("Setor", setor_opcoes)
        data_ag = st.date_input("Data", value=date.today())
        if st.form_submit_button("Salvar"):
            salvar_agenda({
                "cliente": cliente,
                "tarefa": tarefa,
                "horario": str(horario),
                "setor": setor,
                "data": str(data_ag),
                "status": "pendente",
                "criado_por": st.session_state.usuario
            })
            st.success("Agenda salva! Todos os setores já podem ver.")
            st.rerun()

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()
