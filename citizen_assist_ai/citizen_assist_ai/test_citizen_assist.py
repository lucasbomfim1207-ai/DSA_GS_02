"""
Testes automatizados do Citizen Assist AI.
Executar:  python -m unittest -v test_citizen_assist
"""
import contextlib
import io
import json
import os
import random
import tempfile
import unittest
from unittest import mock

import main as app
from algoritmos import busca_por_texto, busca_sequencial_por_id
from gerenciador import GerenciadorServicos
from lista_encadeada import ListaEncadeada
from modelo import (
    ArquivoInvalidoError, IdDuplicadoError, NaoEncontradoError, Servico,
    ValidacaoError, normalizar, validar_id,
)


def novo(g, id, titulo="Serviço teste", categoria="Saúde"):
    return g.cadastrar(id, titulo, categoria, "Descrição de teste", "RG e CPF", "Local de teste")


def ids(lista):
    return [s.id for s in lista]


# ----------------------------------------------------------- LISTA ----
class TesteListaEncadeada(unittest.TestCase):
    def test_lista_vazia(self):
        l = ListaEncadeada()
        self.assertTrue(l.esta_vazia())
        self.assertEqual(len(l), 0)
        self.assertEqual(list(l), [])
        self.assertIsNone(l.remover(lambda x: True))
        self.assertIsNone(l.buscar(lambda x: True))

    def test_inserir_fim_e_inicio(self):
        l = ListaEncadeada()
        l.inserir_fim(2); l.inserir_fim(3); l.inserir_inicio(1)
        self.assertEqual(list(l), [1, 2, 3])
        self.assertEqual(len(l), 3)
        self.assertEqual(l.cauda.dado, 3)

    def test_remover_cabeca_meio_cauda_e_unico(self):
        l = ListaEncadeada()
        for x in [1, 2, 3, 4]:
            l.inserir_fim(x)
        self.assertEqual(l.remover(lambda x: x == 1), 1)   # cabeça
        self.assertEqual(l.remover(lambda x: x == 3), 3)   # meio
        self.assertEqual(l.remover(lambda x: x == 4), 4)   # cauda
        self.assertEqual(list(l), [2])
        self.assertEqual(l.cauda.dado, 2)
        self.assertEqual(l.remover(lambda x: x == 2), 2)   # único
        self.assertTrue(l.esta_vazia())
        self.assertIsNone(l.cauda)

    def test_inserir_apos_remover_cauda_mantem_integridade(self):
        l = ListaEncadeada()
        for x in [1, 2, 3]:
            l.inserir_fim(x)
        l.remover(lambda x: x == 3)
        l.inserir_fim(9)
        self.assertEqual(list(l), [1, 2, 9])
        self.assertEqual(len(l), 3)

    def test_remover_inexistente(self):
        l = ListaEncadeada(); l.inserir_fim(1)
        self.assertIsNone(l.remover(lambda x: x == 99))
        self.assertEqual(len(l), 1)


