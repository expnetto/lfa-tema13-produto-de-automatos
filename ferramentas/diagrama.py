"""Gera docs/diagrama.png a partir dos próprios autômatos de src/.

Só serve para refazer a figura (precisa de matplotlib); o programa do trabalho
não depende disso. Como as setas saem da tabela delta, o desenho nunca destoa do código.

    python ferramentas/diagrama.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from afd import POCO  # noqa: E402
from automatos import A, B, construir_produtos  # noqa: E402
from produto import OPERACOES  # noqa: E402

RAIO_PEQUENO = 0.24  # estados dos produtos
RAIO_GRANDE = 0.36   # estados de A e B (nomes mais longos)
COR = "#1f2937"
COR_FINAL = "#065f46"


def agrupa_setas(afd):
    """{(origem, destino): 'símbolos separados por vírgula'}, sem as setas do poço."""
    setas = {}
    for (origem, simbolo), destino in afd.delta.items():
        if POCO in (origem, destino):
            continue
        setas.setdefault((origem, destino), []).append(simbolo)
    return {par: ",".join(simbolos) for par, simbolos in setas.items()}


def desenha_estado(ax, afd, nome, posicao, lado, raio):
    x, y = posicao
    final = nome in afd.finais
    ax.add_patch(Circle((x, y), raio, fill=True, fc="#ecfdf5" if final else "white", ec=COR_FINAL if final else COR, lw=1.8))
    if final:
        ax.add_patch(Circle((x, y), raio - 0.05, fill=False, ec=COR_FINAL, lw=1.8))
    ax.text(x, y, nome, ha="center", va="center", fontsize=10 if raio > 0.3 else 11, fontweight="bold", color=COR)
    rotulo = afd.rotulos.get(nome)
    if rotulo and rotulo.startswith("("):  # o par (A, B) vai acima ou abaixo do estado
        acima = lado == "acima"
        ax.text(x, y + (raio + 0.1 if acima else -raio - 0.1), rotulo, ha="center",
                va="bottom" if acima else "top", fontsize=8.5, color="#4b5563")


def desenha_seta(ax, origem, destino, rotulo, curva, raio):
    (x1, y1), (x2, y2) = origem, destino
    if origem == destino:
        laco = FancyArrowPatch((x1 - 0.13, y1 + raio - 0.01), (x1 + 0.13, y1 + raio - 0.01),
                               connectionstyle="arc3,rad=-1.9", arrowstyle="-|>", mutation_scale=12, color=COR, lw=1.4)
        ax.add_patch(laco)
        ax.text(x1, y1 + raio + 0.34, rotulo, ha="center", va="center", fontsize=10, color=COR)
        return
    dx, dy = x2 - x1, y2 - y1
    tamanho = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / tamanho, dy / tamanho
    seta = FancyArrowPatch((x1 + ux * raio, y1 + uy * raio), (x2 - ux * raio, y2 - uy * raio),
                           connectionstyle=f"arc3,rad={curva}", arrowstyle="-|>", mutation_scale=12, color=COR, lw=1.4)
    ax.add_patch(seta)
    # ponto de maior afastamento da curva + um empurrão para o texto não ficar em cima da linha
    meio_x, meio_y = (x1 + x2) / 2, (y1 + y2) / 2
    empurrao = 0.5 * curva * tamanho + (0.13 if curva >= 0 else -0.13)
    ax.text(meio_x + empurrao * uy, meio_y - empurrao * ux, rotulo, ha="center", va="center", fontsize=10, color=COR)


def desenha_automato(ax, afd, posicoes, titulo, lados, raio):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, fontsize=11.5, fontweight="bold", color=COR, pad=6)
    for nome, posicao in posicoes.items():
        desenha_estado(ax, afd, nome, posicao, lados.get(nome), raio)
    for (origem, destino), rotulo in agrupa_setas(afd).items():
        desenha_seta(ax, posicoes[origem], posicoes[destino], rotulo, 0.0 if origem == destino else 0.28, raio)
    x, y = posicoes[afd.inicial]
    ax.add_patch(FancyArrowPatch((x - raio - 0.55, y), (x - raio, y), arrowstyle="-|>", mutation_scale=12, color=COR, lw=1.4))


def desenha_poco(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("poço (existe em todos os AFDs)", fontsize=11.5, fontweight="bold", color=COR, pad=6)
    ax.add_patch(Circle((2.2, 0.0), RAIO_GRANDE, fill=True, fc="#fef2f2", ec="#991b1b", lw=1.8))
    ax.text(2.2, 0.0, "poço", ha="center", va="center", fontsize=10, fontweight="bold", color="#991b1b")
    desenha_seta(ax, (2.2, 0.0), (2.2, 0.0), "0,1", 0, RAIO_GRANDE)
    ax.text(0.2, 0.0, "qualquer\nestado", ha="center", va="center", fontsize=9.5, color=COR,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=COR, lw=1.2, ls="--"))
    ax.add_patch(FancyArrowPatch((0.75, 0.0), (2.2 - RAIO_GRANDE, 0.0), arrowstyle="-|>", mutation_scale=12, color="#991b1b", lw=1.4))
    ax.text(1.25, 0.12, "símbolo fora de {0,1}", ha="center", va="bottom", fontsize=8.5, color="#991b1b")
    ax.text(1.2, -0.7, "estado de erro: nunca é final e não tem saída (só volta para ele)",
            ha="center", va="center", fontsize=8.5, color="#4b5563")
    ax.set_xlim(-1.0, 3.0)
    ax.set_ylim(-0.9, 1.0)


def main():
    produtos = construir_produtos()
    figura, eixos = plt.subplots(2, 3, figsize=(15, 7.6))

    dois = {0: (0.0, 0.0), 1: (2.2, 0.0)}
    desenha_automato(eixos[0][0], A, {"par0": dois[0], "impar0": dois[1]}, "A: número PAR de 0", {}, RAIO_GRANDE)
    desenha_automato(eixos[0][1], B, {"par1": dois[0], "impar1": dois[1]}, "B: número ÍMPAR de 1", {}, RAIO_GRANDE)
    for eixo in eixos[0][:2]:
        eixo.set_xlim(-1.0, 3.0)
        eixo.set_ylim(-0.9, 1.0)
    desenha_poco(eixos[0][2])

    quadrado = {"q0": (0.0, 1.5), "q1": (1.8, 1.5), "q2": (0.0, 0.0), "q3": (1.8, 0.0)}
    lados = {"q0": "acima", "q1": "acima", "q2": "abaixo", "q3": "abaixo"}
    legendas = {
        "inter": "A ∩ B  (final: q2)",
        "uniao": "A ∪ B  (finais: q0, q2, q3)",
        "dif": "A − B  (final: q0)",
    }
    for eixo, (chave, _) in zip(eixos[1], OPERACOES.items()):
        desenha_automato(eixo, produtos[chave], quadrado, legendas[chave], lados, RAIO_PEQUENO)
        eixo.set_xlim(-1.0, 3.0)
        eixo.set_ylim(-0.7, 2.2)

    figura.text(0.5, 0.012,
                "Círculo duplo = estado final; seta de fora = estado inicial. Nos produtos, cada estado é um par "
                "(estado de A, estado de B). As setas do poço não foram repetidas nos demais desenhos.",
                ha="center", fontsize=9, color="#4b5563")
    figura.tight_layout(rect=(0, 0.03, 1, 1))
    destino = RAIZ / "docs" / "diagrama.png"
    figura.savefig(destino, dpi=150, facecolor="white")
    print("gerado:", destino)


if __name__ == "__main__":
    main()
