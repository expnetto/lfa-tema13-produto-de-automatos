"""Tema 13: produto de autômatos (A = par de 0, B = ímpar de 1).

    python src/main.py                    mostra as tabelas e lê palavras (uma por linha)
    python src/main.py 001 0101 ε         testa as palavras dadas
    python src/main.py --sem-tabelas 001  só o resultado
    python src/main.py --so-tabelas       só as tabelas

Palavra vazia: linha em branco, ε ou eps. No modo interativo, 'sair' termina (também
Ctrl+D no Linux/macOS, ou Ctrl+Z e Enter no Windows).
"""
import argparse
import sys
from typing import Dict, List, Optional

from afd import AFD
from automatos import A, B, construir_produtos
from produto import OPERACOES

VAZIA = ("", "ε", "eps")
SETA = " → "


def interpreta_linha(linha: str) -> str:
    """Tira só o fim de linha. Espaço e qualquer outro símbolo contam como símbolo da palavra."""
    palavra = linha.rstrip("\r\n")
    return "" if palavra in VAZIA else palavra


def imprime_tabelas(produtos: Dict[str, AFD]) -> None:
    print("AFD A: número PAR de 0")
    print(A.tabela())
    print("\nAFD B: número ÍMPAR de 1")
    print(B.tabela())
    for chave, (nome, _) in OPERACOES.items():
        print(f"\nAFD produto {nome}")
        print(produtos[chave].tabela())
    print("\n'->' estado inicial, '*' estado final. Símbolo fora de {0,1} leva ao poço.")


def imprime_resultado(rotulo: str, afd: AFD, palavra: str) -> None:
    resultado = afd.executa(palavra)
    veredito = "aceita " if resultado.aceita else "rejeita"
    print(f"  {rotulo:<6} {veredito}  {SETA.join(resultado.caminho)}")


def processa(palavra: str, produtos: Dict[str, AFD]) -> None:
    print(f"\npalavra: {palavra or 'ε'}")
    imprime_resultado("A", A, palavra)
    imprime_resultado("B", B, palavra)
    for chave, (nome, _) in OPERACOES.items():
        imprime_resultado(nome, produtos[chave], palavra)


def le_do_teclado(produtos: Dict[str, AFD]) -> None:
    print("\nDigite uma palavra por linha (linha em branco = ε, 'sair' termina).")
    while True:
        try:
            linha = input("palavra> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if linha.rstrip("\r\n") == "sair":
            return
        processa(interpreta_linha(linha), produtos)


def main(argv: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        # utf-8-sig tira o BOM de arquivo redirecionado; byte inválido vira U+FFFD (fora do alfabeto: poço)
        sys.stdin.reconfigure(encoding="utf-8-sig", errors="replace")

    parser = argparse.ArgumentParser(description="Produto de autômatos (tema 13).")
    parser.add_argument("palavras", nargs="*", help="palavras a testar (ε ou eps = vazia)")
    parser.add_argument("--sem-tabelas", action="store_true", help="não imprime as tabelas")
    parser.add_argument("--so-tabelas", action="store_true", help="imprime as tabelas e termina")
    args = parser.parse_args(argv)

    produtos = construir_produtos()
    if not args.sem_tabelas:
        imprime_tabelas(produtos)
    if args.so_tabelas:
        return 0

    if args.palavras:
        for palavra in args.palavras:
            processa(interpreta_linha(palavra), produtos)
    elif sys.stdin.isatty():
        le_do_teclado(produtos)
    else:
        for linha in sys.stdin:
            processa(interpreta_linha(linha), produtos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
