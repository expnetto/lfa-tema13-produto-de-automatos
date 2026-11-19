"""Testes de unidade do AFD, do produto e da leitura de palavras."""
import contextlib
import io
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from afd import AFD, POCO  # noqa: E402
from automatos import A, B, construir_produtos  # noqa: E402
from main import interpreta_linha, main  # noqa: E402
from produto import OPERACOES, produto  # noqa: E402


def afd_ab():
    """Aceita palavras sobre {a,b} que terminam em 'a'; transições de 'b' omitidas em q1."""
    return AFD(
        estados=("q0", "q1"),
        alfabeto=("a", "b"),
        delta={("q0", "a"): "q1", ("q0", "b"): "q0", ("q1", "a"): "q1"},
        inicial="q0",
        finais={"q1"},
    )


class TestAFD(unittest.TestCase):
    def test_poco_entra_em_Q_e_na_tabela(self):
        self.assertIn(POCO, A.estados)
        self.assertEqual(A.delta[(POCO, "0")], POCO)
        self.assertEqual(A.delta[(POCO, "1")], POCO)
        self.assertIn(POCO, A.tabela())

    def test_transicao_omitida_vai_para_o_poco(self):
        afd = afd_ab()
        self.assertEqual(afd.delta[("q1", "b")], POCO)
        self.assertFalse(afd.executa("aab").aceita)
        self.assertTrue(afd.executa("bba").aceita)

    def test_simbolo_fora_do_alfabeto_vai_para_o_poco_e_fica(self):
        res = A.executa("0x0")
        self.assertFalse(res.aceita)
        self.assertEqual(res.caminho, ("par0", "impar0", POCO, POCO))

    def test_caminho_tem_um_estado_a_mais_que_a_palavra(self):
        res = A.executa("0110")
        self.assertEqual(len(res.caminho), 5)
        self.assertEqual(res.caminho[0], A.inicial)

    def test_palavra_vazia_usa_so_o_estado_inicial(self):
        res = A.executa("")
        self.assertTrue(res.aceita)
        self.assertEqual(res.caminho, ("par0",))

    def test_rejeita_construcoes_invalidas(self):
        base = dict(estados=("q0",), alfabeto=("a",), delta={("q0", "a"): "q0"},
                    inicial="q0", finais={"q0"})
        casos = {
            "inicial fora de Q": {**base, "inicial": "z"},
            "final fora de Q": {**base, "finais": {"z"}},
            "poço declarado à mão": {**base, "estados": ("q0", POCO)},
            "estado repetido": {**base, "estados": ("q0", "q0")},
            "símbolo com mais de um caractere": {**base, "alfabeto": ("ab",)},
            "transição para estado desconhecido": {**base, "delta": {("q0", "a"): "z"}},
            "transição de estado desconhecido": {**base, "delta": {("z", "a"): "q0"}},
            "transição com símbolo desconhecido": {**base, "delta": {("q0", "b"): "q0"}},
            "alfabeto vazio": {**base, "alfabeto": (), "delta": {}},
        }
        for nome, args in casos.items():
            with self.subTest(nome):
                with self.assertRaises(ValueError):
                    AFD(**args)

    def test_afd_nao_muda_depois_de_criado(self):
        with self.assertRaises(FrozenInstanceError):
            A.inicial = "impar0"
        with self.assertRaises(TypeError):
            A.delta[("par0", "0")] = "par0"


