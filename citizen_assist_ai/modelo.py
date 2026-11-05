"""
modelo.py - Modelo de dados do Citizen Assist AI.

Define o registro `Servico`, as categorias aceitas, as exceções do sistema
e as funções de validação/normalização usadas por todo o projeto.
"""
import unicodedata

# Recorte escolhido pelo grupo: serviços públicos de uso cotidiano do cidadão.
CATEGORIAS = (
    "Saúde",
    "Assistência Social",
    "Documentação",
    "Educação",
    "Serviços Urbanos",
)

# campo -> (rótulo amigável, tamanho mínimo, tamanho máximo)
CAMPOS_TEXTO = {
    "titulo": ("Título", 3, 80),
    "descricao": ("Descrição", 5, 300),
    "requisitos": ("Requisitos", 2, 200),
    "local": ("Local de atendimento", 3, 100),
}


class ErroDoSistema(Exception):
    """Classe base das exceções controladas do sistema."""


class ValidacaoError(ErroDoSistema):
    """Entrada inválida (ID, texto vazio, categoria inexistente...)."""


class IdDuplicadoError(ErroDoSistema):
    """Tentativa de cadastrar um identificador que já existe."""


class NaoEncontradoError(ErroDoSistema):
    """Registro inexistente (consulta, atualização ou exclusão)."""


class ArquivoInvalidoError(ErroDoSistema):
    """Arquivo de persistência ausente, corrompido ou inconsistente."""


def normalizar(texto):
    """Minúsculas, sem acentos e sem espaços repetidos (para busca/ordenação)."""
    decomposto = unicodedata.normalize("NFD", str(texto))
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return " ".join(sem_acento.casefold().split())


def validar_id(valor):
    """Aceita int ou str numérica; retorna int > 0 ou levanta ValidacaoError."""
    mensagem = "O identificador deve ser um número inteiro positivo (ex.: 15)."
    if isinstance(valor, bool):
        raise ValidacaoError(mensagem)
    if isinstance(valor, str):
        texto = valor.strip()
        if not (texto.isascii() and texto.isdigit()):
            raise ValidacaoError(mensagem)
        valor = int(texto)
    if not isinstance(valor, int) or valor <= 0:
        raise ValidacaoError(mensagem)
    return valor


def validar_texto(campo, valor):
    """Valida um campo de texto livre conforme CAMPOS_TEXTO."""
    rotulo, minimo, maximo = CAMPOS_TEXTO[campo]
    if not isinstance(valor, str):
        raise ValidacaoError(f"{rotulo}: informe um texto.")
    limpo = " ".join(valor.split())
    if not limpo:
        raise ValidacaoError(f"{rotulo} não pode ficar em branco.")
    if len(limpo) < minimo:
        raise ValidacaoError(f"{rotulo} deve ter pelo menos {minimo} caracteres.")
    if len(limpo) > maximo:
        raise ValidacaoError(f"{rotulo} deve ter no máximo {maximo} caracteres.")
    return limpo


def validar_categoria(valor):
    """Retorna o nome canônico da categoria (ignora acento/caixa)."""
    if isinstance(valor, str):
        alvo = normalizar(valor)
        for categoria in CATEGORIAS:
            if normalizar(categoria) == alvo:
                return categoria
    raise ValidacaoError("Categoria inválida. Opções: " + ", ".join(CATEGORIAS) + ".")


def _validar_campo(campo, valor):
    if campo == "categoria":
        return validar_categoria(valor)
    if campo in CAMPOS_TEXTO:
        return validar_texto(campo, valor)
    raise ValidacaoError(f"Campo desconhecido: {campo}.")


class Servico:
    """Registro de um serviço/orientação ao cidadão."""

    __slots__ = ("id", "titulo", "categoria", "descricao", "requisitos", "local")
    CAMPOS_EDITAVEIS = ("titulo", "categoria", "descricao", "requisitos", "local")

    def __init__(self, id, titulo, categoria, descricao, requisitos, local):
        self.id = validar_id(id)
        self.titulo = validar_texto("titulo", titulo)
        self.categoria = validar_categoria(categoria)
        self.descricao = validar_texto("descricao", descricao)
        self.requisitos = validar_texto("requisitos", requisitos)
        self.local = validar_texto("local", local)

    def atualizar(self, **campos):
        """Atualiza campos de forma atômica: valida tudo antes de alterar algo."""
        novos = {}
        for campo, valor in campos.items():
            if campo not in self.CAMPOS_EDITAVEIS:
                raise ValidacaoError(f"O campo '{campo}' não pode ser atualizado.")
            novos[campo] = _validar_campo(campo, valor)
        for campo, valor in novos.items():
            setattr(self, campo, valor)

    def para_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "requisitos": self.requisitos,
            "local": self.local,
        }

    @classmethod
    def de_dict(cls, dados):
        if not isinstance(dados, dict):
            raise ValidacaoError("Registro em formato inválido.")
        try:
            return cls(
                dados["id"], dados["titulo"], dados["categoria"],
                dados["descricao"], dados["requisitos"], dados["local"],
            )
        except KeyError as erro:
            raise ValidacaoError(f"Campo ausente no registro: {erro.args[0]}.")

    def __repr__(self):
        return f"Servico(id={self.id}, titulo={self.titulo!r}, categoria={self.categoria!r})"
