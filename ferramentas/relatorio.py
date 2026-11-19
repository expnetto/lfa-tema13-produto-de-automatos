"""Gera docs/relatorio.pdf.

As tabelas e os resultados dos testes saem dos próprios autômatos de src/ e dos
arquivos de testes/, então o relatório não destoa do código. Só serve para refazer
o PDF (precisa de matplotlib e reportlab); o programa do trabalho não depende disso.

    python ferramentas/diagrama.py     # antes, se o diagrama mudou
    python ferramentas/relatorio.py
"""
import sys
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "testes"))

from afd import POCO  # noqa: E402
from automatos import A, B, construir_produtos  # noqa: E402
from produto import OPERACOES  # noqa: E402
from rodar_testes import TAMANHO_MAXIMO, conta, ler_casos, todas_as_palavras  # noqa: E402

AUTOR = "Eraldo Xavier P Netto"
CABECALHO = "Linguagens Formais e Autômatos · Trabalho prático · Prof. Dr. Leonardo Angelo · 2026.2"
ER_INTERSECAO = "(00+11+(01+10)(00+11)*(10+01))*(1+(01+10)(00+11)*0)"
ER_A = "(1+01*0)*"
ER_B = "0*10*(10*10*)*"
LARGURA = A4[0] - 4 * cm


def registra_fontes():
    pasta = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
    for nome, arquivo in (("Texto", "DejaVuSans.ttf"), ("Texto-B", "DejaVuSans-Bold.ttf"),
                          ("Mono", "DejaVuSansMono.ttf"), ("Mono-B", "DejaVuSansMono-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(nome, str(pasta / arquivo)))
    pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-B", italic="Texto", boldItalic="Texto-B")
    pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono", boldItalic="Mono-B")


def estilos():
    base = dict(fontName="Texto", fontSize=9.6, leading=14, textColor=colors.HexColor("#111827"))
    return {
        "titulo": ParagraphStyle("titulo", **{**base, "fontName": "Texto-B", "fontSize": 19, "leading": 24}),
        "sub": ParagraphStyle("sub", **{**base, "fontSize": 9, "textColor": colors.HexColor("#4b5563")}),
        "h1": ParagraphStyle("h1", **{**base, "fontName": "Texto-B", "fontSize": 12.5, "leading": 16,
                                      "spaceBefore": 14, "spaceAfter": 6, "textColor": colors.HexColor("#065f46")}),
        "p": ParagraphStyle("p", **base, alignment=TA_JUSTIFY, spaceAfter=6),
        "item": ParagraphStyle("item", **base, leftIndent=14, bulletIndent=3, spaceAfter=3, alignment=TA_JUSTIFY),
        "er": ParagraphStyle("er", **{**base, "fontName": "Mono", "fontSize": 8.8, "leading": 13, "leftIndent": 8,
                                      "backColor": colors.HexColor("#f3f4f6"), "borderPadding": 5, "spaceAfter": 10}),
        "nota": ParagraphStyle("nota", **{**base, "fontSize": 8.3, "leading": 11.5, "textColor": colors.HexColor("#4b5563"),
                                          "spaceAfter": 6}),
    }


def tabela(linhas, larguras, fonte=8.6, alinha_primeira="LEFT"):
    t = Table(linhas, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Texto"), ("FONTNAME", (0, 0), (-1, 0), "Texto-B"),
        ("FONTSIZE", (0, 0), (-1, -1), fonte), ("LEADING", (0, 0), (-1, -1), fonte + 3),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9ca3af")),
        ("ALIGN", (0, 0), (0, -1), alinha_primeira), ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ]))
    return t


def sn(valor):
    return "sim" if valor else "não"


def rotulo_estado(afd, estado):
    marca = ("→" if estado == afd.inicial else "") + ("*" if estado in afd.finais else "")
    return f"{marca} {estado}".strip()


