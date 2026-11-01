import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import date
import urllib.parse

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="GDP - Agendamentos por Setor", layout="wide", page_icon="📋")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("Login GDP")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar", type="primary"):
        if usuario and senha:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.rerun()
    st.stop()

TIPOS_POR_SETOR = {
    "Técnico": ["Visita Técnica", "Treinamento", "Palestras", "DDS"],
    "Clínico": ["Viagem", "Substituição do Médico"],
    "Recepção": ["Gerar ASOs", "Viagem"],
    "Administrativo": ["Afastamento", "Folga", "Férias"]
}

def gerar_link_whatsapp(telefone, mensagem):
    tel = "".join(filter(str.isdigit, telefone))
    if not tel.startswith("55"):
        tel = "55" + tel
    msg_encoded = urllib.parse.quote(mensagem)
    return f"https://wa.me/{tel}?text={msg_encoded}"

st.sidebar.title(f"Olá, {st.session_state.usuario}")
setor_selecionado = st.sidebar.selectbox("Setor", list(TIPOS_POR_SETOR.keys()))
tipo_selecionado = st.sidebar.selectbox("Tipo de Serviço", TIPOS_POR_SETOR[setor_selecionado])
menu = st.sidebar.radio("Menu", ["📝 Novo Agendamento", "📋 Lista de Agendamentos", "⚠️ Não Concluídos / Alertas"])

if menu == "📝 Novo Agendamento":
    st.header(f"Novo - {setor_selecionado} / {tipo_selecionado}")
    with st.form("form_agendamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        empresa = col1.text_input("Empresa / Cliente *")
        colaborador = col2.text_input("Colaborador / Médico / Responsável *")
        col3, col4, col5 = st.columns(3)
        data_inicio = col3.date_input("Data Início *", value=date.today())
        data_fim = col4.date_input("Data Fim", value=date.today())
        hora = col5.text_input("Hora", placeholder="08:00")
        col6, col7 = st.columns(2)
        origem = col6.text_input("Origem")
        destino = col7.text_input("Destino")
        telefone = st.text_input("Telefone WhatsApp", placeholder="62999999999")
        observacao = st.text_area("Observação / Detalhes")
        enviar = st.form_submit_button("💾 Salvar Agendamento", type="primary")
        if enviar:
            if not empresa or not colaborador:
                st.error("Preencha Empresa e Colaborador")
            else:
                dados = {
                    "setor": setor_selecionado, "tipo": tipo_selecionado,
                    "empresa": empresa, "cliente": empresa, "colaborador": colaborador,
                    "medico": colaborador if setor_selecionado == "Clínico" else "",
                    "origem": origem, "destino": destino,
                    "data_inicio": str(data_inicio), "data_fim": str(data_fim),
                    "hora": hora, "status": "Pendente",
                    "observacao": f"Tel: {telefone} | {observacao}",
                    "criado_por": st.session_state.usuario
                }
                try:
                    supabase.table("agendamentos_geral").insert(dados).execute()
                    st.success(f"Salvo: {tipo_selecionado}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro: {e}")

elif menu == "📋 Lista de Agendamentos":
    st.header(f"Lista - {setor_selecionado}")
    filtro = st.selectbox("Filtrar Status", ["Todos", "Pendente", "Em Andamento", "Concluído", "Cancelado"])
    q = supabase.table("agendamentos_geral").select("*").eq("setor", setor_selecionado).order("data_inicio", desc=True)
    if filtro != "Todos":
        q = q.eq("status", filtro)
    res = q.execute()
    dados = res.data
    if not dados:
        st.info("Nenhum agendamento.")
    else:
        df = pd.DataFrame(dados)
        st.dataframe(df, use_container_width=True)
        sel = st.selectbox("Selecione para atualizar", [f"{d['id']} | {d['empresa']} | {d['tipo']} | {d['status']}" for d in dados])
        novo_status = st.selectbox("Novo Status", ["Pendente", "Em Andamento", "Concluído", "Cancelado"])
        if st.button("Atualizar Status"):
            id_real = sel.split(" | ")[0]
            supabase.table("agendamentos_geral").update({"status": novo_status}).eq("id", id_real).execute()
            st.success("Atualizado!")
            st.rerun()
else:
    st.header("⚠️ Não Concluídos / Atrasados")
    hoje = str(date.today())
    res = supabase.table("agendamentos_geral").select("*").neq("status", "Concluído").neq("status", "Cancelado").lt("data_inicio", hoje).execute()
    if not res.data:
        st.success("Nenhum atrasado! Tudo em dia.")
    else:
        st.warning(f"{len(res.data)} atrasado(s)")
        for item in res.data:
            with st.expander(f"🔴 {item['data_inicio']} - {item['setor']} | {item['tipo']} | {item['empresa']} - {item['colaborador']}", expanded=True):
                st.write(f"Status: {item['status']} | Obs: {item.get('observacao','')}")
                tel = st.text_input("Telefone", key=f"tel_{item['id']}", placeholder="62999999999")
                msg = f"Olá {item['colaborador']}! O agendamento de {item['tipo']} da empresa {item['empresa']} do dia {item['data_inicio']} ainda está como {item['status']}. Pode atualizar? - GDP"
                msg_edit = st.text_area("Mensagem", value=msg, key=f"msg_{item['id']}")
                if st.button("📲 Gerar Link WhatsApp", key=f"btn_{item['id']}"):
                    if tel:
                        link = gerar_link_whatsapp(tel, msg_edit)
                        st.link_button("Abrir WhatsApp", link)
                    else:
                        st.error("Digite o telefone")
                if st.button("✅ Marcar Concluído", key=f"ok_{item['id']}"):
                    supabase.table("agendamentos_geral").update({"status": "Concluído"}).eq("id", item['id']).execute()
                    st.rerun()

st.sidebar.divider()
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()
