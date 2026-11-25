"""
app.py

Interface web interativa em Streamlit para o framework educacional OriGraphs.
Inclui invalidação automática de cache de sessão (ORIGRAPHS_ENGINE_VERSION)
e verificação de figura não-nula antes de st.pyplot().
"""

import streamlit as st
import matplotlib.pyplot as plt
from classes_origami import Origami
from biblioteca_acoes import BIBLIOTECA_DE_ACOES

ORIGRAPHS_ENGINE_VERSION = "2.2"

st.set_page_config(layout="wide", page_title="OriGraphs")

st.title("OriGraphs - Desenvolvimento de Origamis com Grafos e Álgebra Linear")
st.markdown(
    "Modele sequências de dobras como palavras de uma **Linguagem Formal**, "
    "visualize o **Digrafo de Transições** e inspecione a **Malha Geométrica 2D** do papel."
)


def popular_exemplos() -> None:
    """Cria origamis clássicos de exemplo na galeria."""
    aviao_de_papel = Origami("Avião de Papel Clássico")
    (
        aviao_de_papel
        .adicionar_passo('DOBRAR_MEIO_D_E')
        .adicionar_passo('DESDOBRAR_PASSO_ANTERIOR')
        .adicionar_passo('DOBRAR_CANTO_TD_C')
        .adicionar_passo('DOBRAR_CANTO_TE_C')
        .adicionar_passo('DOBRAR_MEIO_D_E')
        .adicionar_passo('ENTRAR_SETOR_S')
        .adicionar_passo('DOBRAR_MEIO_E_D')
        .adicionar_passo('DESDOBRAR_PARCIALMENTE')
        .adicionar_passo('VIRAR_PAPEL')
        .adicionar_passo('DOBRAR_MEIO_D_E')
        .adicionar_passo('DESDOBRAR_PARCIALMENTE')
        .adicionar_passo('ORIGAMI_FINALIZADO')
    )
    st.session_state.origamis_salvos['Avião de Papel'] = aviao_de_papel

    boi = Origami("Boi")
    (
        boi
        .adicionar_passo('DOBRAR_DIAG_TE_BD')
        .adicionar_passo('ROTACIONAR_45_D')
        .adicionar_passo('ENTRAR_SETOR_B')
        .adicionar_passo('DOBRAR_MEIO_B_T')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ENTRAR_SETOR_T')
        .adicionar_passo('DOBRAR_MEIO_T_B')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ENTRAR_SETOR_D')
        .adicionar_passo('DOBRAR_DIAG_BD_TE')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ENTRAR_SETOR_E')
        .adicionar_passo('DOBRAR_DIAG_BE_TD')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ORIGAMI_FINALIZADO')
    )
    st.session_state.origamis_salvos['Boi'] = boi


    cachorro = Origami("Cachorro")
    (
        cachorro
        .adicionar_passo('DOBRAR_DIAG_TE_BD')
        .adicionar_passo('ROTACIONAR_45_D')
        .adicionar_passo('ENTRAR_SETOR_B')
        .adicionar_passo('DOBRAR_MEIO_B_T')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ENTRAR_SETOR_D')
        .adicionar_passo('DOBRAR_CANTO_TD_C')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ENTRAR_SETOR_E')
        .adicionar_passo('DOBRAR_CANTO_TE_C')
        .adicionar_passo('SAIR_SETOR_ANTERIOR')
        .adicionar_passo('ORIGAMI_FINALIZADO')
    )
    st.session_state.origamis_salvos['Cachorro'] = cachorro


# Reinicializa automaticamente a memória se a versão do motor mudou
if (
    'origamis_salvos' not in st.session_state
    or st.session_state.get('engine_version') != ORIGRAPHS_ENGINE_VERSION
):
    st.session_state['origamis_salvos'] = {}
    st.session_state['engine_version'] = ORIGRAPHS_ENGINE_VERSION
    popular_exemplos()

if 'caminho_em_criacao' not in st.session_state:
    st.session_state['caminho_em_criacao'] = ['INICIO']

# --- BARRA LATERAL ---
st.sidebar.title("Painel de Controle")
modo = st.sidebar.radio(
    "Selecione o Modo de Operação:",
    ("Visualizar Origamis", "Criar Novo Origami", "Analisar Origamis"),
    key="modo_operacao"
)

