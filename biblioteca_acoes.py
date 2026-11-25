"""
biblioteca_acoes.py

Biblioteca formal e declarativa de ações de origami para o framework OriGraphs.
Cada ação encapsula axiomas de Huzita-Justin-Hatori, equações de reta adaptativas,
especificação de semiplano ativo, camadas incidentes e sentido da dobra (vale/pico).
"""

from typing import Callable, Dict, Optional, Tuple


class Acao:
    """
    Representa formalmente uma operação primitiva de origami.
    """

    def __init__(
        self,
        nome: str,
        descricao: str,
        tipo_operacao: str = "DOBRA",
        axioma: Optional[str] = None,
        tipo_dobra: Optional[str] = None,
        camadas: str = "TODAS",
        equacao_simbolica: str = "N/A",
        reta_funcao: Optional[
            Callable[[float, float, float, float], Tuple[float, float, float, int]]
        ] = None,
        parametro_adicional: Optional[float] = None
    ) -> None:
        self.nome = nome
        self.descricao = descricao
        self.tipo_operacao = tipo_operacao
        self.axioma = axioma
        self.tipo_dobra = tipo_dobra
        self.camadas = camadas
        self.equacao_simbolica = equacao_simbolica
        self.reta_funcao = reta_funcao
        self.parametro_adicional = parametro_adicional

    def __repr__(self) -> str:
        return f"Acao('{self.nome}', tipo='{self.tipo_operacao}', axioma='{self.axioma}')"


