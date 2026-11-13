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
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span { color: white; }
[data-testid="stSidebar"] button, [data-testid="stSidebar"] button p, [data-testid="stSidebar"] button span {
    background-color: white !important;
    color: #0F2F5E !important;
    font-weight: bold !important;
}
[data-testid="stSidebar"] button:hover, [data-testid="stSidebar"] button:hover p {
    background-color: #FF4B4B !important;
    color: white !important;
}
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
        st.session_state.logado = False
        st.session_state.mostrar_form = False
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

st.divider()
st.markdown("### 📋 Relatório Diário")

data_rel = st.date_input("Escolha o dia do relatório", value=date.today(), key="data_relatorio")

df_rel = df[df['data'].astype(str) == str(data_rel)] if len(df) > 0 else df

if len(df_rel) == 0:
    st.info(f"Nenhum agendamento em {setor} no dia {data_rel.strftime('%d/%m/%Y')}.")
else:
    def status_final_rel(row):
        s = str(row.get('status', 'Pendente') or 'Pendente').strip()
        try:
            d = pd.to_datetime(row['data'])
        except:
            d = hoje_dt
        if s not in ['Concluído', 'Cancelado'] and d < hoje_dt:
            return 'Pendente - Atrasado'
        if s not in ['Concluído', 'Cancelado']:
            return 'Pendente'
        return s

    df_rel = df_rel.copy()
    df_rel['status_final'] = df_rel.apply(status_final_rel, axis=1)

    concluidas = df_rel[df_rel['status_final'] == 'Concluído']
    canceladas_rel = df_rel[df_rel['status_final'] == 'Cancelado']
    pendentes_rel = df_rel[df_rel['status_final'].str.contains('Pendente')]
    total_rel = len(df_rel)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total do dia", total_rel)
    c2.metric("✅ Concluídas", len(concluidas))
    c3.metric("❌ Canceladas", len(canceladas_rel))
    c4.metric("🟡 Pendentes", len(pendentes_rel))

    st.markdown("#### ✅ Concluídas")
    if len(concluidas) > 0:
        for _, r in concluidas.iterrows():
            st.write(f"{r['inicio']}-{r['fim']} - {r['cliente']} - {r['profissional']}")
    else:
        st.write("Nenhuma")

    st.markdown("#### ❌ Canceladas")
    if len(canceladas_rel) > 0:
        for _, r in canceladas_rel.iterrows():
            st.write(f"{r['inicio']}-{r['fim']} - {r['cliente']} - Motivo: {r.get('motivo','')}")
    else:
        st.write("Nenhuma")

    st.markdown("#### 🟡 Pendentes")
    if len(pendentes_rel) > 0:
        for _, r in pendentes_rel.iterrows():
            st.write(f"{r['inicio']}-{r['fim']} - {r['cliente']} - {r['profissional']} - {r['status_final']}")
    else:
        st.write("Nenhuma")

    # Texto do relatório
    texto = f"RELATORIO {setor} - {data_rel.strftime('%d/%m/%Y')}\nTotal: {total_rel} | Concluidas: {len(concluidas)} | Canceladas: {len(canceladas_rel)} | Pendentes: {len(pendentes_rel)}\n\n"
    for _, r in concluidas.iterrows():
        texto += f"✅ {r['inicio']}-{r['fim']} - {r['cliente']} - {r['profissional']}\n"
    for _, r in canceladas_rel.iterrows():
        texto += f"❌ {r['inicio']}-{r['fim']} - {r['cliente']} - Motivo: {r.get('motivo','')}\n"
    for _, r in pendentes_rel.iterrows():
        texto += f"🟡 {r['inicio']}-{r['fim']} - {r['cliente']} - {r['profissional']}\n"

    # Enviar pros 2 números
    import urllib.parse
    NUMEROS = ["5564999955603", "5564981318325"]
    msg_cod = urllib.parse.quote(texto)

    st.markdown("#### 📤 Enviar relatório")
    c1, c2 = st.columns(2)
    c1.link_button("📲 Enviar - 99995-5603", f"https://wa.me/{NUMEROS[0]}?text={msg_cod}", use_container_width=True)
    c2.link_button("📲 Enviar - 98131-8325", f"https://wa.me/{NUMEROS[1]}?text={msg_cod}", use_container_width=True)

    st.download_button("📥 Baixar Relatório", data=texto, file_name=f"relatorio_{setor}_{data_rel}.txt", mime="text/plain")