# -------------------------------------------------------- ORDENAÇÃO ----
class TesteOrdenacao(unittest.TestCase):
    def test_ordenar_numeros_aleatorios_contra_referencia(self):
        random.seed(7)
        for tamanho in (0, 1, 2, 3, 10, 101):
            valores = [random.randint(0, 50) for _ in range(tamanho)]
            l = ListaEncadeada()
            for v in valores:
                l.inserir_fim(v)
            l.ordenar(lambda x: x)
            self.assertEqual(list(l), sorted(valores))
            self.assertEqual(len(l), tamanho)
            if tamanho:
                self.assertEqual(l.cauda.dado, max(valores))
                self.assertIsNone(l.cauda.proximo)

    def test_ordenar_decrescente(self):
        l = ListaEncadeada()
        for v in [3, 1, 2]:
            l.inserir_fim(v)
        l.ordenar(lambda x: x, decrescente=True)
        self.assertEqual(list(l), [3, 2, 1])

    def test_estabilidade(self):
        l = ListaEncadeada()
        for par in [(1, "a"), (0, "b"), (1, "c"), (0, "d")]:
            l.inserir_fim(par)
        l.ordenar(lambda p: p[0])
        self.assertEqual(list(l), [(0, "b"), (0, "d"), (1, "a"), (1, "c")])

    def test_inserir_depois_de_ordenar(self):
        l = ListaEncadeada()
        for v in [5, 2, 9]:
            l.inserir_fim(v)
        l.ordenar(lambda x: x)
        l.inserir_fim(100)
        self.assertEqual(list(l), [2, 5, 9, 100])

    def test_ordenar_servicos_por_titulo_ignora_acento_e_caixa(self):
        g = GerenciadorServicos()
        novo(g, 1, "zebra")
        novo(g, 2, "Água tratada")
        novo(g, 3, "Brasão")
        self.assertEqual(ids(g.ordenar("titulo")), [2, 3, 1])

    def test_ordenar_servicos_por_id_e_categoria(self):
        g = GerenciadorServicos()
        novo(g, 30, "Serviço C", "Educação")
        novo(g, 10, "Serviço A", "Saúde")
        novo(g, 20, "Serviço B", "Documentação")
        self.assertEqual(ids(g.ordenar("id")), [10, 20, 30])
        self.assertEqual(ids(g.ordenar("id", decrescente=True)), [30, 20, 10])
        self.assertEqual(ids(g.ordenar("categoria")), [20, 30, 10])

    def test_ordenar_lista_vazia_e_criterio_invalido(self):
        g = GerenciadorServicos()
        self.assertEqual(g.ordenar("id"), [])
        with self.assertRaises(ValidacaoError):
            g.ordenar("preco")


# ------------------------------------------------------------ BUSCA ----
class TesteBusca(unittest.TestCase):
    def setUp(self):
        self.g = GerenciadorServicos()
        novo(self.g, 1, "Vacinação de rotina", "Saúde")
        novo(self.g, 2, "Emissão de identidade", "Documentação")
        novo(self.g, 3, "Consulta médica", "Saúde")

    def test_consultar_por_id_existente(self):
        self.assertEqual(self.g.consultar_por_id(2).titulo, "Emissão de identidade")
        self.assertEqual(self.g.consultar_por_id("3").id, 3)

    def test_consultar_id_inexistente(self):
        with self.assertRaises(NaoEncontradoError):
            self.g.consultar_por_id(999)

    def test_consultar_lista_vazia(self):
        with self.assertRaises(NaoEncontradoError):
            GerenciadorServicos().consultar_por_id(1)
        self.assertIsNone(busca_sequencial_por_id(ListaEncadeada(), 1))

    def test_pesquisa_por_titulo_parcial_sem_acento(self):
        self.assertEqual(ids(self.g.pesquisar("titulo", "vacinacao")), [1])
        self.assertEqual(ids(self.g.pesquisar("titulo", "  CONSULTA ")), [3])

    def test_pesquisa_por_categoria(self):
        self.assertEqual(ids(self.g.pesquisar("categoria", "saude")), [1, 3])

    def test_pesquisa_sem_resultado(self):
        self.assertEqual(self.g.pesquisar("titulo", "inexistente"), [])
        self.assertEqual(busca_por_texto(ListaEncadeada(), "titulo", "x"), [])

    def test_pesquisa_entradas_invalidas(self):
        with self.assertRaises(ValidacaoError):
            self.g.pesquisar("titulo", "   ")
        with self.assertRaises(ValidacaoError):
            self.g.pesquisar("local", "x")


