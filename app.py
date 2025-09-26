# app.py

import streamlit as st
from classes_origami import Origami            # Importa a classe principal
from biblioteca_acoes import BIBLIOTECA_DE_ACOES, Acao # Importa a biblioteca e a classe Acao

# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
st.set_page_config(layout="wide", page_title="Estúdio de Origami Digital")

st.title("Estúdio de Origami Digital")
st.markdown("Crie, analise e visualize os caminhos de ação para construir origamis.")

# --- FUNÇÕES AUXILIARES ---
def popular_exemplos():
    """Cria origamis de exemplo se a lista de salvos estiver vazia."""
    aviao_de_papel = Origami("Avião de Papel Clássico")
    aviao_de_papel.adicionar_passo('DOBRAR_MEIO_D_E')\
              .adicionar_passo('DESDOBRAR_PASSO_ANTERIOR')\
              .adicionar_passo('DOBRAR_CANTO_TD_C')\
              .adicionar_passo('DOBRAR_CANTO_TE_C')\
              .adicionar_passo('DOBRAR_MEIO_D_E')\
              .adicionar_passo('ENTRAR_SETOR_S')\
              .adicionar_passo('DOBRAR_MEIO_E_D')\
              .adicionar_passo('DESDOBRAR_PARCIALMENTE')\
              .adicionar_passo('VIRAR_PAPEL')\
              .adicionar_passo('DOBRAR_MEIO_D_E')\
              .adicionar_passo('DESDOBRAR_PARCIALMENTE')\
              .adicionar_passo('ORIGAMI_FINALIZADO')\
              
    st.session_state.origamis_salvos['Avião de Papel'] = aviao_de_papel

    peixe_papel = Origami("Peixe de Papel")
    peixe_papel.adicionar_passo('DOBRAR_DIAG_TD_BE')\
           .adicionar_passo('DOBRAR_DIAG_TE_BD')\
           .adicionar_passo('DOBRAR_MEIO_D_E')\
           .adicionar_passo('DESDOBRAR_PASSO_ANTERIOR')\
           .adicionar_passo('DESDOBRAR_PASSO_ANTERIOR')\
           .adicionar_passo('DESDOBRAR_PASSO_ANTERIOR')\
           .adicionar_passo('COLAPSAR_LATERAIS')\
           .adicionar_passo('DOBRAR_DIAG_TD_BE')\
           .adicionar_passo('DOBRAR_DIAG_TE_BD')\
           .adicionar_passo('ROTACIONAR_90_D')\
           .adicionar_passo('VIRAR_PAPEL')\
           .adicionar_passo('ORIGAMI_FINALIZADO')\
           
    st.session_state.origamis_salvos['Peixe de Papel'] = peixe_papel

# --- INICIALIZAÇÃO DO SESSION STATE ---
if 'origamis_salvos' not in st.session_state:
    st.session_state['origamis_salvos'] = {}
    popular_exemplos()

# 'caminho_em_criacao' guarda a lista de passos do origami que está sendo criado
if 'caminho_em_criacao' not in st.session_state:
    st.session_state['caminho_em_criacao'] = ['INICIO']

# --- LAYOUT DA INTERFACE ---

st.sidebar.title("Painel de Controle")
modo = st.sidebar.radio(
    "Selecione o Modo de Operação:",
    ("Visualizar Origamis", "Criar Novo Origami", "Analisar Origamis"),
    key="modo_operacao"
)

# ---------------------------------------------------------------------
# MODO 1: VISUALIZAR ORIGAMIS
# ---------------------------------------------------------------------
if modo == "Visualizar Origamis":
    st.header("🖼️ Galeria e Visualizador de Origamis")

    if not st.session_state.origamis_salvos:
        st.warning("Nenhum origami foi criado ainda.")
    else:
        nomes_origamis = list(st.session_state.origamis_salvos.keys())
        nome_selecionado = st.sidebar.selectbox("Escolha um origami para visualizar:", nomes_origamis)
        
        origami_selecionado = st.session_state.origamis_salvos[nome_selecionado]
        st.subheader(f"Analisando: {origami_selecionado.nome}")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("#### 📜 Instruções Passo a Passo")
            instrucoes = origami_selecionado.obter_instrucoes()
            st.code(instrucoes, language=None)
        with col2:
            st.markdown("#### 📈 Grafo de Ações")
            figura_grafo = origami_selecionado.obter_grafo_visual()
            if figura_grafo:
                st.pyplot(figura_grafo)