class TestProduto(unittest.TestCase):
    def setUp(self):
        self.produtos = construir_produtos()

    def test_quatro_estados_alcancaveis_mais_o_poco(self):
        for chave, afd in self.produtos.items():
            with self.subTest(chave):
                self.assertEqual(afd.estados, ("q0", "q1", "q2", "q3", POCO))

    def test_tabela_de_transicao_do_produto(self):
        esperado = {
            ("q0", "0"): "q1", ("q0", "1"): "q2",
            ("q1", "0"): "q0", ("q1", "1"): "q3",
            ("q2", "0"): "q3", ("q2", "1"): "q0",
            ("q3", "0"): "q2", ("q3", "1"): "q1",
        }
        for chave, afd in self.produtos.items():
            with self.subTest(chave):
                for par, destino in esperado.items():
                    self.assertEqual(afd.delta[par], destino)

    def test_conjuntos_de_finais(self):
        self.assertEqual(self.produtos["inter"].finais, {"q2"})
        self.assertEqual(self.produtos["uniao"].finais, {"q0", "q2", "q3"})
        self.assertEqual(self.produtos["dif"].finais, {"q0"})

    def test_rotulos_dizem_o_par_de_origem(self):
        self.assertEqual(self.produtos["inter"].rotulos["q0"], "(par0,par1)")
        self.assertEqual(self.produtos["inter"].rotulos["q3"], "(impar0,impar1)")

    def test_alfabetos_diferentes_sao_recusados(self):
        with self.assertRaises(ValueError):
            produto(A, afd_ab(), OPERACOES["inter"][1])

    def test_produto_com_transicoes_omitidas(self):
        # transições omitidas (q1 sem 'b') têm que cair no poço também dentro do produto
        a = afd_ab()
        inter = produto(a, a, OPERACOES["inter"][1])
        for palavra in ("a", "ba", "aba", "ab", "", "aab"):
            with self.subTest(palavra):
                self.assertEqual(inter.executa(palavra).aceita, a.executa(palavra).aceita)

    def test_produto_nao_altera_os_automatos_de_entrada(self):
        antes = (A.estados, dict(A.delta), A.finais)
        produto(A, B, OPERACOES["uniao"][1])
        self.assertEqual(antes, (A.estados, dict(A.delta), A.finais))


class TestEntrada(unittest.TestCase):
    def test_vazio_e_epsilon_viram_palavra_vazia(self):
        for linha in ("", "\n", "ε", "ε\n", "eps", "eps\r\n"):
            with self.subTest(linha):
                self.assertEqual(interpreta_linha(linha), "")

    def test_so_o_fim_de_linha_e_removido(self):
        self.assertEqual(interpreta_linha("0101\r\n"), "0101")
        self.assertEqual(interpreta_linha(" 01"), " 01")


def roda_main(argv, stdin_texto=None, teclado=None):
    """Roda main() capturando a saída. `teclado` simula o modo interativo."""
    saida = io.StringIO()
    entrada = io.StringIO(stdin_texto or "")
    entrada.isatty = lambda: teclado is not None
    with contextlib.redirect_stdout(saida), mock.patch("sys.stdin", entrada), \
            mock.patch("builtins.input", side_effect=teclado or []):
        codigo = main(argv)
    return codigo, saida.getvalue()


class TestProgramaPrincipal(unittest.TestCase):
    def test_palavras_na_linha_de_comando(self):
        codigo, texto = roda_main(["--sem-tabelas", "001", "ε"])
        self.assertEqual(codigo, 0)
        self.assertIn("palavra: 001", texto)
        self.assertIn("A ∩ B  aceita   q0 → q1 → q0 → q2", texto)
        self.assertIn("palavra: ε", texto)
        self.assertNotIn("δ", texto)

    def test_so_tabelas_imprime_os_cinco_automatos_e_nao_le_palavras(self):
        codigo, texto = roda_main(["--so-tabelas"], stdin_texto="001\n")
        self.assertEqual(codigo, 0)
        self.assertEqual(texto.count("δ"), 5)
        self.assertNotIn("palavra:", texto)

    def test_le_palavras_da_entrada_padrao_e_linha_vazia_e_epsilon(self):
        _, texto = roda_main(["--sem-tabelas"], stdin_texto="1\n\n0x1\n")
        self.assertEqual(texto.count("palavra:"), 3)
        self.assertIn("palavra: ε", texto)
        self.assertIn("q0 → q1 → poço → poço", texto)

    def test_modo_interativo_termina_com_sair(self):
        _, texto = roda_main(["--sem-tabelas"], teclado=["111", "sair", "000"])
        self.assertIn("palavra: 111", texto)
        self.assertNotIn("palavra: 000", texto)

    def test_modo_interativo_termina_no_fim_da_entrada(self):
        _, texto = roda_main(["--sem-tabelas"], teclado=["1", EOFError()])
        self.assertIn("palavra: 1", texto)


if __name__ == "__main__":
    unittest.main()
