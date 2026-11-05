#!/usr/bin/env python3
"""
Citizen Assist AI - Global Solution 2026.2 (Data Structures and Algorithms)

Menu interativo em terminal para cadastrar, consultar, pesquisar, atualizar,
excluir, ordenar e analisar serviços públicos ao cidadão.

Uso:
    python main.py                      # usa/gera dados_servicos.json
    python main.py --sem-persistencia   # não grava arquivo (demonstração)
    python main.py --vazio              # começa sem os registros de exemplo
"""
import argparse
import os
import sys

from dados_exemplo import carregar_exemplos
from gerenciador import GerenciadorServicos
from modelo import (
    CATEGORIAS, ArquivoInvalidoError, ErroDoSistema, ValidacaoError,
    validar_categoria, validar_id, validar_texto,
)

LARGURA = 78
ARQUIVO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_servicos.json")


# --------------------------------------------------------- entrada/saída --
def entrada(prompt):
    valor = input(prompt).strip()
    if not sys.stdin.isatty():  # ao usar redirecionamento, ecoa a resposta
        print(valor)
    return valor


def aviso(texto):
    print(f"  [!] {texto}")


def ok(texto):
    print(f"  [OK] {texto}")


def titulo(texto):
    print("\n" + "-" * LARGURA)
    print(texto)
    print("-" * LARGURA)


def cortar(texto, tamanho):
    return texto if len(texto) <= tamanho else texto[: tamanho - 3] + "..."


def ler_id(prompt):
    while True:
        try:
            return validar_id(entrada(prompt))
        except ValidacaoError as erro:
            aviso(str(erro))


def ler_campo(rotulo, validador, atual=None):
    """Lê e valida um campo. Se `atual` for informado, Enter mantém o valor."""
    while True:
        dica = f" [Enter mantém: {cortar(atual, 40)}]" if atual is not None else ""
        bruto = entrada(f"{rotulo}{dica}: ")
        if atual is not None and bruto == "":
            return atual
        try:
            return validador(bruto)
        except ValidacaoError as erro:
            aviso(str(erro))


def _categoria_por_menu(valor):
    if valor.isascii() and valor.isdigit():
        indice = int(valor)
        if 1 <= indice <= len(CATEGORIAS):
            return CATEGORIAS[indice - 1]
        raise ValidacaoError(f"Escolha um número entre 1 e {len(CATEGORIAS)}.")
    return validar_categoria(valor)


def ler_categoria(atual=None):
    for i, categoria in enumerate(CATEGORIAS, start=1):
        print(f"    {i} - {categoria}")
    return ler_campo("Categoria (número ou nome)", _categoria_por_menu, atual)


def confirmar(pergunta):
    while True:
        resposta = entrada(f"{pergunta} (s/n): ").lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        aviso("Responda com 's' ou 'n'.")


def mostrar_servico(s):
    print(f"  ID.............: {s.id}")
    print(f"  Título.........: {s.titulo}")
    print(f"  Categoria......: {s.categoria}")
    print(f"  Descrição......: {s.descricao}")
    print(f"  Requisitos.....: {s.requisitos}")
    print(f"  Local..........: {s.local}")


def mostrar_tabela(servicos):
    print(f"{'ID':>5}  {'Título':<34}  {'Categoria':<19}  {'Local':<12}")
    print("-" * LARGURA)
    for s in servicos:
        print(f"{s.id:>5}  {cortar(s.titulo, 34):<34}  {s.categoria:<19}  {cortar(s.local, 12):<12}")
    print(f"\n  Total exibido: {len(servicos)}")


# ----------------------------------------------------------------- ações --
def acao_cadastrar(g):
    titulo("CADASTRAR NOVO SERVIÇO")
    while True:
        identificador = ler_id("Identificador (inteiro positivo): ")
        if g.existe(identificador):
            aviso(f"O ID {identificador} já está em uso. Informe outro.")
        else:
            break
    nome = ler_campo("Título", lambda v: validar_texto("titulo", v))
    categoria = ler_categoria()
    descricao = ler_campo("Descrição", lambda v: validar_texto("descricao", v))
    requisitos = ler_campo("Requisitos (documentos/condições)", lambda v: validar_texto("requisitos", v))
    local = ler_campo("Local de atendimento", lambda v: validar_texto("local", v))
    servico = g.cadastrar(identificador, nome, categoria, descricao, requisitos, local)
    ok(f"Serviço {servico.id} cadastrado com sucesso.")


def acao_consultar(g):
    titulo("CONSULTAR SERVIÇO POR ID")
    if len(g) == 0:
        aviso("Não há serviços cadastrados.")
        return
    servico = g.consultar_por_id(ler_id("ID do serviço: "))
    mostrar_servico(servico)


def acao_pesquisar(g):
    titulo("PESQUISAR SERVIÇOS")
    if len(g) == 0:
        aviso("Não há serviços cadastrados.")
        return
    print("  1 - Por título\n  2 - Por categoria")
    opcao = entrada("Pesquisar por: ")
    campos = {"1": "titulo", "2": "categoria"}
    if opcao not in campos:
        aviso("Opção inválida. Escolha 1 ou 2.")
        return
    termo = entrada("Termo (trecho do texto): ")
    resultado = g.pesquisar(campos[opcao], termo)
    if not resultado:
        aviso(f"Nenhum serviço encontrado para '{termo}'.")
        if campos[opcao] == "categoria":
            print("  Categorias disponíveis: " + ", ".join(CATEGORIAS))
        return
    print(f"\n  {len(resultado)} resultado(s) encontrado(s):\n")
    mostrar_tabela(resultado)