# =====================================================================
# MODO 1: VISUALIZAR ORIGAMIS
# =====================================================================
if modo == "Visualizar Origamis":
    st.header("🖼️ Galeria e Visualizador de Origamis")

    if not st.session_state.origamis_salvos:
        st.warning("Nenhum origami foi criado ainda.")
    else:
        nomes_origamis = list(st.session_state.origamis_salvos.keys())
        nome_selecionado = st.selectbox("Escolha um origami para visualizar:", nomes_origamis)
        origami_selecionado: Origami = st.session_state.origamis_salvos[nome_selecionado]

        st.subheader(f"Analisando: {origami_selecionado.nome}")

        total_passos = len(origami_selecionado.caminho_de_acoes) - 1
        passo_atual = st.slider(
            "Inspecionar evolução de estados (Prefixo da Palavra Formal):",
            min_value=0,
            max_value=max(0, total_passos),
            value=max(0, total_passos),
            help="Deslize para observar a transformação afim acumulada até o passo escolhido."
        )
        acao_passo = BIBLIOTECA_DE_ACOES[origami_selecionado.caminho_de_acoes[passo_atual]]
        st.info(
            f"**Passo {passo_atual} — `{acao_passo.nome}`** "
            f"| **Operação:** `{acao_passo.tipo_operacao}` "
            f"| **Axioma:** `{acao_passo.axioma or 'N/A'}` "
            f"| **Equação:** `{acao_passo.equacao_simbolica}`\n\n"
            f"_{acao_passo.descricao}_"
        )

        col_malha, col_grafo = st.columns([1.15, 1])

        with col_malha:
            st.markdown("#### 📐 Malha 2D do Papel e Padrão de Vincos")
            fig_papel = origami_selecionado.obter_imagem_papel(
                ate_passo=passo_atual, mostrar_vincos=True
            )
            if fig_papel is not None:
                st.pyplot(fig_papel)
                plt.close(fig_papel)

            props = origami_selecionado.motor_grafico.avaliar_propriedades_fisicas()
            c1, c2, c3 = st.columns(3)
            c1.metric("Vincos Vale (V)", props["vincos_vale"])
            c2.metric("Vincos Pico (M)", props["vincos_pico"])
            c3.metric("Camadas Z Ativas", props["camadas_z"])

        with col_grafo:
            st.markdown("#### 📈 Digrafo de Ações (NetworkX)")
            figura_grafo = origami_selecionado.obter_grafo_visual()
            if figura_grafo is not None:
                st.pyplot(figura_grafo)
                plt.close(figura_grafo)
            else:
                st.info("Adicione pelo menos 2 passos para visualizar o digrafo.")

        with st.expander("📜 Ver Instruções Textuais Completas e Palavra Formal", expanded=False):
            st.markdown(
                f"**Palavra Formal ($w \\in \\Sigma^*$):** "
                f"`{' -> '.join(origami_selecionado.caminho_de_acoes)}`"
            )
            st.code(origami_selecionado.obter_instrucoes(), language=None)