# ---------------------------------------------------------------------
# MODO 2: CRIAR NOVO ORIGAMI
# ---------------------------------------------------------------------
elif modo == "Criar Novo Origami":
    st.header("✍️ Oficina de Criação")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Ferramentas de Criação")
        
        nome_novo_origami = st.text_input("Nome do Novo Origami:", "Meu Origami")
        
        # Cria uma lista de nomes de ações para o selectbox
        opcoes_acoes = {acao.nome: id_acao for id_acao, acao in BIBLIOTECA_DE_ACOES.items()}
        nome_acao_selecionada = st.selectbox("Escolha a próxima ação:", list(opcoes_acoes.keys()))
        id_acao_selecionada = opcoes_acoes[nome_acao_selecionada]

        if st.button("Adicionar Passo", use_container_width=True, type="primary"):
            st.session_state.caminho_em_criacao.append(id_acao_selecionada)
        
        if st.button("Salvar Origami", use_container_width=True):
            if nome_novo_origami and len(st.session_state.caminho_em_criacao) > 1:
                novo_origami = Origami(nome_novo_origami, id_acao_inicial=st.session_state.caminho_em_criacao[0])
                for passo in st.session_state.caminho_em_criacao[1:]:
                    novo_origami.adicionar_passo(passo)
                
                st.session_state.origamis_salvos[nome_novo_origami] = novo_origami
                st.session_state.caminho_em_criacao = ['INICIO'] # Reseta para o próximo
                st.success(f"Origami '{nome_novo_origami}' salvo com sucesso!")
            else:
                st.error("Por favor, dê um nome ao origami e adicione pelo menos um passo.")
        
        if st.button("Limpar Caminho Atual", use_container_width=True):
            st.session_state.caminho_em_criacao = ['INICIO']
            st.rerun()

    with col2:
        st.markdown("#### Caminho de Ações Atual")
        if st.session_state.caminho_em_criacao:
            for i, id_acao in enumerate(st.session_state.caminho_em_criacao):
                st.text(f"Passo {i}: {BIBLIOTECA_DE_ACOES[id_acao].nome}")
        else:
            st.info("O caminho está vazio. Comece adicionando uma ação.")

# ---------------------------------------------------------------------
# MODO 3: ANALISAR ORIGAMIS
# ---------------------------------------------------------------------
elif modo == "Analisar Origamis":
    st.header("🔬 Laboratório de Análise")

    if len(st.session_state.origamis_salvos) < 2:
        st.warning("Você precisa de pelo menos dois origamis salvos para fazer uma análise.")
    else:
        nomes_origamis = list(st.session_state.origamis_salvos.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            origami_principal_nome = st.selectbox("Selecione a 'Palavra' (Origami Principal):", nomes_origamis, key="principal")
        with col2:
            origami_padrao_nome = st.selectbox("Selecione o 'Padrão' (Origami para Comparar):", nomes_origamis, key="padrao")

        origami_principal = st.session_state.origamis_salvos[origami_principal_nome]
        origami_padrao = st.session_state.origamis_salvos[origami_padrao_nome]

        st.markdown("---")
        st.subheader("Análise de Linguagens Formais (LFA)")

        # Botões para cada análise
        b_col1, b_col2, b_col3 = st.columns(3)
        if b_col1.button("É Prefixo?", use_container_width=True):
            resultado = origami_principal.is_prefixo(origami_padrao)
            st.metric(label=f"'{origami_padrao.nome}' é prefixo de '{origami_principal.nome}'?", value=str(resultado))

        if b_col2.button("É Subpalavra?", use_container_width=True):
            resultado = origami_principal.is_subpalavra(origami_padrao)
            st.metric(label=f"'{origami_padrao.nome}' é subpalavra de '{origami_principal.nome}'?", value=str(resultado))
            
        if b_col3.button("É Sufixo?", use_container_width=True):
            resultado = origami_principal.is_sufixo(origami_padrao)
            st.metric(label=f"'{origami_padrao.nome}' é sufixo de '{origami_principal.nome}'?", value=str(resultado))
        
        st.markdown("---")
        st.subheader("Análise Estrutural de Grafos")

        if st.button("É Subgrafo Induzido?", use_container_width=True):
            resultado = origami_principal.is_subgrafo_induzido(origami_padrao)
            st.metric(label=f"'{origami_padrao.nome}' é subgrafo induzido de '{origami_principal.nome}'?", value=str(resultado))

        st.markdown("---")
        st.subheader("Visualização Comparativa")

        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.pyplot(origami_principal.obter_grafo_visual())
        with v_col2:
            st.pyplot(origami_padrao.obter_grafo_visual())