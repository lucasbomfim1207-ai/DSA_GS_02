"""
gerenciador.py - Regras de negócio do Citizen Assist AI (sem entrada/saída).

Separar as regras da interface permite testar tudo automaticamente.
"""
import json
import os

from algoritmos import busca_por_texto, busca_sequencial_por_id
from lista_encadeada import ListaEncadeada
from modelo import (
    CATEGORIAS, ArquivoInvalidoError, IdDuplicadoError, NaoEncontradoError,
    Servico, ValidacaoError, normalizar, validar_id, validar_texto,
)

CHAVES_ORDENACAO = {
    "id": lambda s: s.id,
    "titulo": lambda s: (normalizar(s.titulo), s.id),
    "categoria": lambda s: (normalizar(s.categoria), normalizar(s.titulo), s.id),
}
CAMPOS_BUSCA = ("titulo", "categoria")


class GerenciadorServicos:
    def __init__(self, arquivo=None):
        self.lista = ListaEncadeada()
        self.arquivo = arquivo

    def __len__(self):
        return len(self.lista)

    # ------------------------------------------------------------- CRUD --
    def existe(self, identificador):
        return busca_sequencial_por_id(self.lista, identificador) is not None

    def cadastrar(self, id, titulo, categoria, descricao, requisitos, local):
        servico = Servico(id, titulo, categoria, descricao, requisitos, local)
        if self.existe(servico.id):
            raise IdDuplicadoError(f"Já existe um serviço com o ID {servico.id}.")
        self.lista.inserir_fim(servico)
        self._autosalvar()
        return servico

    def consultar_por_id(self, identificador):
        identificador = validar_id(identificador)
        servico = busca_sequencial_por_id(self.lista, identificador)
        if servico is None:
            raise NaoEncontradoError(f"Nenhum serviço encontrado com o ID {identificador}.")
        return servico

    def pesquisar(self, campo, termo):
        """Pesquisa por trecho em 'titulo' ou 'categoria'. [] se nada achar."""
        if campo not in CAMPOS_BUSCA:
            raise ValidacaoError("Pesquisa disponível apenas por título ou categoria.")
        if not isinstance(termo, str) or not normalizar(termo):
            raise ValidacaoError("Informe um termo de pesquisa.")
        return busca_por_texto(self.lista, campo, termo)

    def atualizar(self, identificador, **campos):
        servico = self.consultar_por_id(identificador)
        if not campos:
            raise ValidacaoError("Nenhum campo informado para atualização.")
        servico.atualizar(**campos)  # atômico: se algo for inválido, nada muda
        self._autosalvar()
        return servico

    def excluir(self, identificador):
        identificador = validar_id(identificador)
        removido = self.lista.remover(lambda s: s.id == identificador)
        if removido is None:
            raise NaoEncontradoError(f"Nenhum serviço encontrado com o ID {identificador}.")
        self._autosalvar()
        return removido

    # ------------------------------------------------ ORDENAÇÃO / ANÁLISE --
    def ordenar(self, criterio="id", decrescente=False):
        """Ordena a lista encadeada (Merge Sort próprio) e devolve os registros."""
        if criterio not in CHAVES_ORDENACAO:
            raise ValidacaoError("Critério de ordenação inválido (id, titulo ou categoria).")
        self.lista.ordenar(CHAVES_ORDENACAO[criterio], decrescente)
        self._autosalvar()
        return list(self.lista)

    def listar(self):
        return list(self.lista)

    def analise(self):
        contagem = {categoria: 0 for categoria in CATEGORIAS}
        for servico in self.lista:
            contagem[servico.categoria] += 1
        total = len(self.lista)
        percentual = {c: (100.0 * n / total if total else 0.0) for c, n in contagem.items()}
        maior = max(contagem.values())
        mais = [c for c, n in contagem.items() if n == maior] if total else []
        sem = [c for c, n in contagem.items() if n == 0]
        return {
            "total": total,
            "por_categoria": contagem,
            "percentual": percentual,
            "mais_servicos": mais,
            "sem_servicos": sem,
        }

    # ------------------------------------------------------ PERSISTÊNCIA --
    def salvar(self, arquivo=None):
        destino = arquivo or self.arquivo
        if destino is None:
            return
        dados = {"versao": 1, "servicos": [s.para_dict() for s in self.lista]}
        temporario = destino + ".tmp"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(temporario, destino)

    def carregar(self, arquivo=None):
        origem = arquivo or self.arquivo
        if origem is None:
            raise ArquivoInvalidoError("Nenhum arquivo configurado.")
        try:
            with open(origem, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except FileNotFoundError:
            raise ArquivoInvalidoError(f"Arquivo não encontrado: {origem}")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erro:
            raise ArquivoInvalidoError(f"Não foi possível ler {origem}: {erro}")
        if not isinstance(dados, dict) or not isinstance(dados.get("servicos"), list):
            raise ArquivoInvalidoError("Estrutura do arquivo inválida (esperado: {'servicos': [...]}).")
        nova = ListaEncadeada()
        for posicao, item in enumerate(dados["servicos"], start=1):
            try:
                servico = Servico.de_dict(item)
            except ValidacaoError as erro:
                raise ArquivoInvalidoError(f"Registro {posicao} inválido: {erro}")
            if busca_sequencial_por_id(nova, servico.id) is not None:
                raise ArquivoInvalidoError(f"ID duplicado no arquivo: {servico.id}")
            nova.inserir_fim(servico)
        self.lista = nova  # só substitui se o arquivo inteiro for válido

    def _autosalvar(self):
        if self.arquivo is not None:
            self.salvar()
