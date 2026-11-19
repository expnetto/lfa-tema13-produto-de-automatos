"""Os dois autômatos do tema 13, escritos à mão, e os três produtos.

A = palavras com número PAR de 0.     (os 1 não mudam nada)
B = palavras com número ÍMPAR de 1.   (os 0 não mudam nada)
"""
from typing import Dict

from afd import AFD
from produto import OPERACOES, produto

# O poço não é listado aqui: AFD acrescenta o estado POCO (src/afd.py) a Q e a δ.
A = AFD(
    estados=("par0", "impar0"),
    alfabeto=("0", "1"),
    delta={
        ("par0", "0"): "impar0",
        ("par0", "1"): "par0",
        ("impar0", "0"): "par0",
        ("impar0", "1"): "impar0",
    },
    inicial="par0",
    finais={"par0"},
    rotulos={"par0": "quantidade par de 0", "impar0": "quantidade ímpar de 0"},
)

B = AFD(
    estados=("par1", "impar1"),
    alfabeto=("0", "1"),
    delta={
        ("par1", "0"): "par1",
        ("par1", "1"): "impar1",
        ("impar1", "0"): "impar1",
        ("impar1", "1"): "par1",
    },
    inicial="par1",
    finais={"impar1"},
    rotulos={"par1": "quantidade par de 1", "impar1": "quantidade ímpar de 1"},
)


def construir_produtos() -> Dict[str, AFD]:
    """{'inter': AFD de A ∩ B, 'uniao': AFD de A ∪ B, 'dif': AFD de A - B}."""
    return {chave: produto(A, B, criterio) for chave, (_, criterio) in OPERACOES.items()}
