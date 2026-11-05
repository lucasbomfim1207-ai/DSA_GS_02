"""
lista_encadeada.py - Lista simplesmente encadeada implementada pela equipe.

Estrutura:  cabeca -> [No|dado] -> [No|dado] -> ... -> [No|dado] -> None
                                                          ^ cauda

Mantemos um ponteiro para a cauda para que a inserção no fim seja O(1).
"""
from algoritmos import merge_sort_nos


class No:
    """Nó da lista: guarda um dado e a referência para o próximo nó."""

    __slots__ = ("dado", "proximo")

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self._tamanho = 0

    def __len__(self):
        return self._tamanho

    def esta_vazia(self):
        return self.cabeca is None

    def __iter__(self):
        """Percurso: visita os nós do início ao fim. O(n)."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def inserir_inicio(self, dado):
        """Insere no início. O(1)."""
        novo = No(dado)
        novo.proximo = self.cabeca
        self.cabeca = novo
        if self.cauda is None:
            self.cauda = novo
        self._tamanho += 1

    def inserir_fim(self, dado):
        """Insere no fim usando o ponteiro da cauda. O(1)."""
        novo = No(dado)
        if self.cabeca is None:
            self.cabeca = novo
        else:
            self.cauda.proximo = novo
        self.cauda = novo
        self._tamanho += 1

    def buscar(self, predicado):
        """Retorna o primeiro dado que satisfaz o predicado, ou None. O(n)."""
        for dado in self:
            if predicado(dado):
                return dado
        return None

    def remover(self, predicado):
        """
        Remove o primeiro nó cujo dado satisfaz o predicado e devolve o dado
        removido (ou None se nada for encontrado). O(n).
        Trata os casos: lista vazia, remoção da cabeça, do meio e da cauda.
        """
        anterior = None
        atual = self.cabeca
        while atual is not None:
            if predicado(atual.dado):
                if anterior is None:
                    self.cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if atual is self.cauda:
                    self.cauda = anterior
                removido = atual.dado
                atual.proximo = None
                self._tamanho -= 1
                return removido
            anterior = atual
            atual = atual.proximo
        return None

    def ordenar(self, chave, decrescente=False):
        """Ordena a própria lista com Merge Sort (religando nós). O(n log n)."""
        self.cabeca = merge_sort_nos(self.cabeca, chave, decrescente)
        self.cauda = self.cabeca
        while self.cauda is not None and self.cauda.proximo is not None:
            self.cauda = self.cauda.proximo

    def limpar(self):
        self.cabeca = None
        self.cauda = None
        self._tamanho = 0
