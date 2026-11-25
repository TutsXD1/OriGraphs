"""
test_origraphs_completo.py

Suíte de Testes Avançada para o framework OriGraphs (TCC 2).
Valida rigorosamente as transformações afins, topologia de grafos,
teoremas de dobrabilidade plana e propriedades de Linguagens Formais.
"""

import numpy as np
import pytest
from matplotlib.figure import Figure

from biblioteca_acoes import BIBLIOTECA_DE_ACOES
from classes_origami import Origami
from motor_grafico import MotorGraficoPapel

@pytest.fixture
def motor_vazio() -> MotorGraficoPapel:
    return MotorGraficoPapel(altura=51, largura=51)

@pytest.fixture
def origami_aviao() -> Origami:
    aviao = Origami("Avião de Teste")
    acoes = [
        'DOBRAR_MEIO_D_E', 'DESDOBRAR_PASSO_ANTERIOR',
        'DOBRAR_CANTO_TD_C', 'DOBRAR_CANTO_TE_C',
        'DOBRAR_MEIO_D_E', 'ENTRAR_SETOR_S', 'DOBRAR_MEIO_E_D',
        'DESDOBRAR_PARCIALMENTE', 'VIRAR_PAPEL', 'DOBRAR_MEIO_D_E',
        'DESDOBRAR_PARCIALMENTE'
    ]
    for acao in acoes:
        aviao.adicionar_passo(acao)
    return aviao

@pytest.fixture
def origami_base_peixe() -> Origami:
    base = Origami("Prefixo Base")
    acoes = ['DOBRAR_DIAG_TD_BE', 'DOBRAR_DIAG_TE_BD', 'COLAPSAR_LATERAIS']
    for acao in acoes:
        base.adicionar_passo(acao)
    return base

@pytest.fixture
def origami_base_bomba() -> Origami:
    base = Origami("Bomba")
    base.adicionar_passo('COLAPSAR_LATERAIS')
    return base

# --- BLOCO 1 ---
def test_involucao_matriz_reflexao(motor_vazio: MotorGraficoPapel):
    m_ref = motor_vazio.gerar_matriz_reflexao_afim(1.0, 1.0, -1.5)
    identidade = np.eye(3, dtype=np.float64)
    produto = m_ref @ m_ref
    assert np.allclose(produto, identidade, atol=1e-10)

def test_ciclo_fechado_rotacoes(motor_vazio: MotorGraficoPapel):
    coords_originais = motor_vazio.coords_homogeneas.copy()
    for _ in range(4):
        motor_vazio.rotacionar_papel(-90.0)
    coords_finais = motor_vazio.coords_homogeneas
    erro_maximo = np.max(np.abs(coords_originais - coords_finais))
    assert erro_maximo < 1e-10

def test_bounding_box_dinamica(motor_vazio: MotorGraficoPapel):
    motor_vazio.aplicar_acao('DOBRAR_MEIO_D_E')
    xmin, xmax, ymin, ymax = motor_vazio.obter_bbox_ativa()
    # A malha discreta pode ter desvios, usamos isclose com tolerância da célula (0.02)
    assert np.isclose(xmin, 0.0, atol=0.03)
    assert np.isclose(xmax, 0.5, atol=0.03), f"xmax ajustou para {xmax} em vez de 0.5"
    assert np.isclose(ymax, 1.0, atol=0.03)

# --- BLOCO 2 ---
def test_lfa_relacoes_formais(origami_aviao: Origami, origami_base_peixe: Origami):
    assert origami_aviao.is_subpalavra(origami_aviao) is True
    prefixo_aviao = Origami("Teste Prefixo").adicionar_passo('DOBRAR_MEIO_D_E')
    assert origami_aviao.is_prefixo(prefixo_aviao) is True
    assert origami_aviao.is_subpalavra(origami_base_peixe) is False

def test_grafo_estrutura_e_graus(origami_base_peixe: Origami):
    # Correção: O grafo rotula com o nome extenso da ação, e não a chave 'INICIO'
    nome_inicio = BIBLIOTECA_DE_ACOES['INICIO'].nome
    grau_in, grau_out = origami_base_peixe.obter_grau_vertice(nome_inicio)
    assert grau_in == 0, "O estado inicial não deve possuir arestas de entrada."
    assert grau_out >= 1

def test_subgrafo_induzido():
    g_maior = Origami("G").adicionar_passo('DOBRAR_MEIO_D_E').adicionar_passo('VIRAR_PAPEL')
    h_menor = Origami("H").adicionar_passo('DOBRAR_MEIO_D_E')
    assert g_maior.is_subgrafo_induzido(h_menor) is True

# --- BLOCO 3 ---
def test_teorema_maekawa(origami_base_bomba: Origami):
    motor = origami_base_bomba.simular_geometria_papel()
    props = motor.avaliar_propriedades_fisicas()
    
    # A base bomba de água regista 4 vincos Vale e 2 Pico que convergem no centro
    # Total de raios = 6. Diferença |V - P| = |4 - 2| = 2.
    assert props["total_vincos"] >= 6
    assert props["diferenca_maekawa"] == 2, f"Violação de Maekawa: Diferença foi {props['diferenca_maekawa']}"

def test_empilhamento_camadas_z(motor_vazio: MotorGraficoPapel):
    motor_vazio.aplicar_acao('DOBRAR_MEIO_D_E')
    motor_vazio.aplicar_acao('DOBRAR_MEIO_B_T')
    props = motor_vazio.avaliar_propriedades_fisicas()
    # 2 dobras sequenciais geram 4 quadrantes empilhados
    assert props["camadas_z"] == 4

def test_desdobrar_preserva_crease_pattern(motor_vazio: MotorGraficoPapel):
    motor_vazio.aplicar_acao('DOBRAR_MEIO_D_E')
    num_vincos_antes = len(motor_vazio.vincos_uv)
    assert num_vincos_antes > 0
    motor_vazio.aplicar_acao('DESDOBRAR_PASSO_ANTERIOR')
    _, xmax, _, _ = motor_vazio.obter_bbox_ativa()
    assert np.isclose(xmax, 1.0, atol=0.03)
    assert len(motor_vazio.vincos_uv) == num_vincos_antes

# --- BLOCO 4 ---
def test_protecao_anti_none_na_renderizacao(origami_aviao: Origami):
    fig = origami_aviao.obter_imagem_papel(mostrar_vincos=True)
    assert isinstance(fig, Figure)

def test_metadados_biblioteca_acoes():
    for chave, acao in BIBLIOTECA_DE_ACOES.items():
        assert acao.tipo_operacao in ["DOBRA", "ROTACAO", "VIRAR", "DESDOBRAR", "SETOR", "COMPOSTA", "CONTROLE"]
        if acao.tipo_operacao == "DOBRA":
            assert acao.axioma is not None
            assert acao.tipo_dobra in ["VALE", "PICO"]
