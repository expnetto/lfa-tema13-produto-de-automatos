"""AFD completo, com poço explícito.

O autômato é a 5-tupla (Q, Σ, δ, q0, F) guardada em campos. Quem lê a tabela
delta consegue desenhar o autômato. Nada aqui usa expressão regular.

O poço (POCO) é um estado de erro que sempre faz parte de Q:
  - símbolo fora do alfabeto leva ao poço;
  - transição que o autor não definiu leva ao poço;
  - do poço, qualquer símbolo volta para o poço (nunca é final).
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Tuple

POCO = "poço"


@dataclass(frozen=True)
class Resultado:
    """Resposta da execução de uma palavra: aceita ou não, e o caminho de estados."""
    aceita: bool
    caminho: Tuple[str, ...]


@dataclass(frozen=True)
class AFD:
    """Autômato finito determinístico (Q, Σ, δ, q0, F), imutável.

    estados   Q sem o poço (o poço é acrescentado ao final)
    alfabeto  Σ, cada símbolo com um caractere
    delta     δ como {(estado, símbolo): estado}; o que faltar vai para o poço
    inicial   q0
    finais    F
    rotulos   texto opcional por estado, usado só na impressão das tabelas
    """
    estados: Tuple[str, ...]
    alfabeto: Tuple[str, ...]
    delta: Mapping[Tuple[str, str], str]
    inicial: str
    finais: frozenset
    rotulos: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        estados, alfabeto = tuple(self.estados), tuple(self.alfabeto)
        if len(set(estados)) != len(estados):
            raise ValueError("estado repetido em Q")
        if POCO in estados:
            raise ValueError(f"'{POCO}' é acrescentado automaticamente, não declare em Q")
        if not alfabeto or len(set(alfabeto)) != len(alfabeto):
            raise ValueError("o alfabeto precisa ter ao menos um símbolo, sem repetir")
        if any(len(simbolo) != 1 for simbolo in alfabeto):
            raise ValueError("cada símbolo do alfabeto precisa ter um caractere")
        if self.inicial not in estados:
            raise ValueError(f"estado inicial {self.inicial!r} não está em Q")
        finais = frozenset(self.finais)
        if not finais <= set(estados):
            raise ValueError(f"estados finais fora de Q: {sorted(finais - set(estados))}")

        validos = set(estados) | {POCO}
        for (origem, simbolo), destino in self.delta.items():
            if origem not in estados or simbolo not in alfabeto:
                raise ValueError(f"transição fora de Q x Σ: ({origem!r}, {simbolo!r})")
            if destino not in validos:
                raise ValueError(f"transição leva a estado desconhecido: {destino!r}")

        completa = {(q, a): self.delta.get((q, a), POCO) for q in estados for a in alfabeto}
        completa.update({(POCO, a): POCO for a in alfabeto})

        object.__setattr__(self, "estados", estados + (POCO,))
        object.__setattr__(self, "alfabeto", alfabeto)
        object.__setattr__(self, "delta", MappingProxyType(completa))
        object.__setattr__(self, "finais", finais)
        object.__setattr__(self, "rotulos", MappingProxyType(dict(self.rotulos)))

    def passo(self, estado: str, simbolo: str) -> str:
        """δ(estado, símbolo); símbolo fora do alfabeto vai para o poço."""
        if simbolo not in self.alfabeto:
            return POCO
        return self.delta[(estado, simbolo)]

    def executa(self, palavra: str) -> Resultado:
        """Lê a palavra símbolo por símbolo e devolve aceita/rejeita e o caminho."""
        atual = self.inicial
        caminho = [atual]
        for simbolo in palavra:
            atual = self.passo(atual, simbolo)
            caminho.append(atual)
        return Resultado(atual in self.finais, tuple(caminho))

    def aceita(self, palavra: str) -> bool:
        return self.executa(palavra).aceita

    def tabela(self) -> str:
        """Tabela de transição em texto. '->' marca o inicial e '*' os finais."""
        def nome(estado: str) -> str:
            marca = ("->" if estado == self.inicial else "  ") + ("*" if estado in self.finais else " ")
            rotulo = self.rotulos.get(estado)
            return f"{marca} {estado}" + (f" = {rotulo}" if rotulo else "")

        linhas = [[nome(q)] + [self.delta[(q, a)] for a in self.alfabeto] for q in self.estados]
        cabecalho = ["δ"] + list(self.alfabeto)
        larguras = [max(len(linha[i]) for linha in [cabecalho] + linhas) for i in range(len(cabecalho))]
        formata = lambda linha: " | ".join(celula.ljust(l) for celula, l in zip(linha, larguras)).rstrip()
        return "\n".join([formata(cabecalho), "-+-".join("-" * l for l in larguras)] + [formata(l) for l in linhas])