# =====================================================================
# MODO 2: CRIAR NOVO ORIGAMI (OFICINA DE CRIAÇÃO GUIADA)
# =====================================================================
elif modo == "Criar Novo Origami":
    st.header("✍️ Oficina de Criação Geométrica")

    origami_temp = Origami(
        "Em Construção",
        id_acao_inicial=st.session_state.caminho_em_criacao[0]
    )
    for p in st.session_state.caminho_em_criacao[1:]:
        origami_temp.adicionar_passo(p)
    motor_temp = origami_temp.simular_geometria_papel()
    x0, x1, y0, y1 = motor_temp.obter_bbox_ativa()

    col_ferramentas, col_preview = st.columns([1.1, 2.0])

    with col_ferramentas:
        st.markdown("#### 1. Identificação do Modelo")
        nome_novo_origami = st.text_input("Nome do Novo Origami:", "Meu Origami")

        st.markdown("---")
        st.markdown("#### 2. Escolha da Próxima Operação")

        categorias = {
            "1. Dobras ao Meio (Axioma A2)": [
                'DOBRAR_MEIO_D_E', 'DOBRAR_MEIO_E_D', 'DOBRAR_MEIO_B_T', 'DOBRAR_MEIO_T_B'
            ],
            "2. Dobras na Diagonal (Axioma A1)": [
                'DOBRAR_DIAG_BE_TD', 'DOBRAR_DIAG_TD_BE', 'DOBRAR_DIAG_BD_TE', 'DOBRAR_DIAG_TE_BD'
            ],
            "3. Dobras Canto ao Centro (Axioma A2)": [
                'DOBRAR_CANTO_TD_C', 'DOBRAR_CANTO_TE_C', 'DOBRAR_CANTO_BD_C', 'DOBRAR_CANTO_BE_C'
            ],
            "4. Dobras Vale & Pico Inclinadas": [
                'DOBRA_VALE_TD_BC', 'DOBRA_VALE_TE_BC', 'DOBRA_PICO_BD_TC', 'DOBRA_PICO_BE_TC'
            ],
            "5. Seleção de Setores e Abas (Camadas Z)": [
                'ENTRAR_SETOR_S', 'ENTRAR_SETOR_I', 'ENTRAR_SETOR_D',
                'ENTRAR_SETOR_E', 'ENTRAR_SETOR_T', 'ENTRAR_SETOR_B', 'SAIR_SETOR_ANTERIOR'
            ],
            "6. Desdobraduras (Total e 2.5D)": [
                'DESDOBRAR_PASSO_ANTERIOR', 'DESDOBRAR_PARCIALMENTE', 'ABRIR_ABA'
            ],
            "7. Rotações e Virada de Papel": [
                'VIRAR_PAPEL', 'ROTACIONAR_90_D', 'ROTACIONAR_90_E',
                'ROTACIONAR_45_D', 'ROTACIONAR_45_E', 'ROTACIONAR_180'
            ],
            "8. Dobras Compostas & Finalização": [
                'COLAPSAR_LATERAIS', 'DOBRA_ESMAGADA', 'DOBRA_PETALA',
                'ORELHA_DE_COELHO', 'DOBRA_REVERSA_INTERNA', 'DOBRA_REVERSA_EXTERNA',
                'AFUNDAR_PONTA', 'VINCO_PREGAS', 'ORIGAMI_FINALIZADO'
            ],
        }

        categoria_sel = st.selectbox("Categoria Geométrica:", list(categorias.keys()))
        chaves_cat = categorias[categoria_sel]

        opcoes_cat = {BIBLIOTECA_DE_ACOES[k].nome: k for k in chaves_cat}
        nome_acao_sel = st.selectbox("Escolha a Ação:", list(opcoes_cat.keys()))
        id_acao_sel = opcoes_cat[nome_acao_sel]
        acao_obj = BIBLIOTECA_DE_ACOES[id_acao_sel]

        eq_numerica_str = acao_obj.equacao_simbolica
        if acao_obj.reta_funcao is not None:
            a_val, b_val, c_val, _ = acao_obj.reta_funcao(x0, x1, y0, y1)
            eq_numerica_str = f"{a_val:+.2f}·x {b_val:+.2f}·y {c_val:+.2f} = 0"

        st.info(
            f"**Símbolo ($\\sigma \\in \\Sigma$):** `{id_acao_sel}`\n\n"
            f"**Operação:** `{acao_obj.tipo_operacao}` | "
            f"**Axioma:** `{acao_obj.axioma or 'N/A'}` | "
            f"**Vinco:** `{acao_obj.tipo_dobra or 'Neutro'}`\n\n"
            f"**Reta Adaptativa Atual:** `{eq_numerica_str}`\n\n"
            f"_{acao_obj.descricao}_"
        )

        btn_add, btn_rmv = st.columns(2)
        if btn_add.button("➕ Executar Passo", use_container_width=True, type="primary"):
            st.session_state.caminho_em_criacao.append(id_acao_sel)
            st.rerun()

        if btn_rmv.button("↩️ Desfazer Último", use_container_width=True, type="secondary"):
            if len(st.session_state.caminho_em_criacao) > 1:
                st.session_state.caminho_em_criacao.pop()
                st.rerun()
            else:
                st.warning("Não é possível remover o passo inicial.")

        st.markdown("---")
        st.markdown("#### 3. Incorporar Subpalavra (Base Salva)")
        if len(st.session_state.origamis_salvos) > 0:
            nome_inc = st.selectbox(
                "Concatenar passos de um modelo existente:",
                list(st.session_state.origamis_salvos.keys())
            )
            if st.button("Incorporar Passos", use_container_width=True):
                origami_inc = st.session_state.origamis_salvos[nome_inc]
                passos_orig = origami_inc.caminho_de_acoes
                fim_slice = len(passos_orig)
                if passos_orig[-1] == 'ORIGAMI_FINALIZADO':
                    fim_slice -= 1
                st.session_state.caminho_em_criacao.extend(passos_orig[1:fim_slice])
                st.success(f"Subpalavra de '{nome_inc}' concatenada!")
                st.rerun()

        st.markdown("---")
        col_salvar, col_limpar = st.columns(2)
        if col_salvar.button("💾 Salvar Origami", use_container_width=True, type="primary"):
            if nome_novo_origami and len(st.session_state.caminho_em_criacao) > 1:
                novo_origami = Origami(
                    nome_novo_origami,
                    id_acao_inicial=st.session_state.caminho_em_criacao[0]
                )
                for passo in st.session_state.caminho_em_criacao[1:]:
                    novo_origami.adicionar_passo(passo)

                st.session_state.origamis_salvos[nome_novo_origami] = novo_origami
                st.session_state.caminho_em_criacao = ['INICIO']
                st.success(f"Origami '{nome_novo_origami}' salvo na galeria!")
                st.rerun()
            else:
                st.error("Informe um nome e adicione pelo menos um passo.")

        if col_limpar.button("🗑️ Reiniciar Folha", use_container_width=True):
            st.session_state.caminho_em_criacao = ['INICIO']
            st.rerun()

    with col_preview:
        m1, m2, m3 = st.columns(3)
        m1.metric("Passos na Palavra (|w|)", len(st.session_state.caminho_em_criacao))
        m2.metric("Setor / Escopo Ativo", motor_temp.setor_ativo or "Folha Completa")
        m3.metric("Bounding Box Ativa", f"X:[{x0:.2f}, {x1:.2f}] Y:[{y0:.2f}, {y1:.2f}]")

        subcol_malha, subcol_grafo = st.columns([1.15, 1])

        with subcol_malha:
            st.markdown("#### 📐 Bancada Física 2D & Padrão de Vincos")
            fig_temp_papel = motor_temp.renderizar(mostrar_vincos=True)
            if fig_temp_papel is not None:
                st.pyplot(fig_temp_papel)
                plt.close(fig_temp_papel)

        with subcol_grafo:
            st.markdown("#### 📈 Digrafo de Estados em Construção")
            fig_temp_grafo = origami_temp.obter_grafo_visual()
            if fig_temp_grafo is not None:
                st.pyplot(fig_temp_grafo)
                plt.close(fig_temp_grafo)
            else:
                st.info("Execute a primeira ação para gerar a primeira transição do autômato.")

        with st.expander("🔗 Palavra Formal em Construção e Histórico de Passos", expanded=True):
            palavra_str = " ➔ ".join([f"`{p}`" for p in st.session_state.caminho_em_criacao])
            st.markdown(f"**Cadeia Atual ($w$):** {palavra_str}")
            for i, id_acao in enumerate(st.session_state.caminho_em_criacao):
                ac = BIBLIOTECA_DE_ACOES[id_acao]
                st.text(f"Passo {i}: {ac.nome} [{id_acao}] — Axioma: {ac.axioma or 'Controle'}")

