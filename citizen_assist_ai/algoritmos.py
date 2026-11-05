"""
algoritmos.py - Algoritmos de busca e ordenação implementados pela equipe.

* Busca sequencial por ID e busca sequencial por texto (título/categoria).
* Merge Sort sobre nós de lista encadeada (estável, sem copiar dados).
Nenhuma função pronta de ordenação (sorted/list.sort) é usada no sistema.
"""
from modelo import normalizar


# ----------------------------------------------------------------- BUSCA --
def busca_sequencial_por_id(lista, identificador):
    """Percorre a lista até achar o ID. Retorna o registro ou None. O(n)."""
    for servico in lista:
        if servico.id == identificador:
            return servico
    return None


def busca_por_texto(lista, campo, termo):
    """
    Busca sequencial por trecho de texto (sem diferenciar maiúsculas/acentos)
    em `campo` ('titulo' ou 'categoria'). Retorna uma lista de registros;
    lista vazia quando nada é encontrado. O(n * L), com L limitado (<= 80).
    """
    alvo = normalizar(termo)
    encontrados = []
    for servico in lista:
        if alvo in normalizar(getattr(servico, campo)):
            encontrados.append(servico)
    return encontrados


# ------------------------------------------------------------- ORDENAÇÃO --
def _dividir(cabeca):
    """Divide a lista ao meio (ponteiros lento/rápido). Retorna (esq, dir)."""
    lento = cabeca
    rapido = cabeca.proximo
    while rapido is not None and rapido.proximo is not None:
        lento = lento.proximo
        rapido = rapido.proximo.proximo
    direita = lento.proximo
    lento.proximo = None
    return cabeca, direita


def _intercalar(a, b, chave, decrescente):
    """Intercala duas listas ordenadas religando os nós. Estável. O(n)."""
    cabeca = None
    cauda = None
    while a is not None and b is not None:
        if decrescente:
            a_primeiro = chave(a.dado) >= chave(b.dado)
        else:
            a_primeiro = chave(a.dado) <= chave(b.dado)
        if a_primeiro:
            no = a
            a = a.proximo
        else:
            no = b
            b = b.proximo
        if cabeca is None:
            cabeca = no
        else:
            cauda.proximo = no
        cauda = no
    resto = a if a is not None else b
    if cabeca is None:
        return resto
    cauda.proximo = resto
    return cabeca


def merge_sort_nos(cabeca, chave, decrescente=False):
    """Merge Sort em lista encadeada. Retorna a nova cabeça. O(n log n)."""
    if cabeca is None or cabeca.proximo is None:
        return cabeca
    esquerda, direita = _dividir(cabeca)
    esquerda = merge_sort_nos(esquerda, chave, decrescente)
    direita = merge_sort_nos(direita, chave, decrescente)
    return _intercalar(esquerda, direita, chave, decrescente)