def tabela_transicao(afd, colunas_extra=None):
    cabecalho = ["δ"] + list(afd.alfabeto)
    linhas = [cabecalho] + [[rotulo_estado(afd, q)] + [afd.delta[(q, a)] for a in afd.alfabeto] for q in afd.estados]
    return tabela(linhas, [3.2 * cm] + [2.4 * cm] * len(afd.alfabeto))


def secao_problema(e):
    produtos = construir_produtos()
    itens = [
        Paragraph("1. O problema", e["h1"]),
        Paragraph(
            "O tema 13 pede um programa que construa sozinho o <b>autômato produto</b> de dois AFDs. Os dois "
            "trabalham sobre o alfabeto Σ = {0, 1}. <b>A</b> reconhece as palavras com número <b>par de 0</b> "
            "(zero também é par, então a palavra vazia está em A). <b>B</b> reconhece as palavras com número "
            "<b>ímpar de 1</b>.", e["p"]),
        Paragraph(
            "O produto lê a palavra uma única vez e acompanha A e B ao mesmo tempo. Com as mesmas transições, "
            "mudando só quais estados são finais, saem três linguagens: <b>A ∩ B</b> (par de 0 e ímpar de 1), "
            "<b>A ∪ B</b> (pelo menos uma das duas) e <b>A − B</b> (está em A e não está em B, isto é, par de 0 e "
            "par de 1). Palavra com símbolo fora de {0,1} não pertence a nenhuma delas: vai para o poço.", e["p"]),
        Paragraph(
            "Exemplo: <font name='Mono'>001</font> tem dois 0 e um 1, então está em A e em B e portanto em A ∩ B. "
            "Já <font name='Mono'>01</font> tem um 0 (ímpar, fora de A) e um 1 (ímpar, dentro de B): fica de fora "
            "da interseção, mas entra na união. A tabela mostra as palavras obrigatórias do enunciado.", e["p"]),
    ]
    linhas = [["palavra", "# de 0", "# de 1", "A", "B", "A ∩ B", "A ∪ B", "A − B"]]
    for palavra in ("1", "001", "111", "0101", "01", "0011", ""):
        linhas.append([palavra or "ε", conta(palavra, "0"), conta(palavra, "1"), sn(A.aceita(palavra)), sn(B.aceita(palavra))]
                      + [sn(produtos[c].aceita(palavra)) for c in OPERACOES])
    return itens + [tabela(linhas, [2.4 * cm, 1.8 * cm, 1.8 * cm] + [1.9 * cm] * 5)]


