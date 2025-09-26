# classes_origami.py

import networkx as nx
import matplotlib.pyplot as plt
from biblioteca_acoes import BIBLIOTECA_DE_ACOES, Acao 

class Origami:
    def __init__(self, nome, id_acao_inicial='INICIO'):
        self.nome = nome
        if id_acao_inicial not in BIBLIOTECA_DE_ACOES:
            raise ValueError(f"Ação inicial '{id_acao_inicial}' não existe na biblioteca.")
        self.caminho_de_acoes = [id_acao_inicial]

    def adicionar_passo(self, id_acao):
        if id_acao not in BIBLIOTECA_DE_ACOES:
            raise ValueError(f"Ação '{id_acao}' não existe na biblioteca.")
        self.caminho_de_acoes.append(id_acao)
        return self

    def obter_instrucoes(self):
        instrucoes = []
        instrucoes.append("="*40)
        instrucoes.append(f"Instruções para o Origami: {self.nome}")
        instrucoes.append("="*40)
        for i, id_acao in enumerate(self.caminho_de_acoes):
            acao = BIBLIOTECA_DE_ACOES[id_acao] 
            instrucoes.append(f"Passo {i}: {acao.nome}")
            instrucoes.append(f"   -> {acao.descricao}")
        instrucoes.append("="*40)
        return "\n".join(instrucoes)

    def _gerar_grafo(self, com_passos=True):
        node_labels = {id_acao: BIBLIOTECA_DE_ACOES[id_acao].nome for id_acao in set(self.caminho_de_acoes)}
        
        if com_passos:
            g = nx.MultiDiGraph()
            g.add_nodes_from(node_labels.values())
            for i in range(len(self.caminho_de_acoes) - 1):
                nome_origem = node_labels[self.caminho_de_acoes[i]]
                nome_destino = node_labels[self.caminho_de_acoes[i+1]]
                g.add_edge(nome_origem, nome_destino, passo=i + 1)
        else:
            g = nx.DiGraph()
            g.add_nodes_from(node_labels.values())
            for i in range(len(self.caminho_de_acoes) - 1):
                nome_origem = node_labels[self.caminho_de_acoes[i]]
                nome_destino = node_labels[self.caminho_de_acoes[i+1]]
                g.add_edge(nome_origem, nome_destino)
        return g

    def obter_grafo_visual(self):
        if len(self.caminho_de_acoes) < 2:
            return None

        g = self._gerar_grafo(com_passos=True)
        
        fig, ax = plt.subplots(figsize=(18, 14))
        pos = nx.spring_layout(g, seed=42, k=2.5, iterations=50)

        nx.draw(g, pos, ax=ax, with_labels=False, node_size=3000, node_color='skyblue',
                edge_color="gray", width=2.0, arrowstyle="-|>",
                arrowsize=25, connectionstyle='arc3,rad=0.15')
        
        nx.draw_networkx_labels(g, pos, ax=ax, font_size=10, font_weight='bold')
        
        labels_arestas = nx.get_edge_attributes(g, 'passo')
        nx.draw_networkx_edge_labels(g, pos, ax=ax, edge_labels=labels_arestas, font_color='red',
                                     font_size=11, font_weight='bold',
                                     bbox=dict(facecolor='gray', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'),
                                     label_pos=0.15)
        
        ax.set_title(f"Grafo de Ações para: {self.nome}", size=20)
        return fig
   
   # --- Métodos de Teoria dos Grafos ---

    def is_subgrafo(self, outro_origami): #Verifica se o outro_origami é um subgrafo do origami atual.
        caminho_maior_str = " ".join(self.caminho_de_acoes)
        caminho_menor_str = " ".join(outro_origami.caminho_de_acoes)

        return caminho_menor_str in caminho_maior_str

    def is_subgrafo_induzido(self, outro_origami): #Verifica se o outro_origami é um subgrafo induzido do origami atual.(Se tem a mesmas conexões/arestas para os vértices existentes)

        G = self._gerar_grafo(com_passos=False)
        H = outro_origami._gerar_grafo(com_passos=False)

        if not set(H.nodes()).issubset(set(G.nodes())): #Já verifica se os nós de H existem em G
            return False

        G_induzido = G.subgraph(H.nodes()) #Cria um G_induzido com base em H

        return set(G_induzido.edges()) == set(H.edges()) #Compara se o conjunto de arestas do subgrafo induzido é igual ao de H

    # --- Métodos de LFA ---

    def is_prefixo(self, outro_origami):
        """
        Verifica se a palavra de 'outro_origami' é um prefixo da palavra deste origami.
        Em LFA: dado w = self e p = outro, verifica se w = p x para alguma palavra x.
        """
        palavra_maior = self.caminho_de_acoes
        palavra_menor = outro_origami.caminho_de_acoes

        if len(palavra_menor) > len(palavra_maior): #A palavra menor NÃO pode ser maior que a palavra menor
            return False

        return palavra_maior[:len(palavra_menor)] == palavra_menor #Os primeiros caracteres, do tamanho da palavra menor, da palavra maior tem que que ser igual a palavra menor

    def is_sufixo(self, outro_origami):
        """
        Verifica se a palavra de 'outro_origami' é um sufixo da palavra deste origami.
        Em LFA: dado w = self e s = outro, verifica se w = x s para alguma palavra x.
        """
        palavra_maior = self.caminho_de_acoes
        palavra_menor = outro_origami.caminho_de_acoes

        if len(palavra_menor) > len(palavra_maior): #A palavra menor NÃO pode ser maior que a palavra menor
            return False

        return palavra_maior[-len(palavra_menor):] == palavra_menor #Os últimos caracteres, do tamanho da palavra menor, da palavra maior tem que que ser igual a palavra menor

    def is_subpalavra(self, outro_origami):
        """
        Verifica se a palavra de 'outro_origami' é uma subpalavra (substring) da palavra deste origami.
        Em LFA: dado w = self e u = outro, verifica se w = x u y para algumas palavras x, y.
        """

        palavra_maior_str = " ".join(self.caminho_de_acoes)
        palavra_menor_str = " ".join(outro_origami.caminho_de_acoes)

        return palavra_menor_str in palavra_maior_str

