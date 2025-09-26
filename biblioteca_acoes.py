# biblioteca_acoes.py

class Acao:
    """Representa uma única ação de origami, um 'bloco de construção'."""
    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao
    def __repr__(self):
        return f"Acao('{self.nome}')"

# --- BIBLIOTECA DE AÇÕES ---

BIBLIOTECA_DE_ACOES = {

    # Ações de controle
    'INICIO': Acao("Início: Papel Quadrado", "Comece com uma folha de papel quadrada sobre a mesa."),
    'ORIGAMI_FINALIZADO': Acao("Origami Finalizado", "O modelo está completo."),

    # --- 1. Dobras Fundamentais ---

    # Dobras ao Meio
    'DOBRAR_MEIO_D_E': Acao("Dobra ao Meio (D->E)", "Leve a borda da direita e dobre-a sobre a borda da esquerda."),
    'DOBRAR_MEIO_E_D': Acao("Dobra ao Meio (E->D)", "Leve a borda da esquerda e dobre-a sobre a borda da direita."),
    'DOBRAR_MEIO_B_T': Acao("Dobra ao Meio (B->T)", "Leve a borda de baixo e dobre-a sobre a borda do topo."),
    'DOBRAR_MEIO_T_B': Acao("Dobra ao Meio (T->B)", "Leve a borda do topo e dobre-a sobre a borda de baixo."),

    # Dobras na Diagonal
    'DOBRAR_DIAG_BE_TD': Acao("Dobra na Diagonal (BE->TD)", "Leve o canto inferior esquerdo (BE) até o canto superior direito (TD)."),
    'DOBRAR_DIAG_BD_TE': Acao("Dobra na Diagonal (BD->TE)", "Leve o canto inferior direito (BD) até o canto superior esquerdo (TE)."),
    'DOBRAR_DIAG_TE_BD': Acao("Dobra na Diagonal (TE->BD)", "Leve o canto superior esquerdo (TE) até o canto inferior direito (BD)."),
    'DOBRAR_DIAG_TD_BE': Acao("Dobra na Diagonal (TD->BE)", "Leve o canto superior direito (TD) até o canto inferior esquerdo (BE)."),

    # Dobras Canto ao Centro
    'DOBRAR_CANTO_TD_C': Acao("Dobra Canto ao Centro (TD->C)", "Leve o canto superior direito (TD) até o ponto central (C) do papel."),
    'DOBRAR_CANTO_TE_C': Acao("Dobra Canto ao Centro (TE->C)", "Leve o canto superior esquerdo (TE) até o ponto central (C) do papel."),
    'DOBRAR_CANTO_BD_C': Acao("Dobra Canto ao Centro (BD->C)", "Leve o canto inferior direito (BD) até o ponto central (C) do papel."),
    'DOBRAR_CANTO_BE_C': Acao("Dobra Canto ao Centro (BE->C)", "Leve o canto inferior esquerdo (BE) até o ponto central (C) do papel."),

    # Dobra Vale
    'DOBRA_VALE_TD_BC': Acao("Dobra Vale (TD->BC)", "Dobre o canto superior direito (TD) em direção a parte baixa centro (BC) formando um vale."),
    'DOBRA_VALE_TE_BC': Acao("Dobra Vale (TE->BC)", "Dobre o canto superior esquerdo (TE) em direção a parte baixa centro (BC) formando um vale."),

    # Dobra Pico/Montanha
    'DOBRA_PICO_BD_TC': Acao("Dobra Pico (BD->TC)", "Dobre o canto inferior direito (BD) em direção ao centro de cima (TC)."),
    'DOBRA_PICO_BE_TC': Acao("Dobra Pico (BE->TC)", "Dobre o canto inferior esquerdo (BE) em direção ao centro de cima (TC)."),


    # --- 2. Manipulações ---
    'DESDOBRAR_PASSO_ANTERIOR': Acao("Desdobrar Passo Anterior", "Desfaça a última dobra ou manipulação realizada."),
    'DESDOBRAR_PARCIALMENTE': Acao("Desdobrar Parcialmente", "Desfaça apenas parte da última dobra ou manipulação realizada."),
    'ROTACIONAR_90_D': Acao("Rotacionar 90° (D)", "Gire o papel 90 graus para a direita (sentido horário)."),
    'ROTACIONAR_90_E': Acao("Rotacionar 90° (E)", "Gire o papel 90 graus para a esquerda (sentido anti-horário)."),
    'ROTACIONAR_45_D': Acao("Rotacionar 45° (D)", "Gire o papel 45 graus para a direita (sentido horário)."),
    'ROTACIONAR_45_E': Acao("Rotacionar 45° (E)", "Gire o papel 45 graus para a esquerda (sentido anti-horário)."),
    'ROTACIONAR_180': Acao("Rotacionar 180°", "Gire o papel 180 graus."),
    'VIRAR_PAPEL': Acao("Virar", "Vire o papel completamente, de modo que o lado de inferior fique para a parte superios na horizontal."),
    'ABRIR_ABA': Acao("Abrir Aba", "Levante a aba ou camada superior para revelar o que está embaixo."),
    'ESCONDER_ABA_DENTRO': Acao("Esconder Aba", "Dobre e esconda uma aba ou ponta dentro de um 'bolso' de papel."),

    # --- 3. Manipulações de Setores
    'ENTRAR_SETOR_D': Acao("Entrar no Setor (D)", "Manipule somente o papel no setor da direita."),
    'ENTRAR_SETOR_E': Acao("Entrar no Setor (E)", "Manipule somente o papel no setor da esquerda."),
    'ENTRAR_SETOR_T': Acao("Entrar no Setor (T)", "Manipule somente o papel no setor do topo."),
    'ENTRAR_SETOR_B': Acao("Entrar no Setor (B)", "Manipule somente o papel no setor de baixo."),
    'ENTRAR_SETOR_S': Acao("Entrar no Setor (S)", "Manipule somente o papel no setor da superfície."),
    'ENTRAR_SETOR_I': Acao("Entrar no Setor (I)", "Manipule somente o papel no setor interno."),
    'SAIR_SETOR_ANTERIOR': Acao("Sair do Setor Anterior", "Saia do setor que você estava manipulando."),

    # --- 4. Dobras Compostas ---
    'DOBRA_ESMAGADA': Acao("Dobra Esmagada", "Abra uma aba e achate-a (esmague-a) simetricamente, formando um losango."),
    'DOBRA_PETALA': Acao("Dobra Pétala", "Execute a dobra pétala, levantando uma ponta enquanto afina a base, comum em flores e pássaros."),
    'DOBRA_REVERSA_INTERNA': Acao("Dobra Reversa Interna", "Empurre uma ponta para dentro do modelo, entre as camadas de papel, para formar pescoços ou caudas."),
    'DOBRA_REVERSA_EXTERNA': Acao("Dobra Reversa Externa", "Dobre uma ponta para fora, envolvendo as camadas de papel existentes."),
    'ORELHA_DE_COELHO': Acao("Dobra Orelha de Coelho", "Achate um canto do papel de forma a criar uma ponta mais fina, colapsando as laterais."),
    'AFUNDAR_PONTA': Acao("Afundar Ponta", "Uma manobra avançada onde um vértice do modelo é empurrado para dentro do modelo."),
    'VINCO_PREGAS': Acao("Vinco de Pregas", "Crie uma série de dobras vale e montanha alternadas para encurtar uma aba, como para fazer pernas ou pescoços."),
    'COLAPSAR_LATERAIS': Acao("Colapsar as Laterias", "Pegue o meio das laterais e colapse os meios na borda de Baixo formando dois Triangulos, Superior e Inferior (Caixa d'Água)"),

    # --- 5. Finalização e Modelagem 3D ---
    'INFLAR_MODELO': Acao("Inflar Modelo", "Assopre em uma abertura para dar volume tridimensional ao modelo (ex: balão)."),
    'ARREDONDAR_CURVAR': Acao("Modelar/Curvar", "Use os dedos para dar forma ao papel sem criar vincos duros, como curvar asas ou pétalas."),

}