# ------------------------------------------------------------- CRUD ----
class TesteCrud(unittest.TestCase):
    def setUp(self):
        self.g = GerenciadorServicos()

    def test_cadastrar_multiplos(self):
        for i in range(1, 6):
            novo(self.g, i)
        self.assertEqual(len(self.g), 5)
        self.assertEqual(ids(self.g.listar()), [1, 2, 3, 4, 5])

    def test_id_duplicado(self):
        novo(self.g, 1)
        with self.assertRaises(IdDuplicadoError):
            novo(self.g, 1, "Outro serviço")
        self.assertEqual(len(self.g), 1)

    def test_ids_invalidos(self):
        for invalido in ["abc", "", "-3", "0", "1.5", -1, 0, None, True, "²"]:
            with self.subTest(id=invalido):
                with self.assertRaises(ValidacaoError):
                    validar_id(invalido)
        self.assertEqual(len(self.g), 0)

    def test_campos_invalidos(self):
        casos = [
            ("", "Saúde", "Descrição ok", "RG", "Local ok"),            # título vazio
            ("Ab", "Saúde", "Descrição ok", "RG", "Local ok"),          # título curto
            ("Título ok", "Esportes", "Descrição ok", "RG", "Local"),   # categoria inválida
            ("Título ok", "Saúde", "   ", "RG", "Local ok"),            # descrição em branco
            ("Título ok", "Saúde", "Descrição ok", "", "Local ok"),     # requisitos vazios
            ("T" * 81, "Saúde", "Descrição ok", "RG", "Local ok"),      # título longo
        ]
        for caso in casos:
            with self.subTest(caso=caso):
                with self.assertRaises(ValidacaoError):
                    self.g.cadastrar(1, *caso)
        self.assertEqual(len(self.g), 0)

    def test_categoria_aceita_sem_acento_e_normaliza(self):
        s = self.g.cadastrar(1, "Teste", "saude", "Descrição ok", "RG", "Local ok")
        self.assertEqual(s.categoria, "Saúde")

    def test_atualizar(self):
        novo(self.g, 1)
        self.g.atualizar(1, titulo="Novo título", categoria="Educação")
        s = self.g.consultar_por_id(1)
        self.assertEqual((s.titulo, s.categoria), ("Novo título", "Educação"))

    def test_atualizar_invalido_preserva_registro(self):
        novo(self.g, 1, "Original", "Saúde")
        with self.assertRaises(ValidacaoError):
            self.g.atualizar(1, titulo="Título válido", categoria="Inexistente")
        s = self.g.consultar_por_id(1)
        self.assertEqual((s.titulo, s.categoria), ("Original", "Saúde"))

    def test_atualizar_inexistente_e_campo_proibido(self):
        with self.assertRaises(NaoEncontradoError):
            self.g.atualizar(5, titulo="Qualquer")
        novo(self.g, 1)
        with self.assertRaises(ValidacaoError):
            self.g.atualizar(1, id=2)
        with self.assertRaises(ValidacaoError):
            self.g.atualizar(1)

    def test_excluir_preserva_integridade(self):
        for i in (1, 2, 3):
            novo(self.g, i)
        self.g.excluir(2)
        self.assertEqual(ids(self.g.listar()), [1, 3])
        self.g.excluir(3)
        novo(self.g, 4)
        self.assertEqual(ids(self.g.listar()), [1, 4])
        self.assertEqual(len(self.g), 2)

    def test_excluir_inexistente_e_lista_vazia(self):
        with self.assertRaises(NaoEncontradoError):
            self.g.excluir(1)
        novo(self.g, 1)
        with self.assertRaises(NaoEncontradoError):
            self.g.excluir(2)
        self.g.excluir(1)
        with self.assertRaises(NaoEncontradoError):
            self.g.excluir(1)


# ----------------------------------------------------------- ANÁLISE ----
class TesteAnalise(unittest.TestCase):
    def test_analise_lista_vazia(self):
        r = GerenciadorServicos().analise()
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["mais_servicos"], [])
        self.assertTrue(all(v == 0 for v in r["por_categoria"].values()))

    def test_analise_com_dados(self):
        g = GerenciadorServicos()
        novo(g, 1, categoria="Saúde"); novo(g, 2, categoria="Saúde"); novo(g, 3, categoria="Educação")
        r = g.analise()
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["por_categoria"]["Saúde"], 2)
        self.assertEqual(r["mais_servicos"], ["Saúde"])
        self.assertAlmostEqual(r["percentual"]["Educação"], 100 / 3)
        self.assertIn("Documentação", r["sem_servicos"])


