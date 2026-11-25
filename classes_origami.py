"""
classes_origami.py

Modela sequências de instruções de origami como palavras de uma Linguagem Formal
e digrafos de transição no NetworkX, integrando a simulação geométrica matricial
via MotorGraficoPapel.
"""

from typing import Optional, Tuple
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from biblioteca_acoes import BIBLIOTECA_DE_ACOES
from motor_grafico import MotorGraficoPapel


class Origami:
    """
    Representa um modelo de origami através de sua palavra de ações (LFA),
    seu digrafo de estados/transições (NetworkX) e sua malha geométrica 2D.
    """

    def __init__(self, nome: str, id_acao_inicial: str = 'INICIO') -> None:
        self.nome = nome
        if id_acao_inicial not in BIBLIOTECA_DE_ACOES:
            raise ValueError(f"Ação inicial '{id_acao_inicial}' não existe na biblioteca.")
        self.caminho_de_acoes = [id_acao_inicial]
        self.motor_grafico = MotorGraficoPapel(altura=50, largura=50)

    def adicionar_passo(self, id_acao: str) -> "Origami":
        """Concatena um novo símbolo à palavra formal do origami."""
        if id_acao not in BIBLIOTECA_DE_ACOES:
            raise ValueError(f"Ação '{id_acao}' não existe na biblioteca.")
        self.caminho_de_acoes.append(id_acao)
        return self

    def simular_geometria_papel(self, ate_passo: Optional[int] = None) -> MotorGraficoPapel:
        if not hasattr(self, 'motor_grafico') or self.motor_grafico is None:
            self.motor_grafico = MotorGraficoPapel(altura=51, largura=51)

        self.motor_grafico.resetar()
        limite = len(self.caminho_de_acoes) if ate_passo is None else min(
            ate_passo + 1, len(self.caminho_de_acoes)
        )

        for id_acao in self.caminho_de_acoes[:limite]:
            self.motor_grafico.aplicar_acao(id_acao)

        return self.motor_grafico

    def obter_imagem_papel(
        self,
        ate_passo: Optional[int] = None,
        mostrar_vincos: bool = True
    ) -> Figure:
        """
        Executa a simulação geométrica e retorna garantidamente um objeto Figure.
        """
        self.simular_geometria_papel(ate_passo=ate_passo)
        fig = self.motor_grafico.renderizar(mostrar_vincos=mostrar_vincos)
        if fig is None:
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.text(0.5, 0.5, "Erro ao renderizar malha", ha="center", va="center")
        return fig

    def obter_instrucoes(self) -> str:
        """Gera a listagem textual formatada das instruções passo a passo."""
        instrucoes = [
            "=" * 40,
            f"Instruções para o Origami: {self.nome}",
            "=" * 40
        ]
        for i, id_acao in enumerate(self.caminho_de_acoes):
            acao = BIBLIOTECA_DE_ACOES[id_acao]
            instrucoes.append(f"Passo {i}: {acao.nome}")
            instrucoes.append(f"  -> {acao.descricao}")
        instrucoes.append("=" * 40)
        return "\n".join(instrucoes)

    def _gerar_grafo(self, com_passos: bool = True) -> nx.Graph:
        """Constrói o grafo direcionado de ações (MultiDiGraph ou DiGraph)."""
        node_labels = {
            id_acao: BIBLIOTECA_DE_ACOES[id_acao].nome
            for id_acao in set(self.caminho_de_acoes)
        }

        if com_passos:
            g = nx.MultiDiGraph()
            g.add_nodes_from(node_labels.values())
            for i in range(len(self.caminho_de_acoes) - 1):
                nome_origem = node_labels[self.caminho_de_acoes[i]]
                nome_destino = node_labels[self.caminho_de_acoes[i + 1]]
                g.add_edge(nome_origem, nome_destino, passo=i + 1)
        else:
            g = nx.DiGraph()
            g.add_nodes_from(node_labels.values())
            for i in range(len(self.caminho_de_acoes) - 1):
                nome_origem = node_labels[self.caminho_de_acoes[i]]
                nome_destino = node_labels[self.caminho_de_acoes[i + 1]]
                g.add_edge(nome_origem, nome_destino)
        return g

    def obter_grafo_visual(self) -> Optional[Figure]:
        """Renderiza o digrafo de transições de ações usando Matplotlib."""
        if len(self.caminho_de_acoes) < 2:
            return None

        g = self._gerar_grafo(com_passos=True)
        fig, ax = plt.subplots(figsize=(12, 9))
        pos = nx.spring_layout(g, seed=42, k=2.5, iterations=50)

        nx.draw(
            g, pos, ax=ax, with_labels=False, node_size=2600,
            node_color='skyblue', edge_color='gray', width=2.0,
            arrowstyle='-|>', arrowsize=22, connectionstyle='arc3,rad=0.15'
        )
        nx.draw_networkx_labels(g, pos, ax=ax, font_size=9, font_weight='bold')

        labels_arestas = nx.get_edge_attributes(g, 'passo')
        nx.draw_networkx_edge_labels(
            g, pos, ax=ax, edge_labels=labels_arestas,
            font_color='red', font_size=10, font_weight='bold',
            bbox=dict(facecolor='gray', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'),
            label_pos=0.15
        )

        ax.set_title(f"Grafo de Ações para: {self.nome}", size=15)
        fig.tight_layout()
        return fig

    def obter_grau_vertice(self, nome_da_acao: str) -> Tuple[Optional[int], Optional[int]]:
        """Calcula o grau de entrada (in-degree) e saída (out-degree) de um vértice."""
        g = self._gerar_grafo(com_passos=False)
        if nome_da_acao not in g.nodes():
            return None, None
        return g.in_degree(nome_da_acao), g.out_degree(nome_da_acao)

    # --- Métodos de Teoria dos Grafos ---

    def is_subgrafo(self, outro_origami: "Origami") -> bool:
        caminho_maior_str = " ".join(self.caminho_de_acoes)
        caminho_menor_str = " ".join(outro_origami.caminho_de_acoes)
        return caminho_menor_str in caminho_maior_str

    def is_subgrafo_induzido(self, outro_origami: "Origami") -> bool:
        g_maior = self._gerar_grafo(com_passos=False)
        h_menor = outro_origami._gerar_grafo(com_passos=False)

        if not set(h_menor.nodes()).issubset(set(g_maior.nodes())):
            return False

        g_induzido = g_maior.subgraph(h_menor.nodes())
        return set(g_induzido.edges()) == set(h_menor.edges())

    def is_subgrafo_gerador(self, outro_origami: "Origami") -> bool:
        g_maior = self._gerar_grafo(com_passos=False)
        h_menor = outro_origami._gerar_grafo(com_passos=False)

        if set(g_maior.nodes()) != set(h_menor.nodes()):
            return False
        return set(h_menor.edges()).issubset(set(g_maior.edges()))

    def obter_grafo_colorido(self) -> Tuple[Optional[Figure], Optional[int]]:
        if len(self.caminho_de_acoes) < 2:
            return None, None

        g_nao_direcionado = self._gerar_grafo(com_passos=False).to_undirected()
        coloring = nx.greedy_color(g_nao_direcionado)
        numero_cromatico = max(coloring.values()) + 1
        node_colors = [coloring[node] for node in g_nao_direcionado.nodes()]

        g_direcionado = self._gerar_grafo(com_passos=True)
        fig, ax = plt.subplots(figsize=(12, 9))
        pos = nx.spring_layout(g_direcionado, seed=42, k=2.5, iterations=50)

        nx.draw(
            g_direcionado, pos, ax=ax, with_labels=False,
            node_color=node_colors, cmap=plt.cm.viridis, node_size=2600,
            edge_color='gray', width=2.0, arrowstyle='-|>',
            arrowsize=22, connectionstyle='arc3,rad=0.15'
        )
        nx.draw_networkx_labels(g_direcionado, pos, ax=ax, font_size=9, font_weight='bold')

        labels_arestas = nx.get_edge_attributes(g_direcionado, 'passo')
        nx.draw_networkx_edge_labels(
            g_direcionado, pos, ax=ax, edge_labels=labels_arestas,
            font_color='red', font_size=10, font_weight='bold',
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'),
            label_pos=0.3
        )

        ax.set_title(
            f"Grafo Colorido: {self.nome} (Número Cromático: {numero_cromatico})",
            size=15
        )
        fig.tight_layout()
        return fig, numero_cromatico

    # --- Métodos de Linguagens Formais e Autômatos (LFA) ---

    # --- Métodos de Linguagens Formais e Autômatos (LFA) ---

    def detalhar_prefixo(self, outro_origami: "Origami") -> Tuple[bool, List[str]]:
        """
        Retorna se a palavra 'H' é prefixo de 'G' e o maior trecho coincidente no início.
        """
        palavra_maior = self.caminho_de_acoes
        palavra_menor = outro_origami.caminho_de_acoes
        trecho_comum = []
        
        for i in range(min(len(palavra_maior), len(palavra_menor))):
            if palavra_maior[i] == palavra_menor[i]:
                trecho_comum.append(palavra_maior[i])
            else:
                break
                
        is_pref = (len(trecho_comum) == len(palavra_menor) and len(palavra_menor) > 0)
        return is_pref, trecho_comum

    def detalhar_sufixo(self, outro_origami: "Origami") -> Tuple[bool, List[str]]:
        """
        Retorna se a palavra 'H' é sufixo de 'G' e o maior trecho coincidente no final.
        """
        palavra_maior = self.caminho_de_acoes
        palavra_menor = outro_origami.caminho_de_acoes
        trecho_comum = []
        
        for i in range(1, min(len(palavra_maior), len(palavra_menor)) + 1):
            if palavra_maior[-i] == palavra_menor[-i]:
                trecho_comum.insert(0, palavra_maior[-i])
            else:
                break
                
        is_suf = (len(trecho_comum) == len(palavra_menor) and len(palavra_menor) > 0)
        return is_suf, trecho_comum

    def detalhar_subpalavra(self, outro_origami: "Origami") -> Tuple[List[Tuple[int, int, List[str]]], List[str]]:
        """
        Busca ocorrências exatas da subpalavra e aplica Programação Dinâmica (LCS)
        para encontrar a Maior Substring Comum Contígua caso não seja uma subpalavra integral.
        Retorna: (Lista de Ocorrências [inicio, fim, trecho], Maior Trecho em Comum)
        """
        w1 = self.caminho_de_acoes
        w2 = outro_origami.caminho_de_acoes
        ocorrencias = []
        len2 = len(w2)
        
        # 1. Algoritmo de Busca de Padrão Exato
        if 0 < len2 <= len(w1):
            for i in range(len(w1) - len2 + 1):
                if w1[i:i+len2] == w2:
                    ocorrencias.append((i, i + len2 - 1, w2))
                    
        # 2. Algoritmo de Programação Dinâmica (Longest Common Substring - LCS)
        max_len = 0
        end_idx = 0
        dp = [[0] * (len(w2) + 1) for _ in range(len(w1) + 1)]
        
        for i in range(1, len(w1) + 1):
            for j in range(1, len(w2) + 1):
                if w1[i-1] == w2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    if dp[i][j] > max_len:
                        max_len = dp[i][j]
                        end_idx = i
                else:
                    dp[i][j] = 0
                    
        maior_trecho_comum = w1[end_idx - max_len : end_idx] if max_len > 0 else []
        
        return ocorrencias, maior_trecho_comum

        palavra_maior_str = " ".join(self.caminho_de_acoes)
        palavra_menor_str = " ".join(outro_origami.caminho_de_acoes)
        return palavra_menor_str in palavra_maior_str