def secao_modelagem(e):
    produtos = construir_produtos()
    inter, uniao, dif = (produtos[c] for c in ("inter", "uniao", "dif"))
    significado = {
        "par0": "li uma quantidade <b>par</b> de 0 (inclui nenhum)",
        "impar0": "li uma quantidade <b>ímpar</b> de 0",
        "par1": "li uma quantidade <b>par</b> de 1 (inclui nenhum)",
        "impar1": "li uma quantidade <b>ímpar</b> de 1",
    }
    itens = [
        Paragraph("2. Modelagem: o que cada estado significa", e["h1"]),
        Paragraph(
            "Para saber se o número de 0 é par não é preciso contar, basta lembrar a paridade. Duas palavras com a "
            "mesma paridade de 0 se comportam igual daqui para frente, então <b>dois estados bastam</b> em cada "
            "autômato. O 0 troca a paridade e o 1 deixa como está (em B é o contrário).", e["p"]),
    ]
    linhas = [["estado", "autômato", "significado", "papel"]]
    for afd, nome in ((A, "A"), (B, "B")):
        for q in afd.estados[:-1]:
            papel = ", ".join(x for x in ("inicial" if q == afd.inicial else "", "final" if q in afd.finais else "") if x) or "—"
            linhas.append([q, nome, Paragraph(significado[q], e["nota"]), papel])
    itens.append(tabela(linhas, [2.2 * cm, 2 * cm, 8 * cm, 2.8 * cm]))
    explicacao = Paragraph(
        "No produto, cada estado é um <b>par</b> (paridade dos 0, paridade dos 1) e cada símbolo mexe em só uma "
        "das metades: o 0 troca a paridade dos 0, o 1 troca a dos 1. Por isso o produto tem <b>4 estados, todos "
        "alcançáveis</b>, e as transições formam um quadrado em que toda seta tem volta com o mesmo símbolo. "
        "Os estados saem nomeados q0, q1, q2, q3 na ordem em que a busca em largura os encontra.", e["p"])
    linhas = [["estado", "par (A, B)", "significado", "A ∩ B", "A ∪ B", "A − B"]]
    meaning = {
        "q0": "0 par e 1 par (começo, e tudo que fecha em duplas)",
        "q1": "0 ímpar e 1 par",
        "q2": "0 par e 1 ímpar",
        "q3": "0 ímpar e 1 ímpar",
    }
    for q in inter.estados[:-1]:
        linhas.append([q, inter.rotulos[q], Paragraph(meaning[q], e["nota"]),
                       "final" if q in inter.finais else "—", "final" if q in uniao.finais else "—",
                       "final" if q in dif.finais else "—"])
    linhas.append([POCO, "—", Paragraph("símbolo fora de {0,1} já lido; não tem volta", e["nota"]), "—", "—", "—"])
    itens += [Spacer(1, 8), KeepTogether([explicacao, tabela(linhas, [1.7 * cm, 3.5 * cm, 5.6 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm])])]
    itens += [
        Spacer(1, 6),
        Paragraph(
            "A regra para ser final é a única diferença entre as operações: A ∩ B pede 0 par <i>e</i> 1 ímpar (só "
            "q2), A ∪ B pede 0 par <i>ou</i> 1 ímpar (q0, q2 e q3) e A − B pede 0 par e <i>não</i> 1 ímpar (só q0). "
            "No código isso é uma função <font name='Mono'>criterio(em_a, em_b)</font> passada para "
            "<font name='Mono'>produto()</font>.", e["p"]),
    ]
    return itens


def secao_formal(e):
    p = construir_produtos()["inter"]
    pares = "{par0, impar0} × {par1, impar1}"
    itens = [
        Paragraph("3. Definição formal", e["h1"]),
        Paragraph(
            "Todo AFD do programa é uma 5-tupla (Q, Σ, δ, q₀, F) em que Q já inclui o <b>poço</b>. "
            "Marcação nas tabelas: → estado inicial, * estado final. Em todos os autômatos "
            "δ(poço, a) = poço, e símbolo fora de Σ leva ao poço.", e["p"]),
        Paragraph(
            f"<b>A</b> = (Q<sub>A</sub>, Σ, δ<sub>A</sub>, par0, F<sub>A</sub>), com Q<sub>A</sub> = "
            f"{{par0, impar0, {POCO}}}, Σ = {{0, 1}} e F<sub>A</sub> = {{par0}}.", e["p"]),
        tabela_transicao(A), Spacer(1, 8),
        Paragraph(
            f"<b>B</b> = (Q<sub>B</sub>, Σ, δ<sub>B</sub>, par1, F<sub>B</sub>), com Q<sub>B</sub> = "
            f"{{par1, impar1, {POCO}}}, Σ = {{0, 1}} e F<sub>B</sub> = {{impar1}}.", e["p"]),
        tabela_transicao(B), Spacer(1, 8),
        Paragraph(
            f"<b>Produto</b> P = (Q, Σ, δ, q₀, F). Q ⊆ {pares}, mais o poço; "
            "δ((p, r), a) = (δ<sub>A</sub>(p, a), δ<sub>B</sub>(r, a)); q₀ = (par0, par1) = q0. "
            "Os estados alcançáveis são os quatro pares, nomeados q0 a q3 (tabela da seção 2). "
            "A tabela δ é a mesma nas três operações. Os pares que contêm o poço, como (poço, par1), não são alcançáveis a partir de q0 lendo símbolos de Σ, então não entram: o produto tem os 4 pares acima e, à parte, um único poço próprio, que só recebe símbolo de fora de Σ. São 4 + 1 = 5 linhas na tabela, e não 3 × 3 = 9. Tratar símbolo fora do alfabeto como erro (poço) é exigência do enunciado e vai além da definição teórica de AFD, em que δ é total só sobre Σ; sobre Σ = {0, 1} o autômato é um AFD completo comum.", e["p"]),
        tabela_transicao(p),
        Spacer(1, 6),
        Paragraph(
            "F<sub>∩</sub> = {q2} &nbsp;&nbsp; F<sub>∪</sub> = {q0, q2, q3} &nbsp;&nbsp; F<sub>−</sub> = {q0}. "
            "Em termos dos pares: F<sub>∩</sub> = {(par0, impar1)}, F<sub>∪</sub> = F<sub>A</sub> × Q<sub>B</sub> ∪ "
            "Q<sub>A</sub> × F<sub>B</sub> e F<sub>−</sub> = F<sub>A</sub> × (Q<sub>B</sub> ∖ F<sub>B</sub>), "
            "tudo restrito aos pares alcançáveis.", e["p"]),
    ]
    return itens