def acao_atualizar(g):
    titulo("ATUALIZAR SERVIÇO")
    if len(g) == 0:
        aviso("Não há serviços cadastrados.")
        return
    servico = g.consultar_por_id(ler_id("ID do serviço a atualizar: "))
    mostrar_servico(servico)
    print("\n  Pressione Enter para manter o valor atual de cada campo.")
    novos = {
        "titulo": ler_campo("Título", lambda v: validar_texto("titulo", v), servico.titulo),
        "categoria": ler_categoria(servico.categoria),
        "descricao": ler_campo("Descrição", lambda v: validar_texto("descricao", v), servico.descricao),
        "requisitos": ler_campo("Requisitos", lambda v: validar_texto("requisitos", v), servico.requisitos),
        "local": ler_campo("Local de atendimento", lambda v: validar_texto("local", v), servico.local),
    }
    alterados = {c: v for c, v in novos.items() if getattr(servico, c) != v}
    if not alterados:
        aviso("Nenhuma alteração informada.")
        return
    g.atualizar(servico.id, **alterados)
    ok(f"Serviço {servico.id} atualizado (campos: {', '.join(alterados)}).")


def acao_excluir(g):
    titulo("EXCLUIR SERVIÇO")
    if len(g) == 0:
        aviso("Não há serviços cadastrados.")
        return
    servico = g.consultar_por_id(ler_id("ID do serviço a excluir: "))
    mostrar_servico(servico)
    if confirmar("Confirma a exclusão?"):
        g.excluir(servico.id)
        ok(f"Serviço {servico.id} excluído.")
    else:
        print("  Exclusão cancelada.")


def acao_listar(g):
    titulo("LISTAR / ORDENAR SERVIÇOS (Merge Sort)")
    if len(g) == 0:
        aviso("Não há serviços cadastrados.")
        return
    print("  Critério:  1 - ID   2 - Título   3 - Categoria")
    criterios = {"1": "id", "2": "titulo", "3": "categoria"}
    escolha = entrada("Ordenar por: ")
    if escolha not in criterios:
        aviso("Critério inválido. Escolha 1, 2 ou 3.")
        return
    print("  Sentido:   1 - Crescente   2 - Decrescente")
    sentido = entrada("Sentido: ")
    if sentido not in ("1", "2"):
        aviso("Sentido inválido. Escolha 1 ou 2.")
        return
    registros = g.ordenar(criterios[escolha], decrescente=(sentido == "2"))
    print()
    mostrar_tabela(registros)


def acao_analise(g):
    titulo("ANÁLISE DOS SERVIÇOS CADASTRADOS")
    resumo = g.analise()
    print(f"  Total de serviços: {resumo['total']}\n")
    for categoria, quantidade in resumo["por_categoria"].items():
        barra = "#" * quantidade
        pct = resumo["percentual"][categoria]
        print(f"  {categoria:<19} {quantidade:>3}  ({pct:5.1f}%)  {barra}")
    if resumo["total"] == 0:
        print("\n  Nenhum serviço cadastrado ainda.")
        return
    print("\n  Categoria(s) com mais serviços: " + ", ".join(resumo["mais_servicos"]))
    if resumo["sem_servicos"]:
        print("  Categoria(s) sem serviços:      " + ", ".join(resumo["sem_servicos"]))


ACOES = {
    "1": acao_cadastrar,
    "2": acao_consultar,
    "3": acao_pesquisar,
    "4": acao_atualizar,
    "5": acao_excluir,
    "6": acao_listar,
    "7": acao_analise,
}


def exibir_menu():
    print("\n" + "=" * LARGURA)
    print("CITIZEN ASSIST AI - Serviços e orientações ao cidadão".center(LARGURA))
    print("=" * LARGURA)
    print("  1 - Cadastrar serviço")
    print("  2 - Consultar serviço por ID")
    print("  3 - Pesquisar (título ou categoria)")
    print("  4 - Atualizar serviço")
    print("  5 - Excluir serviço")
    print("  6 - Listar / ordenar serviços")
    print("  7 - Apresentar análise")
    print("  0 - Encerrar")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Citizen Assist AI (GS 2026.2 - DSA)")
    parser.add_argument("--arquivo", default=ARQUIVO_PADRAO, help="arquivo JSON de dados")
    parser.add_argument("--sem-persistencia", action="store_true", help="não ler/gravar arquivo")
    parser.add_argument("--vazio", action="store_true", help="não carregar registros de exemplo")
    args = parser.parse_args(argv)

    if not sys.stdout.isatty():
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    arquivo = None if args.sem_persistencia else args.arquivo
    g = GerenciadorServicos(arquivo)
    try:
        if arquivo and os.path.exists(arquivo):
            g.carregar()
            print(f"Dados carregados de {arquivo} ({len(g)} serviço(s)).")
        elif not args.vazio:
            carregar_exemplos(g)
            print(f"Carregados {len(g)} serviços de exemplo.")
    except ArquivoInvalidoError as erro:
        aviso(f"{erro}")
        aviso("O arquivo foi preservado; esta sessão não gravará alterações nele.")
        g = GerenciadorServicos(None)
        arquivo = None

    try:
        while True:
            exibir_menu()
            opcao = entrada("Escolha uma opção: ")
            if opcao == "0":
                break
            acao = ACOES.get(opcao)
            if acao is None:
                aviso("Opção inexistente. Digite um número de 0 a 7.")
                continue
            try:
                acao(g)
            except ErroDoSistema as erro:
                aviso(str(erro))
            except OSError as erro:
                aviso(f"Falha ao gravar o arquivo: {erro}")
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada encerrada.")

    if arquivo:
        try:
            g.salvar()
            print(f"Dados salvos em {arquivo}.")
        except OSError as erro:
            aviso(f"Não foi possível salvar: {erro}")
    print("Encerrando o Citizen Assist AI. Até logo!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