# =====================================================================
# MODO 3: ANALISAR ORIGAMIS
# =====================================================================
elif modo == "Analisar Origamis":
    st.header("🔬 Laboratório de Análise (LFA & Teoria dos Grafos)")

    if not st.session_state.origamis_salvos:
        st.warning("Você precisa de pelo menos um origami salvo para fazer uma análise.")
    else:
        tab_singular, tab_comparativa = st.tabs(["Análise Singular", "Análise Comparativa"])

        with tab_singular:
            st.subheader("Análise de um Único Origami")
            nomes_origamis = list(st.session_state.origamis_salvos.keys())
            nome_selecionado = st.selectbox(
                "Escolha um origami para analisar:", nomes_origamis, key="singular_select"
            )
            origami_selecionado = st.session_state.origamis_salvos[nome_selecionado]

            st.markdown("---")
            st.markdown("#### Grau dos Vértices (Ações)")
            acoes_no_grafo = sorted(list(set(origami_selecionado.caminho_de_acoes)))
            nomes_acoes_no_grafo = [
                BIBLIOTECA_DE_ACOES[id_acao].nome for id_acao in acoes_no_grafo
            ]
            acao_para_grau = st.selectbox(
                "Selecione uma ação para ver seu grau:", nomes_acoes_no_grafo
            )

            if st.button("Calcular Grau", use_container_width=True):
                grau_entrada, grau_saida = origami_selecionado.obter_grau_vertice(acao_para_grau)
                if grau_entrada is not None:
                    g_col1, g_col2 = st.columns(2)
                    g_col1.metric("Grau de Entrada (In-Degree)", grau_entrada)
                    g_col2.metric("Grau de Saída (Out-Degree)", grau_saida)
                else:
                    st.error("Ação não encontrada no grafo.")

            st.markdown("---")
            st.markdown("#### Coloração de Vértices")
            if st.button(
                "Aplicar Coloração e Calcular Número Cromático",
                use_container_width=True,
                type="primary"
            ):
                figura_colorida, num_cromatico = origami_selecionado.obter_grafo_colorido()
                if figura_colorida is not None:
                    st.pyplot(figura_colorida)
                    plt.close(figura_colorida)
                    st.metric("Número Cromático", num_cromatico)
                else:
                    st.info("Origami sem passos suficientes para colorir.")

        with tab_comparativa:
            st.subheader("Análise Comparativa entre Dois Origamis")
            if len(st.session_state.origamis_salvos) < 2:
                st.warning("Você precisa de pelo menos dois origamis salvos para esta análise.")
            else:
                nomes_origamis = list(st.session_state.origamis_salvos.keys())
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    origami_principal_nome = st.selectbox(
                        "Selecione o Origami Principal (G):", nomes_origamis, key="principal_comp"
                    )
                with c_col2:
                    origami_padrao_nome = st.selectbox(
                        "Selecione o Origami para Comparar (H):", nomes_origamis, key="padrao_comp"
                    )

                origami_principal = st.session_state.origamis_salvos[origami_principal_nome]
                origami_padrao = st.session_state.origamis_salvos[origami_padrao_nome]

                st.markdown("---")
                st.markdown("##### 🧬 Análise de Linguagens Formais (LFA) - Detalhamento de Padrões")
                
                # Executa os extratores detalhados
                is_pref, trecho_pref = origami_principal.detalhar_prefixo(origami_padrao)
                is_suf, trecho_suf = origami_principal.detalhar_sufixo(origami_padrao)
                ocorrencias_sub, maior_trecho = origami_principal.detalhar_subpalavra(origami_padrao)

                lfa_cols = st.columns(3)
                
                with lfa_cols[0]:
                    st.markdown("**1. Verificação de Prefixo**")
                    if is_pref:
                        st.success(f"✅ É Prefixo (Tamanho: {len(trecho_pref)})")
                        with st.expander("Ver Trecho Coincidente"):
                            st.code("\n↓\n".join(trecho_pref))
                    else:
                        st.error("❌ Não é Prefixo Integral")
                        if trecho_pref:
                            st.caption(f"Maior coincidência no início (Tamanho: {len(trecho_pref)}):")
                            with st.expander("Ver Trecho Parcial"):
                                st.code("\n↓\n".join(trecho_pref))
                        else:
                            st.caption("Nenhuma ação inicial em comum.")

                with lfa_cols[1]:
                    st.markdown("**2. Verificação de Subpalavra**")
                    if ocorrencias_sub:
                        st.success(f"✅ É Subpalavra ({len(ocorrencias_sub)} ocorrência(s))")
                        for idx, (ini, fim, trecho) in enumerate(ocorrencias_sub):
                            with st.expander(f"Ocorrência {idx+1} (Passos {ini} a {fim})"):
                                st.code("\n↓\n".join(trecho))
                    else:
                        st.error("❌ Não é Subpalavra Integral")
                        if maior_trecho:
                            st.caption(f"Maior Substring Contígua Comum (LCS: {len(maior_trecho)} passos):")
                            with st.expander("Ver Maior Trecho em Comum"):
                                st.code("\n↓\n".join(maior_trecho))
                        else:
                            st.caption("Nenhuma ação em comum encontrada.")

                with lfa_cols[2]:
                    st.markdown("**3. Verificação de Sufixo**")
                    if is_suf:
                        st.success(f"✅ É Sufixo (Tamanho: {len(trecho_suf)})")
                        with st.expander("Ver Trecho Coincidente"):
                            st.code("\n↓\n".join(trecho_suf))
                    else:
                        st.error("❌ Não é Sufixo Integral")
                        if trecho_suf:
                            st.caption(f"Maior coincidência no final (Tamanho: {len(trecho_suf)}):")
                            with st.expander("Ver Trecho Parcial"):
                                st.code("\n↓\n".join(trecho_suf))
                        else:
                            st.caption("Nenhuma ação final em comum.")

                st.markdown("---")
                st.markdown("##### 🕸️ Análise Estrutural de Grafos")
                grafo_cols = st.columns(2)
                if grafo_cols[0].button("É Subgrafo Induzido?", use_container_width=True):
                    st.metric(
                        "Resultado:", str(origami_principal.is_subgrafo_induzido(origami_padrao))
                    )
                if grafo_cols[1].button("É Subgrafo Gerador?", use_container_width=True):
                    st.metric(
                        "Resultado:", str(origami_principal.is_subgrafo_gerador(origami_padrao))
                    )