# ------------------------------------------------------ PERSISTÊNCIA ----
class TestePersistencia(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.dir.name, "dados.json")

    def tearDown(self):
        self.dir.cleanup()

    def test_salvar_e_carregar(self):
        g = GerenciadorServicos(self.caminho)
        novo(g, 1, "Acentuação çãé"); novo(g, 2)
        g2 = GerenciadorServicos(self.caminho)
        g2.carregar()
        self.assertEqual(ids(g2.listar()), [1, 2])
        self.assertEqual(g2.consultar_por_id(1).titulo, "Acentuação çãé")

    def test_arquivo_inexistente_ou_corrompido(self):
        g = GerenciadorServicos(self.caminho)
        with self.assertRaises(ArquivoInvalidoError):
            g.carregar()
        with open(self.caminho, "w", encoding="utf-8") as f:
            f.write("{ isto não é json")
        with self.assertRaises(ArquivoInvalidoError):
            g.carregar()

    def test_arquivo_com_registro_invalido_ou_duplicado_nao_altera_memoria(self):
        g = GerenciadorServicos(self.caminho)
        novo(g, 1)
        base = Servico(7, "Teste", "Saúde", "Descrição ok", "RG", "Local ok").para_dict()
        for conteudo in ({"servicos": [dict(base, categoria="X")]},
                         {"servicos": [base, base]},
                         {"servicos": "nada"}, [1, 2]):
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump(conteudo, f)
            with self.assertRaises(ArquivoInvalidoError):
                g.carregar()
        self.assertEqual(ids(g.listar()), [1])  # memória preservada após falhas de leitura


# --------------------------------------------------- MENU (integração) ----
def executar_menu(entradas):
    saida = io.StringIO()
    with mock.patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
        codigo = app.main(["--sem-persistencia", "--vazio"])
    return codigo, saida.getvalue()


class TesteMenu(unittest.TestCase):
    def test_opcao_inexistente_e_encerrar(self):
        codigo, texto = executar_menu(["9", "abc", "", "0"])
        self.assertEqual(codigo, 0)
        self.assertEqual(texto.count("Opção inexistente"), 3)
        self.assertIn("Até logo", texto)

    def test_operacoes_com_lista_vazia(self):
        _, texto = executar_menu(["2", "3", "4", "5", "6", "0"])
        self.assertEqual(texto.count("Não há serviços cadastrados"), 5)

    def test_cadastro_com_entradas_invalidas_e_id_duplicado(self):
        entradas = [
            "1", "abc", "-5", "10",                 # id inválido, inválido, válido
            "Vacina", "9", "1", "Descrição da vacina", "Caderneta", "UBS central",
            "1", "10", "11",                        # id duplicado (10) e depois 11
            "Água", "Esportes", "2", "Descrição água", "CPF", "Prefeitura",
            "7", "0",
        ]
        _, texto = executar_menu(entradas)
        self.assertIn("deve ser um número inteiro positivo", texto)
        self.assertIn("já está em uso", texto)
        self.assertIn("Escolha um número entre 1 e 5", texto)
        self.assertIn("Categoria inválida", texto)
        self.assertEqual(texto.count("cadastrado com sucesso"), 2)
        self.assertIn("Total de serviços: 2", texto)

    def test_consulta_inexistente_e_pesquisa_sem_resultado(self):
        entradas = [
            "1", "1", "Título ok", "1", "Descrição ok", "RG", "Local ok",
            "2", "77",
            "3", "1", "zzz",
            "3", "7",
            "0",
        ]
        _, texto = executar_menu(entradas)
        self.assertIn("Nenhum serviço encontrado com o ID 77", texto)
        self.assertIn("Nenhum serviço encontrado para 'zzz'", texto)
        self.assertIn("Opção inválida. Escolha 1 ou 2", texto)

    def test_excluir_com_cancelamento_e_confirmacao(self):
        entradas = [
            "1", "1", "Título ok", "1", "Descrição ok", "RG", "Local ok",
            "5", "1", "talvez", "n",
            "5", "1", "s",
            "0",
        ]
        _, texto = executar_menu(entradas)
        self.assertIn("Responda com 's' ou 'n'", texto)
        self.assertIn("Exclusão cancelada", texto)
        self.assertIn("Serviço 1 excluído", texto)

    def test_encerra_com_entrada_esgotada(self):
        saida = io.StringIO()
        with mock.patch("builtins.input", side_effect=EOFError), contextlib.redirect_stdout(saida):
            codigo = app.main(["--sem-persistencia", "--vazio"])
        self.assertEqual(codigo, 0)
        self.assertIn("Entrada encerrada", saida.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