def secao_diagrama(e):
    largura = LARGURA
    imagem = Image(str(RAIZ / "docs" / "diagrama.png"), width=largura, height=largura * 7.6 / 15)
    return [KeepTogether([
        Paragraph("4. Diagrama", e["h1"]), imagem,
        Paragraph("A figura é gerada pelo script <font name='Mono'>ferramentas/diagrama.py</font> a partir da tabela "
                  "δ de cada AFD, então bate com o código. Também está em <font name='Mono'>docs/diagrama.png</font>.", e["nota"])])]


def linhas_de_teste(casos, produtos):
    saida = []
    for operacao, palavra, esperado in casos:
        obtido = "aceita" if produtos[operacao].aceita(palavra) else "rejeita"
        saida.append([OPERACOES[operacao][0], palavra or "ε", esperado, obtido, "ok" if obtido == esperado else "ERRO"])
    return saida


def tabela_dupla(linhas, e):
    """Põe duas colunas de resultados lado a lado para economizar páginas."""
    meio = (len(linhas) + 1) // 2
    esq, dir_ = linhas[:meio], linhas[meio:]
    dir_ += [[""] * 5] * (len(esq) - len(dir_))
    cab = ["op.", "palavra", "esperado", "obtido", "ok"]
    corpo = [cab + [""] + cab] + [a + [""] + b for a, b in zip(esq, dir_)]
    t = tabela(corpo, [1.2 * cm, 2.0 * cm, 1.5 * cm, 1.5 * cm, 0.9 * cm, 0.3 * cm, 1.2 * cm, 2.0 * cm, 1.5 * cm, 1.5 * cm, 0.9 * cm], fonte=7.6)
    t.setStyle(TableStyle([("BOX", (5, 0), (5, -1), 0, colors.white), ("GRID", (5, 0), (5, -1), 0, colors.white),
                           ("BACKGROUND", (5, 0), (5, 0), colors.white)]))
    return t


