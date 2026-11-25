"""
motor_grafico.py

Motor gráfico matricial 2D/2.5D em coordenadas homogêneas para o OriGraphs.
Corrige:
1. Deslocamento de vincos no espaço UV (usa interseção analítica exata em vez de argmax na grade).
2. Assimetria de setores (mantém o eixo central do modelo estável ao entrar em setores D/E/T/B).
3. Artefatos de células mistas no vinco (descarta células cujos 4 vértices foram cortados pela dobra).
4. Distorção de Bounding Box em 'DESDOBRAR_PARCIALMENTE' antes de virar o papel.
"""

from typing import Dict, List, Optional, Tuple
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.collections import PolyCollection

from biblioteca_acoes import Acao, BIBLIOTECA_DE_ACOES


class MotorGraficoPapel:
    """
    Motor de simulação física e geométrica de origami em Álgebra Linear.
    """

    def __init__(self, altura: int = 51, largura: int = 51) -> None:
        self.altura: int = altura
        self.largura: int = largura
        self.historico_estados: List[Dict] = []
        self.vincos_uv: List[Tuple[np.ndarray, np.ndarray, str]] = []
        self.setor_ativo: Optional[str] = None
        self.id_aba: np.ndarray = np.zeros(1, dtype=np.int32)
        self.eixo_centro_global: Tuple[float, float] = (0.5, 0.5)
        self.bbox_referencia_global: Tuple[float, float, float, float] = (0.0, 1.0, 0.0, 1.0)
        self.offsets_25d: np.ndarray = np.zeros((2, 1), dtype=np.float64)

        self.resetar()

    def resetar(self) -> None:
        """Restaura o papel ao estado plano inicial ('INICIO') em [0, 1] x [0, 1]."""
        u = np.linspace(0.0, 1.0, self.largura)
        v = np.linspace(0.0, 1.0, self.altura)
        uu, vv = np.meshgrid(u, v)

        self.coords_uv = np.stack([uu.ravel(), vv.ravel()], axis=-1)
        num_pontos = self.coords_uv.shape[0]

        # Coordenadas homogêneas estruturais 3xN (sem deformação 2.5D estética)
        self.coords_homogeneas = np.vstack([
            self.coords_uv[:, 0],
            self.coords_uv[:, 1],
            np.ones(num_pontos, dtype=np.float64)
        ])

        # Offsets puramente visuais para projeção 2.5D (DESDOBRAR_PARCIALMENTE)
        # Mantém a geometria base 100% íntegra para as próximas dobras!
        self.offsets_25d = np.zeros((2, num_pontos), dtype=np.float64)

        self.z_order = np.zeros(num_pontos, dtype=np.float64)
        self.face_visivel = np.ones(num_pontos, dtype=np.int8)
        self.id_aba = np.where(self.coords_uv[:, 0] > 0.5, 1, 0)
        self.eixo_centro_global = (0.5, 0.5)
        self.bbox_referencia_global = (0.0, 1.0, 0.0, 1.0)

        self.historico_estados.clear()
        self.vincos_uv.clear()
        self.setor_ativo = None

    def _atualizar_referencia_global(self) -> None:
        """Atualiza o centro e a Bounding Box global apenas quando fora de setores locais."""
        if self.setor_ativo is None or self.setor_ativo in ("TODAS", "S", "I", "SUPERFICIE", "INTERNO"):
            x = self.coords_homogeneas[0, :]
            y = self.coords_homogeneas[1, :]
            xmin, xmax = float(np.min(x)), float(np.max(x))
            ymin, ymax = float(np.min(y)), float(np.max(y))
            self.bbox_referencia_global = (xmin, xmax, ymin, ymax)
            self.eixo_centro_global = (0.5 * (xmin + xmax), 0.5 * (ymin + ymax))

    def _salvar_checkpoint(
        self,
        reta_dobra: Optional[Tuple[float, float, float]] = None,
        mascara_movida: Optional[np.ndarray] = None
    ) -> None:
        estado = {
            "coords": self.coords_homogeneas.copy(),
            "offsets_25d": self.offsets_25d.copy(),
            "z_order": self.z_order.copy(),
            "face": self.face_visivel.copy(),
            "vincos": copy.deepcopy(self.vincos_uv),
            "setor": self.setor_ativo,
            "eixo_centro": self.eixo_centro_global,
            "bbox_global": self.bbox_referencia_global,
            "reta_dobra": reta_dobra,
            "mascara_movida": mascara_movida.copy() if mascara_movida is not None else None
        }
        self.historico_estados.append(estado)

    @staticmethod
    def gerar_matriz_reflexao_afim(a: float, b: float, c: float) -> np.ndarray:
        """Gera a Matriz de Reflexão Afim Homogênea 3x3 para a reta ax + by + c = 0."""
        norma = np.hypot(a, b)
        if norma < 1e-12:
            return np.eye(3, dtype=np.float64)

        nx_val = a / norma
        ny_val = b / norma
        d_val = c / norma

        return np.array([
            [1.0 - 2.0 * nx_val**2, -2.0 * nx_val * ny_val, -2.0 * nx_val * d_val],
            [-2.0 * nx_val * ny_val, 1.0 - 2.0 * ny_val**2, -2.0 * ny_val * d_val],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)

    @staticmethod
    def gerar_matriz_rotacao_afim(
        angulo_graus: float,
        centro: Tuple[float, float] = (0.5, 0.5)
    ) -> np.ndarray:
        """Gera a Matriz Homogênea 3x3 de rotação em torno do pivô (cx, cy)."""
        theta = np.radians(angulo_graus)
        cos_t, sin_t = np.cos(theta), np.sin(theta)
        cx, cy = centro

        tx = cx - cos_t * cx + sin_t * cy
        ty = cy - sin_t * cx - cos_t * cy

        return np.array([
            [cos_t, -sin_t, tx],
            [sin_t,  cos_t, ty],
            [0.0,    0.0,   1.0]
        ], dtype=np.float64)

    def _obter_mascara_setor(self) -> np.ndarray:
        """
        Retorna a máscara booleana dos pontos pertencentes ao setor ativo.
        Usa `eixo_centro_global` congelado no momento da entrada no setor para
        garantir simetria bilateral perfeita (ex: chifres esquerdo e direito do Boi).
        """
        x = self.coords_homogeneas[0, :]
        y = self.coords_homogeneas[1, :]
        num_pontos = x.shape[0]

        if self.setor_ativo is None or self.setor_ativo == "TODAS":
            return np.ones(num_pontos, dtype=bool)

        x_med, y_med = self.eixo_centro_global

        if self.setor_ativo == 'D':
            return x >= x_med - 1e-5
        if self.setor_ativo == 'E':
            return x <= x_med + 1e-5
        if self.setor_ativo == 'T':
            return y >= y_med - 1e-5
        if self.setor_ativo == 'B':
            return y <= y_med + 1e-5

        z_media_aba0 = float(np.mean(self.z_order[self.id_aba == 0]))
        z_media_aba1 = float(np.mean(self.z_order[self.id_aba == 1]))

        if abs(z_media_aba0 - z_media_aba1) > 1e-3:
            aba_superior = 0 if z_media_aba0 > z_media_aba1 else 1
            if self.setor_ativo in ('S', 'SUPERFICIE'):
                return self.id_aba == aba_superior
            if self.setor_ativo in ('I', 'INTERNO'):
                return self.id_aba != aba_superior

        z_divisor = 0.5 * (float(np.min(self.z_order)) + float(np.max(self.z_order)))
        if self.setor_ativo in ('S', 'SUPERFICIE'):
            return self.z_order >= z_divisor
        if self.setor_ativo in ('I', 'INTERNO'):
            return self.z_order < z_divisor

        return np.ones(num_pontos, dtype=bool)

    def obter_bbox_ativa(self) -> Tuple[float, float, float, float]:
        """
        Retorna (xmin, xmax, ymin, ymax) simétrico para o setor ativo.
        Se o setor for D, E, T ou B, usa a BBox de referência global dividida pelo
        eixo de simetria, garantindo que o Setor E e o Setor D tenham exatamente
        as mesmas dimensões espelhadas!
        """
        g_xmin, g_xmax, g_ymin, g_ymax = self.bbox_referencia_global
        x_med, y_med = self.eixo_centro_global

        if self.setor_ativo == 'D':
            return (x_med, g_xmax, g_ymin, g_ymax)
        if self.setor_ativo == 'E':
            return (g_xmin, x_med, g_ymin, g_ymax)
        if self.setor_ativo == 'T':
            return (g_xmin, g_xmax, y_med, g_ymax)
        if self.setor_ativo == 'B':
            return (g_xmin, g_xmax, g_ymin, y_med)

        mascara = self._obter_mascara_setor()
        if not np.any(mascara):
            mascara = np.ones(self.coords_homogeneas.shape[1], dtype=bool)

        x_ativo = self.coords_homogeneas[0, mascara]
        y_ativo = self.coords_homogeneas[1, mascara]
        return (
            float(np.min(x_ativo)),
            float(np.max(x_ativo)),
            float(np.min(y_ativo)),
            float(np.max(y_ativo))
        )

    def _registrar_vinco_no_espaco_uv(
        self,
        a: float,
        b: float,
        c: float,
        mascara_setor: np.ndarray,
        tipo: str
    ) -> None:
        """
        Calcula com precisão analítica os segmentos de vinco no espaço UV [0, 1]².
        Usa detecção de cruzamento de arestas (zero-crossing da distância sinalizada)
        na malha (H, W) para nunca deslocar ou entortar retas como x = 0.5!
        """
        norma = np.hypot(a, b)
        if norma < 1e-12:
            return

        x_grid = self.coords_homogeneas[0, :].reshape(self.altura, self.largura)
        y_grid = self.coords_homogeneas[1, :].reshape(self.altura, self.largura)
        z_grid = self.z_order.reshape(self.altura, self.largura)
        m_grid = mascara_setor.reshape(self.altura, self.largura)
        u_grid = self.coords_uv[:, 0].reshape(self.altura, self.largura)
        v_grid = self.coords_uv[:, 1].reshape(self.altura, self.largura)

        d_grid = (a * x_grid + b * y_grid + c) / norma

        # Agrupa por camada Z para extrair o segmento exato de cada folha dobrada
        for z_val in np.unique(z_grid[m_grid]):
            mask_z = m_grid & (np.abs(z_grid - z_val) < 1e-4)
            if np.count_nonzero(mask_z) < 3:
                continue

            pts_intersecao_uv = []

            # 1. Vértices que já caem exatamente sobre a reta (ex: U = 0.500000)
            exatos = mask_z & (np.abs(d_grid) <= 1e-6)
            if np.any(exatos):
                pts_intersecao_uv.append(
                    np.stack([u_grid[exatos], v_grid[exatos]], axis=-1)
                )

            # 2. Interpolação linear exata nas arestas horizontais onde d muda de sinal
            val_h = mask_z[:, :-1] & mask_z[:, 1:]
            d1_h, d2_h = d_grid[:, :-1], d_grid[:, 1:]
            cruz_h = val_h & ((d1_h * d2_h) < -1e-10)
            if np.any(cruz_h):
                t = np.abs(d1_h[cruz_h]) / (np.abs(d1_h[cruz_h]) + np.abs(d2_h[cruz_h]))
                u_int = (1.0 - t) * u_grid[:, :-1][cruz_h] + t * u_grid[:, 1:][cruz_h]
                v_int = (1.0 - t) * v_grid[:, :-1][cruz_h] + t * v_grid[:, 1:][cruz_h]
                pts_intersecao_uv.append(np.stack([u_int, v_int], axis=-1))

            # 3. Interpolação linear exata nas arestas verticais onde d muda de sinal
            val_v = mask_z[:-1, :] & mask_z[1:, :]
            d1_v, d2_v = d_grid[:-1, :], d_grid[1:, :]
            cruz_v = val_v & ((d1_v * d2_v) < -1e-10)
            if np.any(cruz_v):
                t = np.abs(d1_v[cruz_v]) / (np.abs(d1_v[cruz_v]) + np.abs(d2_v[cruz_v]))
                u_int = (1.0 - t) * u_grid[:-1, :][cruz_v] + t * u_grid[1:, :][cruz_v]
                v_int = (1.0 - t) * v_grid[:-1, :][cruz_v] + t * v_grid[1:, :][cruz_v]
                pts_intersecao_uv.append(np.stack([u_int, v_int], axis=-1))

            if not pts_intersecao_uv:
                continue

            uv_all = np.vstack(pts_intersecao_uv)
            if uv_all.shape[0] < 2:
                continue

            # Como todos os pontos de uma mesma camada Z plana pertencem à mesma reta em UV,
            # os dois pontos extremos da coleção definem o segmento analítico exato!
            dists_uv = np.sum((uv_all[:, None, :] - uv_all[None, :, :]) ** 2, axis=-1)
            idx_max = np.unravel_index(np.argmax(dists_uv), dists_uv.shape)
            p1_uv = np.round(uv_all[idx_max[0]], 4)
            p2_uv = np.round(uv_all[idx_max[1]], 4)

            if np.linalg.norm(p1_uv - p2_uv) > 0.04:
                se_borda_h = np.isclose(p1_uv[1], p2_uv[1], atol=1e-3) and (
                    np.isclose(p1_uv[1], 0.0, atol=1e-3) or np.isclose(p1_uv[1], 1.0, atol=1e-3)
                )
                se_borda_v = np.isclose(p1_uv[0], p2_uv[0], atol=1e-3) and (
                    np.isclose(p1_uv[0], 0.0, atol=1e-3) or np.isclose(p1_uv[0], 1.0, atol=1e-3)
                )
                if not (se_borda_h or se_borda_v):
                    duplicado = False
                    for ex_p1, ex_p2, _ in self.vincos_uv:
                        d_dir = np.linalg.norm(p1_uv - ex_p1) + np.linalg.norm(p2_uv - ex_p2)
                        d_inv = np.linalg.norm(p1_uv - ex_p2) + np.linalg.norm(p2_uv - ex_p1)
                        if min(d_dir, d_inv) < 0.03:
                            duplicado = True
                            break
                    if not duplicado:
                        self.vincos_uv.append((p1_uv, p2_uv, tipo.lower()))

    def aplicar_dobra_reta(
        self,
        a: float,
        b: float,
        c: float,
        sinal_semiplano: int = 1,
        tipo: str = "VALE"
    ) -> None:
        """Reflete os pontos situados no semiplano ativo e atualiza a pilha Z."""
        x = self.coords_homogeneas[0, :]
        y = self.coords_homogeneas[1, :]
        mascara_setor = self._obter_mascara_setor()

        distancia_sinalizada = (a * x + b * y + c) * sinal_semiplano
        mascara_semiplano = distancia_sinalizada > 1e-6
        mascara_ativa = mascara_semiplano & mascara_setor

        self._salvar_checkpoint(reta_dobra=(a, b, c), mascara_movida=mascara_ativa)

        if not np.any(mascara_ativa):
            return

        self._registrar_vinco_no_espaco_uv(a, b, c, mascara_setor, tipo)

        matriz_ref = self.gerar_matriz_reflexao_afim(a, b, c)
        self.coords_homogeneas[:, mascara_ativa] = (
            matriz_ref @ self.coords_homogeneas[:, mascara_ativa]
        )

        # Se havia algum offset 2.5D nos pontos movidos, reflete-o também
        if np.any(self.offsets_25d[:, mascara_ativa]):
            lin_ref = matriz_ref[:2, :2]
            self.offsets_25d[:, mascara_ativa] = lin_ref @ self.offsets_25d[:, mascara_ativa]

        self.face_visivel[mascara_ativa] *= -1

        z_max_global = float(np.max(self.z_order))
        z_min_global = float(np.min(self.z_order))

        if tipo.upper() == "VALE":
            z_max_bloco = float(np.max(self.z_order[mascara_ativa]))
            self.z_order[mascara_ativa] = (
                z_max_global + 1.0 + (z_max_bloco - self.z_order[mascara_ativa])
            )
        else:
            z_min_bloco = float(np.min(self.z_order[mascara_ativa]))
            self.z_order[mascara_ativa] = (
                z_min_global - 1.0 - (self.z_order[mascara_ativa] - z_min_bloco)
            )

        self.z_order = np.round(self.z_order, 4)
        z_unicos = np.unique(self.z_order)
        z_map = {val: i for i, val in enumerate(np.sort(z_unicos))}
        self.z_order = np.vectorize(z_map.get)(self.z_order).astype(np.float64)

        self._atualizar_referencia_global()

    def rotacionar_papel(self, angulo_graus: float) -> None:
        """Rotaciona o modelo em torno do centro da sua Bounding Box global."""
        self._salvar_checkpoint()
        x = self.coords_homogeneas[0, :]
        y = self.coords_homogeneas[1, :]
        centro = (
            0.5 * (float(np.min(x)) + float(np.max(x))),
            0.5 * (float(np.min(y)) + float(np.max(y)))
        )
        matriz_rot = self.gerar_matriz_rotacao_afim(angulo_graus, centro=centro)
        self.coords_homogeneas = matriz_rot @ self.coords_homogeneas
        if np.any(self.offsets_25d):
            self.offsets_25d = matriz_rot[:2, :2] @ self.offsets_25d
        self._atualizar_referencia_global()

    def virar_papel(self) -> None:
        """
        Vira o papel horizontalmente em torno do eixo de referência estrutural,
        sem ser contaminado por abas abertas em 2.5D!
        """
        self._salvar_checkpoint()
        x_centro = self.eixo_centro_global[0]

        matriz_flip = self.gerar_matriz_reflexao_afim(1.0, 0.0, -x_centro)
        self.coords_homogeneas = matriz_flip @ self.coords_homogeneas
        if np.any(self.offsets_25d):
            self.offsets_25d[0, :] = -self.offsets_25d[0, :]

        self.z_order = -self.z_order
        self.z_order = np.round(self.z_order - np.min(self.z_order), 4)
        self.face_visivel *= -1
        self._atualizar_referencia_global()

    def desdobrar_ultimo_passo(self, fator_parcial: float = 0.0) -> None:
        """
        - Se `fator_parcial == 0.0` (`DESDOBRAR_PASSO_ANTERIOR`): Restaura 100% as coordenadas
          estruturais anteriores, preservando o vinco UV.
        - Se `fator_parcial > 0.0` (`DESDOBRAR_PARCIALMENTE`): Aplica o deslocamento de abertura
          no buffer `offsets_25d`, mantendo `coords_homogeneas` intacto para que o próximo
          `VIRAR_PAPEL` e a dobra da segunda asa do avião tenham simetria matemática perfeita!
        """
        if not self.historico_estados:
            return

        ultimo = self.historico_estados.pop()

        if fator_parcial <= 1e-5:
            vincos_atuais = copy.deepcopy(self.vincos_uv)
            self.coords_homogeneas = ultimo["coords"]
            self.offsets_25d = ultimo["offsets_25d"]
            self.z_order = ultimo["z_order"]
            self.face_visivel = ultimo["face"]
            self.eixo_centro_global = ultimo["eixo_centro"]
            self.bbox_global = ultimo["bbox_global"]
            self.vincos_uv = vincos_atuais
            self._atualizar_referencia_global()
        else:
            # Mantém a geometria estrutural dobrada intacta, mas adiciona projeção 2.5D visual!
            coords_dobradas = self.coords_homogeneas[:2, :]
            coords_antes = ultimo["coords"][:2, :]
            deslocamento = coords_antes - coords_dobradas
            movidos = np.linalg.norm(deslocamento, axis=0) > 1e-5

            if np.any(movidos):
                # Abre a asa em 35% de volta para a posição pré-dobra como efeito 2.5D
                self.offsets_25d[:, movidos] = (1.0 - fator_parcial) * deslocamento[:, movidos]

    def _executar_colapso_bomba_dagua(self) -> None:
        """Executa o colapso simultâneo da Base Bomba d'Água."""
        self._salvar_checkpoint()
        self.vincos_uv.append((np.array([0.0, 0.0]), np.array([0.5, 0.5]), 'vale'))
        self.vincos_uv.append((np.array([0.5, 0.5]), np.array([1.0, 1.0]), 'vale'))
        self.vincos_uv.append((np.array([0.0, 1.0]), np.array([0.5, 0.5]), 'vale'))
        self.vincos_uv.append((np.array([0.5, 0.5]), np.array([1.0, 0.0]), 'vale'))
        self.vincos_uv.append((np.array([0.0, 0.5]), np.array([0.5, 0.5]), 'pico'))
        self.vincos_uv.append((np.array([0.5, 0.5]), np.array([1.0, 0.5]), 'pico'))

        u = self.coords_uv[:, 0]
        v = self.coords_uv[:, 1]
        dist_centro_x = np.abs(u - 0.5)
        novo_y = 0.5 * (1.0 - np.maximum(2.0 * dist_centro_x, np.abs(2.0 * v - 1.0)))
        novo_x = np.where(u < 0.5, 0.5 - (0.5 - novo_y), 0.5 + (0.5 - novo_y))

        self.coords_homogeneas[0, :] = novo_x
        self.coords_homogeneas[1, :] = novo_y
        self.z_order = np.where(v > 0.5, 2.0, np.where(u < 0.5, 1.0, 0.0))
        self._atualizar_referencia_global()

    def aplicar_acao(self, chave_acao: str) -> None:
        """Despacha a chave da ação para a operação geométrica correspondente."""
        if chave_acao not in BIBLIOTECA_DE_ACOES:
            raise ValueError(f"Ação '{chave_acao}' não encontrada em BIBLIOTECA_DE_ACOES.")

        acao: Acao = BIBLIOTECA_DE_ACOES[chave_acao]

        if chave_acao == 'INICIO':
            self.resetar()
            return

        if acao.tipo_operacao == "CONTROLE":
            self.setor_ativo = None
            self._atualizar_referencia_global()
            return

        if acao.tipo_operacao == "SETOR":
            if acao.camadas == "TODAS":
                self.setor_ativo = None
                self._atualizar_referencia_global()
            else:
                # Congela a referência global antes de entrar no setor para manter simetria D/E
                if self.setor_ativo is None:
                    self._atualizar_referencia_global()
                self.setor_ativo = acao.camadas
            return

        if acao.tipo_operacao == "DESDOBRAR":
            fator = acao.parametro_adicional if acao.parametro_adicional is not None else 0.0
            self.desdobrar_ultimo_passo(fator_parcial=fator)
            return

        if acao.tipo_operacao == "ROTACAO":
            angulo = acao.parametro_adicional if acao.parametro_adicional is not None else 0.0
            self.rotacionar_papel(angulo)
            return

        if acao.tipo_operacao == "VIRAR":
            self.virar_papel()
            return

        if acao.tipo_operacao == "COMPOSTA":
            self._executar_colapso_bomba_dagua()
            return

        if acao.tipo_operacao == "DOBRA" and acao.reta_funcao is not None:
            xmin, xmax, ymin, ymax = self.obter_bbox_ativa()
            a, b, c, sinal = acao.reta_funcao(xmin, xmax, ymin, ymax)
            tipo_dobra = acao.tipo_dobra or "VALE"
            self.aplicar_dobra_reta(a, b, c, sinal_semiplano=sinal, tipo=tipo_dobra)

    def avaliar_propriedades_fisicas(self) -> Dict[str, object]:
        num_vale = sum(1 for _, _, t in self.vincos_uv if t == 'vale')
        num_pico = sum(1 for _, _, t in self.vincos_uv if t == 'pico')
        num_camadas = len(np.unique(np.round(self.z_order, 3)))
        return {
            "vincos_vale": num_vale,
            "vincos_pico": num_pico,
            "total_vincos": num_vale + num_pico,
            "camadas_z": num_camadas,
            "diferenca_maekawa": abs(num_vale - num_pico)
        }

    def renderizar(self, mostrar_vincos: bool = True) -> Figure:
        """
        Renderiza a malha 2D do origami (combinando coordenadas estruturais + offsets 2.5D)
        e descarta células que foram cortadas ao meio por um vinco para eliminar bordas azuis falsas.
        """
        if mostrar_vincos:
            fig, (ax_fisico, ax_cp) = plt.subplots(1, 2, figsize=(11, 5.2))
        else:
            fig, ax_fisico = plt.subplots(1, 1, figsize=(6, 5.5))
            ax_cp = None

        # Soma a coordenada estrutural com o deslocamento estético 2.5D (se houver)
        x_vis = self.coords_homogeneas[0, :] + self.offsets_25d[0, :]
        y_vis = self.coords_homogeneas[1, :] + self.offsets_25d[1, :]

        x_grid = x_vis.reshape(self.altura, self.largura)
        y_grid = y_vis.reshape(self.altura, self.largura)
        z_grid = self.z_order.reshape(self.altura, self.largura)
        face_grid = self.face_visivel.reshape(self.altura, self.largura)

        p00 = np.stack([x_grid[:-1, :-1], y_grid[:-1, :-1]], axis=-1)
        p10 = np.stack([x_grid[:-1, 1:],  y_grid[:-1, 1:]],  axis=-1)
        p11 = np.stack([x_grid[1:, 1:],   y_grid[1:, 1:]],   axis=-1)
        p01 = np.stack([x_grid[1:, :-1],  y_grid[1:, :-1]],  axis=-1)

        poligonos = np.stack([p00, p10, p11, p01], axis=2).reshape(-1, 4, 2)

        z_corners = np.stack([
            z_grid[:-1, :-1], z_grid[:-1, 1:], z_grid[1:, 1:], z_grid[1:, :-1]
        ], axis=-1).reshape(-1, 4)
        f_corners = np.stack([
            face_grid[:-1, :-1], face_grid[:-1, 1:], face_grid[1:, 1:], face_grid[1:, :-1]
        ], axis=-1).reshape(-1, 4)

        z_celulas = np.mean(z_corners, axis=1)
        face_celulas = np.sign(np.sum(f_corners, axis=1))

        # REGRA CRÍTICA ANTI-BORDA FALSA:
        # Uma célula da malha só é íntegra se todos os seus 4 vértices estiverem na mesma camada Z
        # e tiverem a mesma orientação de face! Se uma linha de dobra cortou a célula ao meio,
        # ela tem vértices em camadas/faces diferentes e não deve ser desenhada retorcida!
        mesma_camada = np.ptp(z_corners, axis=1) < 0.01
        mesma_face = np.ptp(f_corners, axis=1) == 0
        largura_celula = np.max(np.ptp(poligonos, axis=1), axis=1)
        celulas_validas = mesma_camada & mesma_face & (largura_celula < 0.15)

        if np.count_nonzero(celulas_validas) > 10:
            poligonos = poligonos[celulas_validas]
            z_celulas = z_celulas[celulas_validas]
            face_celulas = face_celulas[celulas_validas]

        ordem_z = np.argsort(z_celulas, kind='mergesort')
        poligonos_ord = poligonos[ordem_z]
        z_ord = z_celulas[ordem_z]
        face_ord = face_celulas[ordem_z]

        z_min = float(np.min(z_ord)) if len(z_ord) > 0 else 0.0
        z_max = float(np.max(z_ord)) if len(z_ord) > 0 else 1.0
        z_norm = (z_ord - z_min) / (max(z_max - z_min, 1.0))

        cores_face = np.zeros((len(z_ord), 4))
        m_frente = face_ord >= 0
        cores_face[m_frente, 0] = 0.16 + 0.28 * z_norm[m_frente]
        cores_face[m_frente, 1] = 0.52 + 0.30 * z_norm[m_frente]
        cores_face[m_frente, 2] = 0.86 + 0.10 * z_norm[m_frente]
        cores_face[m_frente, 3] = 1.0

        m_verso = ~m_frente
        cores_face[m_verso, 0] = 0.96 - 0.08 * (1.0 - z_norm[m_verso])
        cores_face[m_verso, 1] = 0.87 - 0.10 * (1.0 - z_norm[m_verso])
        cores_face[m_verso, 2] = 0.70 - 0.08 * (1.0 - z_norm[m_verso])
        cores_face[m_verso, 3] = 1.0

        colecao = PolyCollection(
            poligonos_ord,
            facecolors=cores_face,
            edgecolors='#1e293b',
            linewidths=0.25,
            antialiased=True
        )
        ax_fisico.add_collection(colecao)

        num_camadas = len(np.unique(np.round(self.z_order, 3)))
        subtitulo_setor = f" | Setor: {self.setor_ativo}" if self.setor_ativo else ""
        ax_fisico.set_title(
            f"Estado Físico 2D (Camadas Z: {num_camadas}{subtitulo_setor})",
            fontsize=11, fontweight='bold'
        )
        ax_fisico.set_xlim(-0.15, 1.15)
        ax_fisico.set_ylim(-0.15, 1.15)
        ax_fisico.set_aspect('equal')
        ax_fisico.grid(True, linestyle=':', alpha=0.4)
        ax_fisico.set_xlabel("X (Azul=Frente, Creme=Verso)")
        ax_fisico.set_ylabel("Y (Espaço Homogêneo)")

        if ax_cp is not None:
            quadrado_uv = plt.Rectangle(
                (0, 0), 1, 1, fill=True, facecolor='#f8fafc', edgecolor='#334155', linewidth=2
            )
            ax_cp.add_patch(quadrado_uv)

            for p1_uv, p2_uv, tipo in self.vincos_uv:
                cor_linha = '#2563eb' if tipo == 'vale' else '#dc2626'
                estilo = '--' if tipo == 'vale' else '-.'
                ax_cp.plot(
                    [p1_uv[0], p2_uv[0]],
                    [p1_uv[1], p2_uv[1]],
                    color=cor_linha, linestyle=estilo, linewidth=1.8, alpha=0.85
                )

            ax_cp.set_title("Padrão de Vincos (Espaço UV [0,1]²)", fontsize=11, fontweight='bold')
            ax_cp.set_xlim(-0.1, 1.1)
            ax_cp.set_ylim(-0.1, 1.1)
            ax_cp.set_aspect('equal')
            ax_cp.set_xlabel("U (Azul=Vale, Vermelho=Pico)")
            ax_cp.set_ylabel("V")
            ax_cp.grid(True, linestyle=':', alpha=0.3)

        fig.tight_layout()
        return fig