BIBLIOTECA_DE_ACOES: Dict[str, Acao] = {
    # 0. Controle
    'INICIO': Acao(
        nome="Início: Papel Quadrado",
        descricao="Comece com uma folha de papel quadrada plana sobre a mesa no espaço UV [0, 1]².",
        tipo_operacao="CONTROLE",
        equacao_simbolica="Domínio UV ∈ [0, 1] × [0, 1]"
    ),
    'ORIGAMI_FINALIZADO': Acao(
        nome="Origami Finalizado",
        descricao="O modelo está completo.",
        tipo_operacao="CONTROLE",
        equacao_simbolica="Estado de Aceitação (q_f)"
    ),

    # 1. Dobras ao Meio (Axioma A2: Mediatriz Ortogonal)
    'DOBRAR_MEIO_D_E': Acao(
        nome="Dobra ao Meio (D->E)",
        descricao="Leve a borda da direita e dobre-a sobre a borda da esquerda.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="1.0·x + 0.0·y - x_médio = 0 (x > x_médio)",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, 0.0, -0.5 * (x0 + x1), +1)
    ),
    'DOBRAR_MEIO_E_D': Acao(
        nome="Dobra ao Meio (E->D)",
        descricao="Leve a borda da esquerda e dobre-a sobre a borda da direita.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="-1.0·x + 0.0·y + x_médio = 0 (x < x_médio)",
        reta_funcao=lambda x0, x1, y0, y1: (-1.0, 0.0, 0.5 * (x0 + x1), +1)
    ),
    'DOBRAR_MEIO_B_T': Acao(
        nome="Dobra ao Meio (B->T)",
        descricao="Leve a borda de baixo e dobre-a sobre a borda do topo.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="0.0·x - 1.0·y + y_médio = 0 (y < y_médio)",
        reta_funcao=lambda x0, x1, y0, y1: (0.0, -1.0, 0.5 * (y0 + y1), +1)
    ),
    'DOBRAR_MEIO_T_B': Acao(
        nome="Dobra ao Meio (T->B)",
        descricao="Leve a borda do topo e dobre-a sobre a borda de baixo.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="0.0·x + 1.0·y - y_médio = 0 (y > y_médio)",
        reta_funcao=lambda x0, x1, y0, y1: (0.0, 1.0, -0.5 * (y0 + y1), +1)
    ),

    # 2. Dobras na Diagonal (Axioma A1/A2: Inclinação exata de 45° no centro da região ativa)
    'DOBRAR_DIAG_BE_TD': Acao(
        nome="Dobra na Diagonal (BE->TD)",
        descricao="Leve o canto inferior esquerdo (BE) até o canto superior direito (TD).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="-x - y + (x_m + y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (-1.0, -1.0, 0.5 * (x0 + x1) + 0.5 * (y0 + y1), +1)
    ),
    'DOBRAR_DIAG_TD_BE': Acao(
        nome="Dobra na Diagonal (TD->BE)",
        descricao="Leve o canto superior direito (TD) até o canto inferior esquerdo (BE).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="x + y - (x_m + y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, 1.0, -(0.5 * (x0 + x1) + 0.5 * (y0 + y1)), +1)
    ),
    'DOBRAR_DIAG_BD_TE': Acao(
        nome="Dobra na Diagonal (BD->TE)",
        descricao="Leve o canto inferior direito (BD) até o canto superior esquerdo (TE).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="x - y + (y_m - x_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, -1.0, 0.5 * (y0 + y1) - 0.5 * (x0 + x1), +1)
    ),
    'DOBRAR_DIAG_TE_BD': Acao(
        nome="Dobra na Diagonal (TE->BD)",
        descricao="Leve o canto superior esquerdo (TE) até o canto inferior direito (BD).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="-x + y + (x_m - y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (-1.0, 1.0, 0.5 * (x0 + x1) - 0.5 * (y0 + y1), +1)
    ),

    # 3. Dobras Canto ao Centro (Axioma A2: Bissetriz a 45°)
    'DOBRAR_CANTO_TD_C': Acao(
        nome="Dobra Canto ao Centro (TD->C)",
        descricao="Leve o canto superior direito (TD) até o ponto central (C) do papel.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="x + y - (x_m + y_max) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, 1.0, -(0.5 * (x0 + x1) + y1), +1)
    ),
    'DOBRAR_CANTO_TE_C': Acao(
        nome="Dobra Canto ao Centro (TE->C)",
        descricao="Leve o canto superior esquerdo (TE) até o ponto central (C) do papel.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="-x + y + (x_m - y_max) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (-1.0, 1.0, 0.5 * (x0 + x1) - y1, +1)
    ),
    'DOBRAR_CANTO_BD_C': Acao(
        nome="Dobra Canto ao Centro (BD->C)",
        descricao="Leve o canto inferior direito (BD) até o ponto central (C) do papel.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="x - y + (y_min - x_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, -1.0, y0 - 0.5 * (x0 + x1), +1)
    ),
    'DOBRAR_CANTO_BE_C': Acao(
        nome="Dobra Canto ao Centro (BE->C)",
        descricao="Leve o canto inferior esquerdo (BE) até o ponto central (C) do papel.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="-x - y + (x_m + y_min) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (-1.0, -1.0, 0.5 * (x0 + x1) + y0, +1)
    ),

    # 4. Dobras Inclinadas Vale e Pico
    'DOBRA_VALE_TD_BC': Acao(
        nome="Dobra Vale (TD->BC)",
        descricao="Dobre o canto superior direito (TD) em direção à parte baixa central (BC).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="0.5·x + 1.0·y - (0.5·x_max + y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (
            0.5 * (x1 - x0),
            y1 - y0,
            -(0.5 * (x1 - x0) * (0.25 * x0 + 0.75 * x1) + (y1 - y0) * (0.5 * y0 + 0.5 * y1)),
            +1
        )
    ),
    'DOBRA_VALE_TE_BC': Acao(
        nome="Dobra Vale (TE->BC)",
        descricao="Dobre o canto superior esquerdo (TE) em direção à parte baixa central (BC).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="-0.5·x + 1.0·y + (0.5·x_min - y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (
            -0.5 * (x1 - x0),
            y1 - y0,
            -(-0.5 * (x1 - x0) * (0.75 * x0 + 0.25 * x1) + (y1 - y0) * (0.5 * y0 + 0.5 * y1)),
            +1
        )
    ),
    'DOBRA_PICO_BD_TC': Acao(
        nome="Dobra Pico (BD->TC)",
        descricao="Dobre o canto inferior direito (BD) por trás em direção ao centro superior (TC).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="PICO",
        equacao_simbolica="0.5·x - 1.0·y + (y_m - 0.5·x_max) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (
            0.5 * (x1 - x0),
            y0 - y1,
            -(0.5 * (x1 - x0) * (0.25 * x0 + 0.75 * x1) + (y0 - y1) * (0.5 * y0 + 0.5 * y1)),
            +1
        )
    ),
    'DOBRA_PICO_BE_TC': Acao(
        nome="Dobra Pico (BE->TC)",
        descricao="Dobre o canto inferior esquerdo (BE) por trás em direção ao centro superior (TC).",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="PICO",
        equacao_simbolica="-0.5·x - 1.0·y + (y_m + 0.5·x_min) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (
            -0.5 * (x1 - x0),
            y0 - y1,
            -(-0.5 * (x1 - x0) * (0.75 * x0 + 0.25 * x1) + (y0 - y1) * (0.5 * y0 + 0.5 * y1)),
            +1
        )
    ),

    # 5. Manipulações Espaciais Globais
    'DESDOBRAR_PASSO_ANTERIOR': Acao(
        nome="Desdobrar Passo Anterior",
        descricao="Desfaça a última dobra mantendo o vinco registrado no espaço UV.",
        tipo_operacao="DESDOBRAR",
        equacao_simbolica="P_atual ← P_pilha[-1] (Mantém Vinco UV)",
        parametro_adicional=0.0
    ),
    'DESDOBRAR_PARCIALMENTE': Acao(
        nome="Desdobrar Parcialmente",
        descricao="Abre parcialmente a última aba dobrada em projeção 2.5D (ex: asas de avião).",
        tipo_operacao="DESDOBRAR",
        equacao_simbolica="Projeção 2.5D de aba aberta (Asa)",
        parametro_adicional=0.65
    ),
    'ROTACIONAR_90_D': Acao(
        nome="Rotacionar 90° (D)",
        descricao="Gire o papel 90 graus para a direita (sentido horário).",
        tipo_operacao="ROTACAO",
        equacao_simbolica="R(-90°) em torno do centro atual",
        parametro_adicional=-90.0
    ),
    'ROTACIONAR_90_E': Acao(
        nome="Rotacionar 90° (E)",
        descricao="Gire o papel 90 graus para a esquerda (sentido anti-horário).",
        tipo_operacao="ROTACAO",
        equacao_simbolica="R(+90°) em torno do centro atual",
        parametro_adicional=90.0
    ),
    'ROTACIONAR_45_D': Acao(
        nome="Rotacionar 45° (D)",
        descricao="Gire o papel 45 graus para a direita (sentido horário).",
        tipo_operacao="ROTACAO",
        equacao_simbolica="R(-45°) em torno do centro atual",
        parametro_adicional=-45.0
    ),
    'ROTACIONAR_45_E': Acao(
        nome="Rotacionar 45° (E)",
        descricao="Gire o papel 45 graus para a esquerda (sentido anti-horário).",
        tipo_operacao="ROTACAO",
        equacao_simbolica="R(+45°) em torno do centro atual",
        parametro_adicional=45.0
    ),
    'ROTACIONAR_180': Acao(
        nome="Rotacionar 180°",
        descricao="Gire o papel 180 graus.",
        tipo_operacao="ROTACAO",
        equacao_simbolica="R(180°) em torno do centro atual",
        parametro_adicional=180.0
    ),
    'VIRAR_PAPEL': Acao(
        nome="Virar",
        descricao="Vire o papel horizontalmente, invertendo a ordem Z das camadas e as faces.",
        tipo_operacao="VIRAR",
        equacao_simbolica="x ← 2·x_c - x,  Z ← -Z,  Face ← -Face"
    ),
    'ABRIR_ABA': Acao(
        nome="Abrir Aba",
        descricao="Levante a aba ou camada superior para revelar o que está embaixo.",
        tipo_operacao="DESDOBRAR",
        equacao_simbolica="Abertura parcial de aba superior",
        parametro_adicional=0.5
    ),
    'ESCONDER_ABA_DENTRO': Acao(
        nome="Esconder Aba",
        descricao="Dobre e esconda uma aba ou ponta dentro de um bolso de papel.",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="PICO",
        equacao_simbolica="Inversão de camada para o interior (-Z)",
        reta_funcao=lambda x0, x1, y0, y1: (0.0, 1.0, -(y0 + 0.75 * (y1 - y0)), +1)
    ),

    # 6. Manipulações de Setores
    'ENTRAR_SETOR_D': Acao(
        nome="Entrar no Setor (D)",
        descricao="Manipule somente o papel no setor da direita.",
        tipo_operacao="SETOR",
        camadas="D",
        equacao_simbolica="Filtro Espacial: x ≥ x_eixo_simetria"
    ),
    'ENTRAR_SETOR_E': Acao(
        nome="Entrar no Setor (E)",
        descricao="Manipule somente o papel no setor da esquerda.",
        tipo_operacao="SETOR",
        camadas="E",
        equacao_simbolica="Filtro Espacial: x ≤ x_eixo_simetria"
    ),
    'ENTRAR_SETOR_T': Acao(
        nome="Entrar no Setor (T)",
        descricao="Manipule somente o papel no setor do topo.",
        tipo_operacao="SETOR",
        camadas="T",
        equacao_simbolica="Filtro Espacial: y ≥ y_eixo_simetria"
    ),
    'ENTRAR_SETOR_B': Acao(
        nome="Entrar no Setor (B)",
        descricao="Manipule somente o papel no setor de baixo.",
        tipo_operacao="SETOR",
        camadas="B",
        equacao_simbolica="Filtro Espacial: y ≤ y_eixo_simetria"
    ),
    'ENTRAR_SETOR_S': Acao(
        nome="Entrar no Setor (S)",
        descricao="Manipule somente a aba da superfície superior (camadas frontais da pilha Z).",
        tipo_operacao="SETOR",
        camadas="S",
        equacao_simbolica="Filtro Topológico: Aba Superior (Z > Z_médio)"
    ),
    'ENTRAR_SETOR_I': Acao(
        nome="Entrar no Setor (I)",
        descricao="Manipule somente o setor interno/inferior da pilha Z.",
        tipo_operacao="SETOR",
        camadas="I",
        equacao_simbolica="Filtro Topológico: Aba Inferior (Z < Z_médio)"
    ),
    'SAIR_SETOR_ANTERIOR': Acao(
        nome="Sair do Setor Anterior",
        descricao="Saia do setor atual e volte a manipular o modelo inteiro.",
        tipo_operacao="SETOR",
        camadas="TODAS",
        equacao_simbolica="Filtro Ativo ← Todos os Vértices"
    ),

    # 7. Dobras Compostas e Modelagem
    'COLAPSAR_LATERAIS': Acao(
        nome="Colapsar as Laterais",
        descricao="Colapsa as laterais formando a Base Bomba d'Água (triângulo isósceles de 4 abas).",
        tipo_operacao="COMPOSTA",
        axioma="A1+A2",
        tipo_dobra="VALE",
        equacao_simbolica="Colapso Kawasaki/Maekawa (|M - V| = 2)"
    ),
    'DOBRA_ESMAGADA': Acao(
        nome="Dobra Esmagada",
        descricao="Abra uma aba e achate-a simetricamente formando um losango.",
        tipo_operacao="DOBRA",
        axioma="A3",
        tipo_dobra="VALE",
        equacao_simbolica="x + 0.5·y - (x_m + 0.5·y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, 0.5, -(0.5 * (x0 + x1) + 0.25 * (y0 + y1)), +1)
    ),
    'DOBRA_PETALA': Acao(
        nome="Dobra Pétala",
        descricao="Levante uma ponta enquanto afina as laterais da base.",
        tipo_operacao="DOBRA",
        axioma="A3",
        tipo_dobra="VALE",
        equacao_simbolica="x + 0.5·y - (x_m + 0.5·y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, 0.5, -(0.5 * (x0 + x1) + 0.25 * (y0 + y1)), +1)
    ),
    'DOBRA_REVERSA_INTERNA': Acao(
        nome="Dobra Reversa Interna",
        descricao="Empurre uma ponta para dentro do modelo, entre as camadas de papel.",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="PICO",
        equacao_simbolica="0.8·x + y - (0.8·x_m + y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (0.8, 1.0, -(0.8 * 0.5 * (x0 + x1) + 0.5 * (y0 + y1)), +1)
    ),
    'DOBRA_REVERSA_EXTERNA': Acao(
        nome="Dobra Reversa Externa",
        descricao="Dobre uma ponta para fora envolvendo as camadas existentes.",
        tipo_operacao="DOBRA",
        axioma="A1",
        tipo_dobra="VALE",
        equacao_simbolica="0.8·x + y - (0.8·x_m + y_m) = 0",
        reta_funcao=lambda x0, x1, y0, y1: (0.8, 1.0, -(0.8 * 0.5 * (x0 + x1) + 0.5 * (y0 + y1)), +1)
    ),
    'ORELHA_DE_COELHO': Acao(
        nome="Dobra Orelha de Coelho",
        descricao="Achate um canto do papel criando uma ponta mais fina.",
        tipo_operacao="DOBRA",
        axioma="A3",
        tipo_dobra="VALE",
        equacao_simbolica="Bissetriz concorrente de canto",
        reta_funcao=lambda x0, x1, y0, y1: (1.0, 0.5, -(0.5 * (x0 + x1) + 0.25 * (y0 + y1)), +1)
    ),
    'AFUNDAR_PONTA': Acao(
        nome="Afundar Ponta",
        descricao="Achate um vértice empurrando-o para o interior da pilha.",
        tipo_operacao="DOBRA",
        axioma="A4",
        tipo_dobra="PICO",
        equacao_simbolica="Projeção ortogonal de vértice",
        reta_funcao=lambda x0, x1, y0, y1: (0.0, 1.0, -(y0 + 0.8 * (y1 - y0)), +1)
    ),
    'VINCO_PREGAS': Acao(
        nome="Vinco de Pregas",
        descricao="Série de dobras vale e montanha alternadas.",
        tipo_operacao="DOBRA",
        axioma="A2",
        tipo_dobra="VALE",
        equacao_simbolica="Prega paralela periódica",
        reta_funcao=lambda x0, x1, y0, y1: (0.0, 1.0, -(y0 + 0.6 * (y1 - y0)), +1)
    ),
    'INFLAR_MODELO': Acao(
        nome="Inflar Modelo",
        descricao="Expansão volumétrica do modelo.",
        tipo_operacao="CONTROLE",
        equacao_simbolica="Transformação Identidade 2D"
    ),
    'ARREDONDAR_CURVAR': Acao(
        nome="Modelar/Curvar",
        descricao="Acabamento estético sem criação de vincos rígidos.",
        tipo_operacao="CONTROLE",
        equacao_simbolica="Transformação Identidade 2D"
    ),
}