def secao_testes(e):
    produtos = construir_produtos()
    obrigatorias = ler_casos(RAIZ / "testes" / "obrigatorias.txt")
    proprias = ler_casos(RAIZ / "testes" / "proprias.txt")
    inter = [c for c in proprias if c[0] == "inter"]
    total_cruzado = sum(5 for _ in todas_as_palavras(TAMANHO_MAXIMO))
    qtd_palavras = total_cruzado // 5
    return [
        Paragraph("5. Testes", e["h1"]),
        Paragraph(
            "Tudo roda com <font name='Mono'>python testes/rodar_testes.py</font>, que mostra para cada palavra o "
            "resultado esperado, o obtido e se bateu, e termina com código de saída diferente de zero se algo falhar. "
            "Resultado atual: <b>todas passam</b>. As palavras estão nos arquivos "
            "<font name='Mono'>testes/obrigatorias.txt</font> e <font name='Mono'>testes/proprias.txt</font>.", e["p"]),
        KeepTogether([
            Paragraph(f"<b>Obrigatórias do enunciado</b> (A ∩ B): {len(obrigatorias)} de {len(obrigatorias)} passam.", e["p"]),
            tabela_dupla(linhas_de_teste(obrigatorias, produtos), e)]), Spacer(1, 8),
        KeepTogether([Paragraph(
            f"<b>Próprias para A ∩ B</b>: {sum(1 for c in inter if c[2] == 'aceita')} que devem ser aceitas e "
            f"{sum(1 for c in inter if c[2] == 'rejeita')} que devem ser rejeitadas. As bordas cobertas são a menor "
            "palavra aceita (<font name='Mono'>1</font>), um símbolo a mais (<font name='Mono'>1110</font>) e um a "
            "menos (<font name='Mono'>11</font>) em relação a <font name='Mono'>111</font>, símbolo fora do alfabeto no "
            "começo, no meio e no fim (<font name='Mono'>x001</font>, <font name='Mono'>0x01</font>, "
            "<font name='Mono'>12</font>) e a palavra vazia.", e["p"]),
            tabela_dupla(linhas_de_teste(inter, produtos), e)]), Spacer(1, 8),
        KeepTogether([
            Paragraph(f"<b>Próprias para A ∪ B e A − B</b> ({len(proprias) - len(inter)} palavras):", e["p"]),
            tabela_dupla(linhas_de_teste([c for c in proprias if c[0] != "inter"], produtos), e)]), Spacer(1, 8),
        Paragraph(
            f"<b>Verificação cruzada.</b> Além das listas, o script compara A, B e os três produtos com a definição "
            f"da linguagem (contagem de 0 e de 1 feita por laço simples) em <b>todas as {qtd_palavras} palavras de até "
            f"{TAMANHO_MAXIMO} símbolos</b>: {total_cruzado} comparações, nenhuma diferente. Há ainda testes de unidade "
            "do AFD (poço, transição omitida, validação), do produto (tabela, finais, alfabetos diferentes) e da leitura "
            "de palavras e do modo interativo.", e["p"]),
    ]


def secao_limitacoes(e):
    itens = [
        "<b>Poço explícito.</b> Q de todo AFD inclui o poço e a tabela δ mostra a linha dele. O caminho impresso "
        "continua listando o poço a cada símbolo depois de um erro, em vez de parar.",
        "<b>Só pares alcançáveis.</b> O produto é montado por busca em largura a partir de (q₀ de A, q₀ de B). "
        "Aqui os 4 pares são alcançáveis; em outros AFDs a tabela sairia menor que |Q<sub>A</sub>|·|Q<sub>B</sub>|. "
        "Não há minimização.",
        "<b>Mesmo alfabeto.</b> <font name='Mono'>produto()</font> recusa AFDs com alfabetos diferentes. Aceita "
        "quaisquer dois AFDs (inclusive com transições omitidas, que vão para o poço), mas o programa só traz A e B "
        "escritos à mão no código. Ler AFDs de arquivo (a generalização opcional do enunciado) ficou de fora.",
        "<b>Entrada.</b> Uma palavra por linha. Palavra vazia: linha em branco, <font name='Mono'>ε</font> ou "
        "<font name='Mono'>eps</font>. Só o fim de linha é removido: espaço conta como símbolo e a palavra é rejeitada.",
        "<b>A − B</b> é tomada dentro de {0,1}*. Palavra com símbolo de fora vai para o poço e é rejeitada nas três operações.",
        "<b>Sem atalhos.</b> Não há biblioteca de expressões regulares nem função pronta de contagem na solução; "
        "a leitura é feita pelo autômato, símbolo por símbolo. Só a biblioteca padrão do Python é usada "
        "(testado no Python 3.13 e 3.14). Matplotlib e reportlab servem apenas para refazer o diagrama e este PDF.",
    ]
    return [Paragraph("6. Limitações e decisões", e["h1"])] + [Paragraph(t, e["item"], bulletText="•") for t in itens]


