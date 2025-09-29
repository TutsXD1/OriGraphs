# app.py

import streamlit as st
from classes_origami import Origami            # Importa a classe principal
from biblioteca_acoes import BIBLIOTECA_DE_ACOES, Acao # Importa a biblioteca e a classe Acao

# --- CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
st.set_page_config(layout="wide", page_title="OriGraphs")

st.title("Origraphs - Desenvolvimento de Origamis com Grafos")
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
        nome_selecionado = st.selectbox("Escolha um origami para visualizar:", nomes_origamis)
        
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

        btn_add, btn_rmv = st.columns(2)
        
        if btn_add.button("Adicionar Passo", use_container_width=True, type="primary"):
            st.session_state.caminho_em_criacao.append(id_acao_selecionada)

        if btn_rmv.button("Remover Último Passo", use_container_width=True, type="secondary"):
            if len(st.session_state.caminho_em_criacao) > 1:
                st.session_state.caminho_em_criacao.pop()
            else:
                st.warning("Não é possível remover o passo inicial.")
        
        st.markdown("---")  
        
        st.markdown("#### Incorporar Modelo")
        if len(st.session_state.origamis_salvos) > 0:
            nome_origami_para_incorporar = st.selectbox(
                "Use um origami salvo como parte do novo:",
                list(st.session_state.origamis_salvos.keys())
            )
            if st.button("Incorporar Passos", use_container_width=True):
                origami_a_incorporar = st.session_state.origamis_salvos[nome_origami_para_incorporar]
                passos_originais = origami_a_incorporar.caminho_de_acoes

                inicio_slice = 1
                fim_slice = len(passos_originais)
                if passos_originais[-1] == 'ORIGAMI_FINALIZADO':
                    fim_slice -= 1


                # Pega os passos do outro origami, ignorando o passo 'INICIO' [1:]
                passos_para_adicionar = origami_a_incorporar.caminho_de_acoes[inicio_slice:fim_slice]
                st.session_state.caminho_em_criacao.extend(passos_para_adicionar)
                st.success(f"Passos de '{nome_origami_para_incorporar}' incorporados!")
        else:
            st.info("Nenhum origami salvo para incorporar.")

        st.markdown("---")

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

    if not st.session_state.origamis_salvos:
        st.warning("Você precisa de pelo menos um origami salvo para fazer uma análise.")
    else:
        # Cria as duas abas para os modos de análise
        tab_singular, tab_comparativa = st.tabs(["Análise Singular", "Análise Comparativa"])

        # --- ABA DE ANÁLISE SINGULAR ---
        with tab_singular:
            st.subheader("Análise de um Único Origami")
            
            nomes_origamis = list(st.session_state.origamis_salvos.keys())
            nome_selecionado = st.selectbox("Escolha um origami para analisar:", nomes_origamis, key="singular_select")
            origami_selecionado = st.session_state.origamis_salvos[nome_selecionado]

            st.markdown("---")
            
            # Funcionalidade de Grau do Vértice
            st.markdown("#### Grau dos Vértices (Ações)")
            acoes_no_grafo = sorted(list(set(origami_selecionado.caminho_de_acoes)))
            nomes_acoes_no_grafo = [BIBLIOTECA_DE_ACOES[id_acao].nome for id_acao in acoes_no_grafo]
            acao_para_grau = st.selectbox("Selecione uma ação para ver seu grau:", nomes_acoes_no_grafo)

            if st.button("Calcular Grau", use_container_width=True):
                grau_entrada, grau_saida = origami_selecionado.obter_grau_vertice(acao_para_grau)
                if grau_entrada is not None:
                    g_col1, g_col2 = st.columns(2)
                    g_col1.metric("Grau de Entrada (In-Degree)", grau_entrada)
                    g_col2.metric("Grau de Saída (Out-Degree)", grau_saida)
                else:
                    st.error("Ação não encontrada no grafo.")
            
            st.markdown("---")

            # Funcionalidade de Coloração do Grafo
            st.markdown("#### Coloração de Vértices")
            if st.button("Aplicar Coloração e Calcular Número Cromático", use_container_width=True, type="primary"):
                figura_colorida, num_cromatico = origami_selecionado.obter_grafo_colorido()
                if figura_colorida:
                    st.pyplot(figura_colorida)
                    st.metric("Número Cromático", num_cromatico)
                else:
                    st.info("Origami sem passos suficientes para colorir.")


        # --- ABA DE ANÁLISE COMPARATIVA ---
        with tab_comparativa:
            st.subheader("Análise Comparativa entre Dois Origamis")
            if len(st.session_state.origamis_salvos) < 2:
                st.warning("Você precisa de pelo menos dois origamis salvos para esta análise.")
            else:
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    origami_principal_nome = st.selectbox("Selecione o Origami Principal (G):", nomes_origamis, key="principal_comp")
                with c_col2:
                    origami_padrao_nome = st.selectbox("Selecione o Origami para Comparar (H):", nomes_origamis, key="padrao_comp")
                
                origami_principal = st.session_state.origamis_salvos[origami_principal_nome]
                origami_padrao = st.session_state.origamis_salvos[origami_padrao_nome]

                st.markdown("---")
                st.markdown("##### Análise de Linguagens Formais (LFA)")
                lfa_cols = st.columns(3)
                if lfa_cols[0].button("É Prefixo?", use_container_width=True):
                    st.metric("Resultado:", str(origami_principal.is_prefixo(origami_padrao)))
                if lfa_cols[1].button("É Subpalavra?", use_container_width=True):
                    st.metric("Resultado:", str(origami_principal.is_subpalavra(origami_padrao)))
                if lfa_cols[2].button("É Sufixo?", use_container_width=True):
                    st.metric("Resultado:", str(origami_principal.is_sufixo(origami_padrao)))

                st.markdown("---")
                st.markdown("##### Análise Estrutural de Grafos")
                grafo_cols = st.columns(2)
                if grafo_cols[0].button("É Subgrafo Induzido?", use_container_width=True):
                    st.metric("Resultado:", str(origami_principal.is_subgrafo_induzido(origami_padrao)))
                # Adiciona o novo botão de subgrafo gerador
                if grafo_cols[1].button("É Subgrafo Gerador?", use_container_width=True):
                    st.metric("Resultado:", str(origami_principal.is_subgrafo_gerador(origami_padrao)))