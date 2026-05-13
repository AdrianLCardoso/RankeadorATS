import streamlit as st
import plotly.express as px
import pandas as pd
import os
import database
from main import extrair_texto_pdf, analisar_cv_com_ia 
from database import criar_tabela, autenticar_usuario, criar_usuario, registrar_log, obter_metricas_admin

# 1. SETUP INICIAL
database.criar_tabela()
st.set_page_config(page_title="Rankeador On-line📈", layout="wide")
criar_tabela()

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

# BLOQUEIO DE TRADUÇÃO AUTOMÁTICA
st.markdown("""<head><meta name="google" content="notranslate"></head>""", unsafe_allow_html=True)

# 2. SISTEMA DE ACESSO
if not st.session_state['logado']:
    st.title("🔐 Acesso ao Rankeador")
    tab_l, tab_c = st.tabs(["Login", "Cadastro"])
    with tab_l:
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            user = autenticar_usuario(email, senha)
            if user:
                st.session_state.update({'logado': True, 'usuario': user[0], 'tipo': user[2]})
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
    with tab_c:
        n_email = st.text_input("Novo E-mail")
        n_senha = st.text_input("Nova Senha", type="password")
        if st.button("Criar Conta"):
            if criar_usuario(n_email, n_senha):
                st.success("Conta criada! Faça o login.")
            else:
                st.warning("E-mail já cadastrado.")
    st.stop()

# 3. SIDEBAR[cite: 7]
with st.sidebar:
    st.header("🎯 Parâmetros")
    empresa = st.text_input("Empresa")
    cargo = st.text_input("Cargo")
    vaga_desc = st.text_area("Descrição da Vaga", height=200)
    if st.button("🚪 Sair"):
        st.session_state['logado'] = False
        st.rerun()

# 4. PAINEL ADMIN[cite: 7]
if st.session_state.get('tipo') == 'admin':
    with st.expander("🛠️ PAINEL ADMINISTRATIVO"):
        u, a, logs = obter_metricas_admin()
        c_a1, c_a2 = st.columns(2)
        c_a1.metric("Usuários", u)
        c_a2.metric("Análises", a)
        st.dataframe(logs, use_container_width=True)

# 5. EXECUÇÃO[cite: 7]
st.title("📑 Análise de Currículo ATS")
formatos_aceitos = ["pdf"]
file = st.file_uploader("Carregar Currículo", 
    type = formatos_aceitos,
    help = "Dica: Use arquivos com texto extraível para melhor precisão"
)

if st.button("Analisar") and file and vaga_desc:
    with st.spinner('Analisando perfil técnico...'):
        with open("temp.pdf", "wb") as f:
            f.write(file.getbuffer())
        
        texto = extrair_texto_pdf("temp.pdf")
        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")
        
        res = analisar_cv_com_ia(texto, vaga_desc, empresa, cargo)
        
        if "error" in res:
            st.warning(res["error"])
            st.stop()

        registrar_log(st.session_state['usuario'], empresa, cargo, res.get('score', 0))

        # 6. RESULTADOS[cite: 7]
        tab1, tab2 = st.tabs(["📊 Score e Radar", "🏢 Sobre a Empresa"])

        with tab1:
            est = res.get('ats_estimativa', {})
            logos = {
                "Gupy": "assets/gupy.png",
                "Sólides": "assets/solides.png",
                "Workday": "assets/workday.png",
                "Dia de trabalho": "assets/workday.png",
                "Linkedin": "assets/linkedin.png"
            }
            cols = st.columns(len(est) if est else 1)
            for i, (p, v) in enumerate(est.items()):
                with cols[i]:
                    # Exibe a logo se a plataforma estiver no dicionário
                    if p in logos:
                        st.image(logos[p], width=80)
                    
                    st.metric(p, f"{v}%")
                    st.progress(v/100)
            
            st.divider()
            c_score, c_radar = st.columns([1, 1.5])
            
            with c_score:
                st.write("#### 💡 Sugestões")
                for s in res.get('sugestoes', []):
                    st.caption(f"• {s}")
            
            with c_radar:
                # ROSE CHART[cite: 7]
                comp = res.get('competencias', {})
                if comp:
                    df_r = pd.DataFrame({'Hab': list(comp.keys()), 'Nível': list(comp.values())})
                    fig = px.bar_polar(
                        df_r, r='Nível', theta='Hab', color='Nível', 
                        template="plotly_dark", color_continuous_scale="Teal"
                    )
                    fig.update_layout(
                        polar=dict(radialaxis=dict(range=[0, 100], showticklabels=True)),
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            info = res.get('empresa_pesquisa', {})
            st.subheader(f"🏢 Panorama: {empresa}")
            st.info(info.get('o_que_faz', 'N/A'))
            
            sal = info.get('salarios', {})
            s1, s2, s3 = st.columns(3)
            s1.metric("Média de Mercado Jr", sal.get('Jr', 'N/A'))
            s2.metric("Média de Mercado Pl", sal.get('Pl', 'N/A'))
            s3.metric("Média de Mercado Sr", sal.get('Sr', 'N/A'))
            
            st.divider()
            st.write(f"**⭐ Satisfação:** {info.get('satisfacao', 'N/A')}")
            st.write(f"**🧬 Cultura:** {info.get('cultura', 'N/A')}")
            st.write(f"**✅  Veracidade da Vaga:** {info.get('veracidade_da_vaga', 'N/A')}")