def secao_er(e):
    return [
        Paragraph("7. Expressão regular equivalente", e["h1"]),
        Paragraph(
            "Na notação da disciplina (união <font name='Mono'>+</font>, concatenação por justaposição, estrela "
            "<font name='Mono'>*</font>), a interseção A ∩ B, isto é, as palavras com número par de 0 e ímpar de 1, "
            "é descrita por:", e["p"]),
        Paragraph(ER_INTERSECAO, e["er"]),
        Paragraph(
            "Ela foi obtida por <b>eliminação de estados</b> no AFD produto (tirando q1, q2, q3 e por fim q0) e "
            "confirmada contra o AFD em todas as palavras de até 16 símbolos (131.071 palavras), sem nenhuma "
            "diferença. A leitura dela é o caminho no autômato:", e["p"]),
        Paragraph(
            "• <font name='Mono'>(00+11+(01+10)(00+11)*(10+01))*</font> são as voltas que começam e terminam em "
            "q0 (palavras com número par de 0 e par de 1). <font name='Mono'>00</font> vai q0→q1→q0, "
            "<font name='Mono'>11</font> vai q0→q2→q0, e <font name='Mono'>(01+10)(00+11)*(10+01)</font> vai até q3 "
            "(por q1 ou por q2), dá voltas em q3 (<font name='Mono'>00</font> por q2, <font name='Mono'>11</font> "
            "por q1) e volta a q0.", e["item"]),
        Paragraph(
            "• <font name='Mono'>1+(01+10)(00+11)*0</font> é o trecho final, da última passagem por q0 até o "
            "estado final q2: ou o 1 direto, ou ir a q3, dar voltas e entrar em q2 pelo 0.", e["item"]),
        Spacer(1, 4),
        Paragraph(
            "A relação com o autômato é a do teorema de Kleene: cada estrela é um ciclo do diagrama, cada união é uma "
            "bifurcação e a concatenação é a sequência de trechos. O autômato dá a mesma linguagem com 4 estados "
            "porque guarda só a paridade, enquanto a expressão precisa escrever os caminhos. Para os componentes: "
            f"A = <font name='Mono'>{ER_A}</font> (os 0 vêm em pares, com qualquer quantidade de 1 entre os dois de "
            f"cada par) e B = <font name='Mono'>{ER_B}</font> (um 1 que sobra, mais pares de 1, com 0 em qualquer "
            "lugar). Ambas também foram conferidas até 16 símbolos. Para A ∪ B e A − B o caminho é o mesmo, "
            "trocando só os estados finais da eliminação; o relatório fica com a da interseção, que é a testada "
            "nas palavras obrigatórias.", e["p"]),
    ]


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Texto", 7.8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(2 * cm, 1.2 * cm, f"{AUTOR} · Tema 13: produto de autômatos")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"pág. {doc.page}")
    canvas.drawString(2 * cm, A4[1] - 1.1 * cm, CABECALHO)
    canvas.restoreState()


def main():
    registra_fontes()
    e = estilos()
    corpo = [
        Paragraph("Produto de autômatos", e["titulo"]),
        Paragraph(f"Tema 13 · AFD (construção) · Integrante: <b>{AUTOR}</b>", e["sub"]),
        Spacer(1, 4),
    ]
    for secao in (secao_problema, secao_modelagem, secao_formal, secao_diagrama, secao_testes, secao_limitacoes, secao_er):
        corpo += secao(e)
    destino = RAIZ / "docs" / "relatorio.pdf"
    SimpleDocTemplate(str(destino), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                      bottomMargin=1.8 * cm, title="Produto de autômatos (Tema 13)", author=AUTOR).build(
        corpo, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", destino)


if __name__ == "__main__":
    main()
