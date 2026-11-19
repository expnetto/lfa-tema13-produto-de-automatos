"""Construção do produto de dois AFDs.

O produto roda os dois autômatos ao mesmo tempo: cada estado dele é um par
(estado de A, estado de B) e um símbolo move os dois juntos. Só entram os pares
alcançáveis a partir de (q0 de A, q0 de B). O que muda entre interseção, união
e diferença é apenas quais pares são finais.
"""
from collections import deque
from typing import Callable

from afd import AFD

# nome para exibição e critério: recebe (A aceita?, B aceita?) e diz se o par é final
OPERACOES = {
    "inter": ("A ∩ B", lambda em_a, em_b: em_a and em_b),
    "uniao": ("A ∪ B", lambda em_a, em_b: em_a or em_b),
    "dif": ("A − B", lambda em_a, em_b: em_a and not em_b),
}


def produto(a: AFD, b: AFD, criterio: Callable[[bool, bool], bool]) -> AFD:
    """Monta o AFD produto de `a` e `b`. Os estados novos se chamam q0, q1, ...

    Exige o mesmo alfabeto nos dois. `criterio(em_a, em_b)` decide, para cada
    par, se ele é final.
    """
    if set(a.alfabeto) != set(b.alfabeto):
        raise ValueError(f"alfabetos diferentes: {a.alfabeto} e {b.alfabeto}")

    inicial = (a.inicial, b.inicial)
    nomes = {inicial: "q0"}
    delta = {}
    fila = deque([inicial])
    while fila:
        par = fila.popleft()
        for simbolo in a.alfabeto:
            destino = (a.passo(par[0], simbolo), b.passo(par[1], simbolo))
            if destino not in nomes:
                nomes[destino] = f"q{len(nomes)}"
                fila.append(destino)
            delta[(nomes[par], simbolo)] = nomes[destino]

    return AFD(
        estados=tuple(nomes.values()),
        alfabeto=a.alfabeto,
        delta=delta,
        inicial="q0",
        finais=frozenset(nome for (qa, qb), nome in nomes.items()
                         if criterio(qa in a.finais, qb in b.finais)),
        rotulos={nome: f"({qa},{qb})" for (qa, qb), nome in nomes.items()},
    )
