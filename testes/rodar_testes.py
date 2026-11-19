"""Roda todos os testes de uma vez.

    python testes/rodar_testes.py

Para cada palavra mostra o resultado esperado, o obtido e se bateu.
Termina com código 0 se tudo passou e 1 se alguma coisa falhou.
"""
import io
import itertools
import sys
import unittest
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / "src"))
sys.path.insert(0, str(PASTA))

from automatos import A, B, construir_produtos  # noqa: E402
from main import interpreta_linha  # noqa: E402
from produto import OPERACOES  # noqa: E402

TAMANHO_MAXIMO = 10  # a verificação cruzada cobre todas as palavras até esse tamanho
MINIMO_ACEITAS = 10
MINIMO_REJEITADAS = 10


def ler_casos(arquivo):
    """Devolve [(operação, palavra, esperado)] do arquivo de casos."""
    casos = []
    for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
        conteudo = linha.split("#", 1)[0].split()
        if not conteudo:
            continue
        if len(conteudo) != 3 or conteudo[2] not in ("aceita", "rejeita"):
            raise ValueError(f"{arquivo.name}:{numero}: linha mal formada: {linha!r}")
        if conteudo[0] not in OPERACOES:
            raise ValueError(f"{arquivo.name}:{numero}: operação desconhecida: {conteudo[0]!r}")
        casos.append((conteudo[0], interpreta_linha(conteudo[1]), conteudo[2]))
    return casos


def rodar_casos(titulo, casos, produtos):
    """Imprime a tabela esperado x obtido e devolve quantos casos falharam."""
    print(f"\n== {titulo} ==")
    print(f"{'operação':<9}{'palavra':<14}{'esperado':<10}{'obtido':<10}ok")
    falhas = 0
    for operacao, palavra, esperado in casos:
        obtido = "aceita" if produtos[operacao].executa(palavra).aceita else "rejeita"
        bateu = obtido == esperado
        falhas += not bateu
        print(f"{operacao:<9}{palavra or 'ε':<14}{esperado:<10}{obtido:<10}{'ok' if bateu else 'ERRO'}")
    print(f"-> {len(casos) - falhas}/{len(casos)} passaram")
    return falhas


def confere_quantidade(casos):
    """O enunciado pede 10 aceitas e 10 rejeitadas próprias para A ∩ B."""
    inter = [esperado for operacao, _, esperado in casos if operacao == "inter"]
    aceitas, rejeitadas = inter.count("aceita"), inter.count("rejeita")
    ok = aceitas >= MINIMO_ACEITAS and rejeitadas >= MINIMO_REJEITADAS
    print(f"\nA ∩ B próprias: {aceitas} aceitas e {rejeitadas} rejeitadas "
          f"(mínimo {MINIMO_ACEITAS} e {MINIMO_REJEITADAS}) -> {'ok' if ok else 'ERRO'}")
    return 0 if ok else 1


def todas_as_palavras(tamanho_maximo):
    for tamanho in range(tamanho_maximo + 1):
        for letras in itertools.product("01", repeat=tamanho):
            yield "".join(letras)


def conta(palavra, simbolo):
    total = 0
    for letra in palavra:
        if letra == simbolo:
            total += 1
    return total


def verificacao_cruzada(produtos):
    """Compara o produto com a definição da linguagem, palavra por palavra."""
    print(f"\n== verificação cruzada: todas as palavras de até {TAMANHO_MAXIMO} símbolos ==")
    falhas = total = 0
    for palavra in todas_as_palavras(TAMANHO_MAXIMO):
        em_a = conta(palavra, "0") % 2 == 0
        em_b = conta(palavra, "1") % 2 == 1
        esperado = {
            "A": em_a, "B": em_b,
            "inter": em_a and em_b, "uniao": em_a or em_b, "dif": em_a and not em_b,
        }
        obtido = {
            "A": A.executa(palavra).aceita, "B": B.executa(palavra).aceita,
            **{chave: afd.executa(palavra).aceita for chave, afd in produtos.items()},
        }
        for chave in esperado:
            total += 1
            if esperado[chave] != obtido[chave]:
                falhas += 1
                print(f"ERRO: {chave} em {palavra or 'ε'}: esperado {esperado[chave]}, obtido {obtido[chave]}")
    print(f"-> {total - falhas}/{total} comparações iguais")
    return falhas


def testes_de_unidade():
    print("\n== testes de unidade ==")
    fluxo = io.StringIO()
    resultado = unittest.TextTestRunner(stream=fluxo, verbosity=0).run(
        unittest.defaultTestLoader.discover(str(PASTA), pattern="test_*.py"))
    if not resultado.wasSuccessful():
        print(fluxo.getvalue())
    print(f"-> {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}"
          f"/{resultado.testsRun} passaram")
    return len(resultado.failures) + len(resultado.errors)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    produtos = construir_produtos()
    obrigatorias = ler_casos(PASTA / "obrigatorias.txt")
    assert len(obrigatorias) == 7, "o enunciado traz 7 palavras obrigatórias"
    proprias = ler_casos(PASTA / "proprias.txt")

    falhas = rodar_casos("palavras obrigatórias do enunciado (A ∩ B)", obrigatorias, produtos)
    falhas += rodar_casos("palavras próprias (bordas, símbolos fora do alfabeto, vazia)", proprias, produtos)
    falhas += confere_quantidade(proprias)
    falhas += verificacao_cruzada(produtos)
    falhas += testes_de_unidade()

    print("\nRESULTADO:", "tudo passou" if falhas == 0 else f"{falhas} falha(s)")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
